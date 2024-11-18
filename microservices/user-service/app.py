from fastapi import HTTPException, Depends, FastAPI
from jose import jwt, JWTError
from passlib.context import CryptContext
from models import *
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection setup
client = MongoClient("mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")  
db = client["sorting-waste-app"]  
users_collection = db["users"]

app = FastAPI(
    title="Waste Categories API",
    summary="API for managing user using JWT for authentication."
)

# Cryptography setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"  # Replace with a strong secret key
ALGORITHM = "HS256"


# Global variable to store the JWT token
global_jwt_token = None

# Helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# update to check expiration time
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user():
    try:
        payload = jwt.decode(global_jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db_user = users_collection.find_one({"email": user_email})
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# Routes
@app.post("/register", response_model=UserResponse)
async def register_user(user: UserRequest):
    # Check if email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "role": "user",
        "score": 0
    }

    # Insert user into the database
    result = users_collection.insert_one(user_data)
    created_user = users_collection.find_one({"_id": result.inserted_id})
    return UserResponse(id=str(created_user["_id"]), username=created_user["username"], email=created_user["email"], score=created_user["score"])

@app.post("/login")
async def login_user(user: UserLogin):
    global global_jwt_token

    # Find user by email
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token({
        "sub": str(db_user["email"]), 
        "role": db_user["role"] 
    }, expires_delta= timedelta(minutes=15))

    global_jwt_token = access_token
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"],
        score=current_user["score"]
    )

@app.put("/updateme", response_model=UserResponse)
async def update_user_profile(
    update_data: UserRequest,
    current_user: dict = Depends(get_current_user)
):
    global global_jwt_token
    # Prepare fields to update
    update_dict = {}

    # Update username 
    if update_data.username:
        update_dict["username"] = update_data.username

    # Update email 
    if update_data.email:
        if update_data.email != current_user["email"]:  # Check if it's a different email
            # Check if the new email already exists in the database
            existing_email = users_collection.find_one({"email": update_data.email})
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already in use")
            
            # Create JWT token because email is changed
            access_token = create_access_token({
                "sub": update_data.email, 
                "role": current_user["role"]
            }, expires_delta= timedelta(minutes=15))

            global_jwt_token = access_token
        update_dict["email"] = update_data.email

    # Update password 
    if update_data.password:
        update_dict["password"] = hash_password(update_data.password)

    # Update the user in the database
    if update_dict:
        users_collection.update_one({"_id": current_user["_id"]}, {"$set": update_dict})

    # Fetch the updated user
    updated_user = users_collection.find_one({"_id": current_user["_id"]})

    return UserResponse(
        username=updated_user["username"],
        email=updated_user["email"],
        score=updated_user["score"]
    )

@app.delete("/deleteme", response_model=dict)
async def delete_user_profile(
    delete_request: DeleteUserRequest,
    current_user: dict = Depends(get_current_user)
):
    print("Delete request received for user:", current_user["email"])  # Debugging

    # Verify the user's password
    if not verify_password(delete_request.password, current_user["password"]):
        print("Password verification failed")  # Debugging
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Attempt to delete the user
    result = users_collection.delete_one({"email": current_user["email"]})
    if result.deleted_count == 0:
        print("User not found or could not be deleted")  # Debugging
        raise HTTPException(status_code=404, detail="User not found or could not be deleted")

    return {"message": "User deleted successfully"}
