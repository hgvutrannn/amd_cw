from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId

# Represents an ObjectId field in the database.
PyObjectId = Annotated[str, BeforeValidator(str)]

class ChallengeModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    description: str = Field(...)
    difficulty: int = Field(..., ge=1, le=5)
    steps: List[str] = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Recycling Basics",
                "description": "Learn the basics of recycling and waste sorting.",
                "difficulty": 3,
                "steps": ["Collect recyclable items", "Sort them by material", "Dispose of them in the appropriate bins"],
            }
        },
    )

class UpdateChallengeModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    steps: Optional[List[str]] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "Recycling Basics",
                "description": "Learn the basics of recycling and waste sorting.",
                "difficulty": 3,
                "steps": ["Collect recyclable items", "Sort them by material", "Dispose of them in the appropriate bins"],
            }
        },
    )

class ChallengeCollection(BaseModel):
    challenges: List[ChallengeModel]
