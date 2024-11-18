from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pymongo import ReturnDocument

from bson import ObjectId
import motor.motor_asyncio
from model import WasteItemModel, WasteItemCollection

# MongoDB connection and collection setup
MONGO_URL = "mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["sorting-waste-app"]
waste_item_collection = db.get_collection("WasteItems")

app = FastAPI(
    title="Waste Items API",
    summary="API for managing individual waste items and their sorting information."
)

# Waste item endpoints
@app.post(
    "/waste-items/",
    response_description="Add new waste item",
    response_model=WasteItemModel,
    status_code=status.HTTP_201_CREATED
)
async def create_waste_item(item: WasteItemModel = Body(...)):
    new_item = await waste_item_collection.insert_one(item.dict(by_alias=True, exclude=["id"]))
    created_item = await waste_item_collection.find_one({"_id": new_item.inserted_id})
    return created_item


@app.get(
    "/waste-items/",
    response_description="List all waste items",
    response_model=WasteItemCollection
)
async def list_waste_items():
    items = await waste_item_collection.find().to_list(1000)
    return WasteItemCollection(items=items)


@app.get(
    "/waste-items/{id}",
    response_description="Get a single waste item",
    response_model=WasteItemModel
)
async def show_waste_item(id: str):
    if (item := await waste_item_collection.find_one({"_id": ObjectId(id)})) is not None:
        return item
    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")


@app.put(
    "/waste-items/{id}",
    response_description="Update a waste item",
    response_model=WasteItemModel
)
async def update_waste_item(id: str, item: WasteItemModel = Body(...)):
    updated_data = {k: v for k, v in item.dict(by_alias=True).items() if v is not None}
    
    if len(updated_data) >= 1:
        updated_item = await waste_item_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": updated_data},
            return_document=ReturnDocument.AFTER
        )
        if updated_item is not None:
            return updated_item

    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")


@app.delete("/waste-items/{id}", response_description="Delete a waste item")
async def delete_waste_item(id: str):
    delete_result = await waste_item_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")
