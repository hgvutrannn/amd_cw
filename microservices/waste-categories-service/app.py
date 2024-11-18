from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient
from model import *
from jose import jwt, JWTError
from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer


client = MongoClient("mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")  
db = client["sorting-waste-app"]  
waste_category_collection = db.get_collection("WasteCategories")


app = FastAPI(
    title="Waste Categories API",
    summary="API for managing waste categories (e.g., organic, recyclable, hazardous)."
)

SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
        print(role)
        # Check if the role is admin
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        return email  # Optionally return email for further use
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# **1. Create Waste Category**
@app.post("/createca", response_model=WasteCategoryResponse, response_description="Create new Waste Category (Only Admin)")
async def create_waste_category(waste_category: WasteCategoryRequest, email: str=Depends(verify_admin_role)):
    # Check if waste category name already exists
    if waste_category_collection.find_one({"name": waste_category.name}):
        raise HTTPException(status_code=400, detail=f"Waste category name is already exists.")

    waste_category_data = {
        "name": waste_category.name,
        "description": waste_category.description,
        "guidelines": waste_category.guidelines
    }

    # Insert waste category into the database
    result = waste_category_collection.insert_one(waste_category_data)
    created_waste_category = waste_category_collection.find_one({"_id": result.inserted_id})
    return WasteCategoryResponse(id=str(created_waste_category["_id"]), name=created_waste_category["name"], description=created_waste_category["description"], guidelines=created_waste_category["guidelines"])

# **2. Get All Waste Categories**
@app.get("/getallca", response_model=List[WasteCategoryResponse])
async def get_all_waste_categories():
    categories = waste_category_collection.find()
    result = [
        WasteCategoryResponse(
            id=str(category["_id"]),
            name=category["name"],
            description=category["description"],
            guidelines=category["guidelines"]
        ) for category in categories
    ]
    return result

# **3. Update a Waste Category by Name**
@app.put("/updateca", response_model=WasteCategoryResponse, response_description="Update new Waste Category (Only Admin)")
async def update_waste_category(waste_category_update: WasteCategoryRequest, email: str=Depends(verify_admin_role)):
    # Check if the waste category exists
    existing_category = waste_category_collection.find_one({"name": waste_category_update.name})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Waste category not found.")

    # Prepare the update data
    update_data = {}
    if waste_category_update.description:
        update_data["description"] = waste_category_update.description
    if waste_category_update.guidelines:
        update_data["guidelines"] = waste_category_update.guidelines

    # Perform the update
    updated_category = waste_category_collection.find_one_and_update(
        {"name": waste_category_update.name},
        {"$set": update_data},  # Use $set to update fields
        return_document=True  # Return the updated document
    )

    if not updated_category:
        raise HTTPException(status_code=404, detail="Failed to update the waste category.")

    # Return the updated category
    return WasteCategoryResponse(
        id=str(updated_category["_id"]),
        name=updated_category["name"],
        description=updated_category["description"],
        guidelines=updated_category["guidelines"]
    )

# **4. Delete a Waste Category by Name**
@app.delete("/deleteca", response_model=dict, response_description="Delete new Waste Category (Only Admin)")
async def delete_waste_category(name: str, email: str=Depends(verify_admin_role)):
    # Delete the waste category
    result = waste_category_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Waste category not found.")
    return {"message": f"Waste category '{name}' deleted successfully."}