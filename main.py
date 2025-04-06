import logging
import crud
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User, TransportOption, get_accommodations  
from schemas import UserCreate, UserResponse, TransportOptionCreate, TransportOptionResponse, AccommodationCreate, AccommodationResponse
from crud import create_user, authenticate_user
from google_places import get_nearby_housing, geocode_location, get_transport_routes
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("VISTOPIA: MAIN.PY IS RUNNING")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)

@app.post("/signup/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = create_user(db, user.username, user.password)
    return new_user

@app.post("/login/")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful", "username": db_user.username}

class TransportRequest(BaseModel):
    origin: str
    destination: str

# Modify the search_transport endpoint
@app.post("/search_transport/", response_model=list[TransportOptionResponse])
def search_transport(payload: TransportRequest):
    all_modes = ["driving", "transit", "walking", "bicycling"]
    all_options = []
    
    for mode in all_modes:
        routes = get_transport_routes(payload.origin, payload.destination, mode)
        for route in routes:
            all_options.append({
                "origin": payload.origin,
                "destination": payload.destination,
                "transport_type": mode,
                "mode": mode,
                "price": route["price"],
                "duration": route["duration"],
                "distance": route["distance"]
            })
    
    if not all_options:
        raise HTTPException(status_code=404, detail="No routes found")
    
    return [{"id": idx, **opt} for idx, opt in enumerate(all_options)]



class AccommodationRequest(BaseModel):
    location: str
    budget: float

# Update the imports
from google_places import get_nearby_housing, geocode_location

@app.post("/search_accommodation/", response_model=list[AccommodationResponse])
def search_accommodation(payload: AccommodationRequest):
    # Geocode the location to get coordinates
    lat_lng = geocode_location(payload.location)
    if not lat_lng:
        raise HTTPException(status_code=400, detail="Invalid location")
    lat, lng = lat_lng
    
    # Fetch nearby housing from Google Places API
    places = get_nearby_housing(lat, lng)
    print("Total places fetched:", len(places))  # DEBUG

    # Print all names and their prices
    for place in places:
        print(f"{place['name']} - price: {place.get('price')}")  # DEBUG

    if not places:
        raise HTTPException(status_code=404, detail="No accommodations found")
    
    # Filter by price_level (budget)
    filtered = places
    print("Filtered (within budget) places:", len(filtered))  # DEBUG
    
    # Map to AccommodationResponse schema
    results = []
    for place in filtered:
        results.append({
            "id": place["place_id"],
            "name": place["name"],
            "location": place["address"],
            "price": place.get("price") or 0, 
            "rating": place.get("rating")
        })
    return results


@app.post("/transport_options/", response_model=TransportOptionResponse)
def create_transport_option(
    transport: TransportOptionCreate, 
    db: Session = Depends(get_db)
):
    return crud.create_transport_option(db, transport)

# Force execution only when running directly
if __name__ == "__main__":
    for route in app.routes:
        logger.info(f"Registered route: {route.path}")

from database import engine, Base

Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")