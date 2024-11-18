from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
from model import ChallengeModel, ChallengeCollection, UpdateChallengeModel

app = FastAPI(
    title="Challenges API",
    summary="API for managing educational challenges related to waste sorting.",
)

MONGO_URL = "mongodb+srv://hoangvutrannn:77pCHwjv1OwdqKuh@cluster1.7plzt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["sorting-waste-app"]  # name of the database
challenges_collection = db.get_collection("Challenges")  # collection name

@app.post(
    "/challenges/",
    response_description="Add new challenge",
    response_model=ChallengeModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_challenge(challenge: ChallengeModel = Body(...)):
    new_challenge = await challenges_collection.insert_one(
        challenge.model_dump(by_alias=True, exclude=["id"])
    )
    created_challenge = await challenges_collection.find_one(
        {"_id": new_challenge.inserted_id}
    )
    return created_challenge

@app.get(
    "/challenges/",
    response_description="List all challenges",
    response_model=ChallengeCollection,
    response_model_by_alias=False,
)
async def list_challenges():
    return ChallengeCollection(challenges=await challenges_collection.find().to_list(1000))

@app.get(
    "/challenges/{id}",
    response_description="Get a single challenge",
    response_model=ChallengeModel,
    response_model_by_alias=False,
)
async def show_challenge(id: str):
    if (
        challenge := await challenges_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return challenge
    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")

@app.put(
    "/challenges/{id}",
    response_description="Update a challenge",
    response_model=ChallengeModel,
    response_model_by_alias=False,
)
async def update_challenge(id: str, challenge: UpdateChallengeModel = Body(...)):
    challenge_data = {
        k: v for k, v in challenge.model_dump(by_alias=True).items() if v is not None
    }
    if len(challenge_data) >= 1:
        update_result = await challenges_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": challenge_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Challenge {id} not found")
    if (existing_challenge := await challenges_collection.find_one({"_id": ObjectId(id)})) is not None:
        return existing_challenge
    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")

@app.delete("/challenges/{id}", response_description="Delete a challenge")
async def delete_challenge(id: str):
    delete_result = await challenges_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")
