"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
Features user authentication and SQLite persistence.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import os
from pathlib import Path

from database import init_db, seed_activities, get_activities, get_activity_by_name
from database import signup_for_activity, unregister_from_activity, create_user, get_user
from auth import hash_password, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserRegister, UserLogin, TokenResponse, SignupRequest, ActivityResponse

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities with authentication")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()
seed_activities()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Legacy in-memory activity database (for backward compatibility)
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


# ===== Authentication Endpoints =====

@app.post("/auth/register", response_model=TokenResponse)
def register(user: UserRegister):
    """Register a new user"""
    # Check if user already exists
    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    password_hash = hash_password(user.password)
    if not create_user(user.email, password_hash, user.full_name):
        raise HTTPException(status_code=400, detail="Failed to create user")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email, "role": "student"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(user: UserLogin):
    """Login user and return access token"""
    db_user = get_user(user.email)
    
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": db_user["email"], "role": db_user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": db_user["email"]
    }


# ===== Activity Endpoints =====

@app.get("/activities")
def get_activities_endpoint():
    """Get all activities with participant information"""
    activities_list = get_activities()
    return [ActivityResponse(**activity) for activity in activities_list]


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    """Get details for a specific activity"""
    activity = get_activity_by_name(activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityResponse(**activity)


@app.post("/activities/{activity_name}/signup")
def signup_for_activity_endpoint(
    activity_name: str,
    signup: SignupRequest,
    current_user: dict = Depends(verify_token)
):
    """Sign up authenticated user for an activity"""
    # Check if activity exists and has available spots
    activity = get_activity_by_name(activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if activity["participant_count"] >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    
    # Sign up for activity
    if not signup_for_activity(activity_name, signup.email):
        raise HTTPException(status_code=400, detail="Already signed up or invalid email")
    
    return {"message": f"Successfully signed up {signup.email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity_endpoint(
    activity_name: str,
    email: str,
    current_user: dict = Depends(verify_token)
):
    """Unregister from an activity (authenticated)"""
    if not unregister_from_activity(activity_name, email):
        raise HTTPException(status_code=400, detail="Not signed up for this activity")
    
    return {"message": f"Successfully unregistered {email} from {activity_name}"}
