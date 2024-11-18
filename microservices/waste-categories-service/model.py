from pydantic import BaseModel

class WasteCategoryRequest(BaseModel):
    name: str
    description: str
    guidelines: str

class WasteCategoryResponse(BaseModel):
    name: str
    description: str
    guidelines: str
