from pydantic import BaseModel, Field

class ChallengeRequest(BaseModel):  # Validates request data
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=200)
    guidelines: str = Field(..., min_length=5)

class ChallengeResponse(BaseModel):
    name: str
    description: str
    guidelines: str
