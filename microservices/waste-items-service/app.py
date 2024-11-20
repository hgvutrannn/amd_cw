from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
from model import *
from jose import jwt, JWTError
from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer

# MongoDB connection and collection setup
client = MongoClient("mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client["sorting-waste-app"]
waste_item_collection = db.get_collection("WasteItems")

# JWT configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # save authorization token here

app = FastAPI(
    title="Waste Items API",
    summary="API for managing individual waste items and their sorting information."
)

# Verify admin role using the token
async def verify_admin_role(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        exp = payload.get("exp")

        if not email or not role or not exp:
            raise HTTPException(status_code=401, detail="Invalid token")

        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token has expired")

        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")

        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# **1. Create Waste Item**
@app.post(
    "/create-item/",
    response_description="Add new waste item",
    response_model=WasteItemResponse,
)
async def create_waste_item(
    waste_item: WasteItemRequest,
    email: str = Depends(verify_admin_role)
):
    # Check if waste item already exists
    if waste_item_collection.find_one({"name": waste_item.name}):
        raise HTTPException(status_code=400, detail=f"Waste item is already exists.")
    
    waste_item_data = {
        "name": waste_item.name,
        "sorting_information": waste_item.sorting_information
    }

    # Insert waste item into the database
    result = waste_item_collection.insert_one(waste_item_data)
    created_item = waste_item_collection.find_one({"_id": result.inserted_id})
    return WasteItemResponse(id=str(created_item["_id"]), name=created_item["name"], sorting_information=created_item["sorting_information"])

# **2. Get All Waste Items**
@app.get(
    "/getall-item/",
    response_description="List all waste items",
    response_model=List[WasteItemResponse]
)
async def list_waste_items():
    items = waste_item_collection.find()
    result = [
        WasteItemResponse(
            name=item["name"],
            sorting_information=item.get("sorting_information", "No sorting info available")
        ) for item in items
    ]
    return result

# **3. Update a Waste Category by Name**
@app.put(
    "/update-item/",
    response_description="Update a waste item",
    response_model=WasteItemResponse
)
async def update_waste_item(
    waste_item_update: WasteItemRequest,
    email: str = Depends(verify_admin_role)
):
    # Check if the waste item exists
    existing_item = waste_item_collection.find_one({"name": waste_item_update.name})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Waste item not found.")

    update_data = {}
    if waste_item_update.sorting_information:
        update_data["sorting_information"] = waste_item_update.sorting_information

    # Perform the update
    updated_item = waste_item_collection.find_one_and_update(
        {"name": waste_item_update.name},
        {"$set": update_data},  # Use $set to update fields
        return_document=True  # Return the updated document
    )

    if not updated_item:
        raise HTTPException(status_code=404, detail="Waste item not found.")
    
    return WasteItemResponse(
        id=str(updated_item["_id"]),
        name=updated_item["name"],
        sorting_information=updated_item["sorting_information"]
    )

# **4. Delete a Waste Category by Name**
@app.delete("/delete-item/", response_model=dict, response_description="Delete a waste item")
async def delete_waste_item(name: str, email: str = Depends(verify_admin_role)):
    delete_result = waste_item_collection.delete_one({"name": name})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Waste item not found.")
    return {"message": f"Waste item '{name}' deleted successfully."}