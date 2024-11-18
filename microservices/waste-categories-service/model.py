from pydantic import BaseModel, Field

class WasteCategoryRequest(BaseModel):  # Validates request data
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=200)
    guidelines: str = Field(..., min_length=5)

class WasteCategoryResponse(BaseModel):
    name: str
    description: str
    guidelines: str
