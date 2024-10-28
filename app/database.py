from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new registry
REGISTRY = CollectorRegistry()

# Metrics with unique names
API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Total API HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

API_REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API HTTP request duration',
    ['method', 'endpoint'],
    registry=REGISTRY
)

API_ACTIVE_REQUESTS = Gauge(
    'api_active_requests',
    'Number of active API requests',
    registry=REGISTRY
)

APP_CPU_USAGE = Gauge(
    'api_cpu_usage_percent',
    'API application CPU usage percentage',
    registry=REGISTRY
)

# Database setup with retry logic
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres-service:5432/products") # the default value to use if the environment variable is not found

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            engine.connect()
            logger.info("Successfully connected to the database")
            return engine
        except Exception as e:
            retries -= 1
            if retries == 0:
                logger.error(f"Failed to connect to database after 5 attempts: {e}")
                raise e
            logger.warning(f"Failed to connect to database. Retrying... ({retries} attempts left)")
            time.sleep(5)

# Initialize database engine and session
engine = get_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise e

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()