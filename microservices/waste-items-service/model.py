from pydantic import BaseModel, Field

class WasteItemRequest(BaseModel):  # Validates request data
    name: str = Field(..., min_length=3, max_length=50)
    sorting_information: str = Field(..., max_length=200)

class WasteItemResponse(BaseModel):
    name: str
    sorting_information: str