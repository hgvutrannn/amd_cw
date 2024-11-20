from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient
from model import *
from jose import jwt, JWTError
from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="Challenges API",
    summary="API for managing educational challenges related to waste sorting.",
)

client = MongoClient("mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")   
db = client["sorting-waste-app"]  # name of the database
challenges_collection = db.get_collection("Challenges")  # collection name

SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # save authorization token here

async def verify_admin_role(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        exp = payload.get("exp")

        # Check if required fields exist
        if not email or not role or not exp:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if the token is expired
        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token has expired")

        # Check if the role is admin
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")

        return email  # Optionally return email for further use
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/createchallenges",response_model=ChallengeResponse,response_description="Add new challenge",)
async def create_challenge(challenge: ChallengeRequest, email: str = Depends(verify_admin_role)):
    if challenges_collection.find_one({"name": challenge.name}):
            raise HTTPException(status_code=400, detail=f"Challenge name is already exists.")
    challenge_data = {
            "name": challenge.name,
            "description": challenge.description,
            "guidelines": challenge.guidelines
        }
    # Insert challenge into the database
    result = challenges_collection.insert_one(challenge_data)
    created_challenge = challenges_collection.find_one({"_id": result.inserted_id})
    return ChallengeResponse(id=str(created_challenge["_id"]), name=created_challenge["name"], description=created_challenge["description"], guidelines=created_challenge["guidelines"])


@app.get("/getallchallenges",response_description="List all challenges",response_model=List[ChallengeResponse])
async def get_all_challenges():
    categories = challenges_collection.find()
    result = [
        ChallengeResponse(
            id=str(category["_id"]),
            name=category["name"],
            description=category["description"],
            guidelines=category["guidelines"]
        ) for category in categories
    ]
    return result

@app.put("/updatechallenges", response_model=ChallengeResponse, response_description="Update new Challenges (Only Admin)")
async def update_challenge(challenge_update: ChallengeRequest, email: str=Depends(verify_admin_role)):
    # Check if the challenge exists
    existing_category = challenges_collection.find_one({"name": challenge_update.name})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    # Prepare the update data
    update_data = {}
    if challenge_update.description:
        update_data["description"] = challenge_update.description
    if challenge_update.guidelines:
        update_data["guidelines"] = challenge_update.guidelines

    # Perform the update
    updated_category = challenges_collection.find_one_and_update(
        {"name": challenge_update.name},
        {"$set": update_data},  # Use $set to update fields
        return_document=True  # Return the updated document
    )

    if not updated_category:
        raise HTTPException(status_code=404, detail="Failed to update the challenge.")

    # Return the updated category
    return ChallengeResponse(
        id=str(updated_category["_id"]),
        name=updated_category["name"],
        description=updated_category["description"],
        guidelines=updated_category["guidelines"]
    )

# **4. Delete a Challenge by Name**
@app.delete("/deletechallenges", response_model=dict, response_description="Delete Challenge (Only Admin)")
async def delete_challenge(name: str, email: str=Depends(verify_admin_role)):
    # Delete the Challenge
    result = challenges_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    return {"message": f"Challenge '{name}' deleted successfully."}
