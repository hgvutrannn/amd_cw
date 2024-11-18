from pydantic import BaseModel, Field, validator
from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId

# Represents an ObjectId field in the database.
PyObjectId = Annotated[str, ObjectId]

class WasteItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., example="Plastic Bottle")
    category_id: PyObjectId = Field(..., example="5f8f8c44b54764421b7156c1")  # Reference to a waste category
    sorting_instructions: str = Field(..., example="Remove the cap, rinse, and place in recycling.")
    is_recyclable: bool = Field(..., example=True)
    disposal_method: Optional[str] = Field(None, example="Recycle")

    # Custom validator to convert ObjectId to string
    @validator('id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}  # Ensure ObjectId is serialized to a string
        json_schema_extra = {
            "example": {
                "name": "Plastic Bottle",
                "category_id": "6734c3274e2dcc1b2615fb1b",
                "sorting_instructions": "Remove the cap, rinse, and place in recycling.",
                "is_recyclable": True,
                "disposal_method": "Recycle",
            }
        }

    

class WasteItemCollection(BaseModel):
    items: List[WasteItemModel]
