from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List
import time
import logging
import psutil
from prometheus_client import generate_latest
from .models import Product, ProductCreate, ProductResponse
from .database import get_db, REGISTRY, API_REQUESTS_TOTAL, API_REQUEST_DURATION, API_ACTIVE_REQUESTS, APP_CPU_USAGE, Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting up FastAPI application")
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    API_ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        logger.error(f"Request error: {str(e)}")
        raise e
    finally:
        duration = time.time() - start_time
        API_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status_code
        ).inc()
        
        API_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        API_ACTIVE_REQUESTS.dec()
        
        # Update CPU usage metric
        APP_CPU_USAGE.set(psutil.Process().cpu_percent())
    
    return response

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest(REGISTRY).decode("utf-8"))

@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Created product: {db_product.name}")
        return ProductResponse(**db_product.to_dict())
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/", response_model=List[ProductResponse])
def read_products(db: Session = Depends(get_db)):
    try:
        products = db.query(Product).all()
        logger.info(f"Retrieved {len(products)} products")
        return [ProductResponse(**product.to_dict()) for product in products]
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            logger.warning(f"Product not found: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"Retrieved product: {product.name}")
        return ProductResponse(**product.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))