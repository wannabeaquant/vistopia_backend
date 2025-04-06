from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class ListingResponse(BaseModel):
    name: str
    address: str | None  
    latitude: float
    longitude: float
    rating: float | None
    total_reviews: int | None
    price: int | None
    amenities: list | None

    class Config:
        from_attributes = True
    
class AccommodationCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    price: float | None = None
    amenities: str | None = None

class AccommodationRequest(BaseModel):
    location: str
    budget: int

class TransportOptionCreate(BaseModel):
    origin: str
    destination: str
    transport_type: str
    mode: str
    price: float | None = None
    duration: str | None = None
    distance: float | None = None

class TransportOptionResponse(BaseModel):
    id: int
    origin: str
    destination: str
    transport_type: str
    mode: str
    price: float | None
    duration: str | None
    distance: float | None

    class Config:
        from_attributes = True

class AccommodationResponse(BaseModel):
    id: str
    name: str
    location: str
    price: int
    rating: Optional[float]