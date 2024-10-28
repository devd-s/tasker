from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from .database import Base

class Product(Base):
    __tablename__ = "products"    # Fixed: Added double underscores

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock
        }

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    class Config:
        orm_mode = True  # Added for better Pydantic-SQLAlchemy integration