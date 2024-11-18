from pydantic import BaseModel, EmailStr, Field, root_validator
from typing import Optional

# Request models
class UserValidationBase(BaseModel):
    @root_validator(pre=True)
    def validate_username(cls, values):
        username = values.get('username')
        if username:
            # Check if username is blank (empty string)
            if not username.strip():
                raise ValueError('Username cannot be blank')

            # Check if username is fully numeric
            if username.isdigit():
                raise ValueError('Username cannot be fully numeric')

        return values
    
    @root_validator(pre=True)
    def validate_password(cls, values):
        password = values.get('password')
        if password:
            # Password must contain at least one uppercase letter
            if not any(c.isupper() for c in password):
                raise ValueError('Password must contain at least one uppercase letter')
            
            # Password must contain at least one special character
            if not any(c in '!@#$%^&*()-_=+[{]}\\|;:\'",<.>/?' for c in password):
                raise ValueError('Password must contain at least one special character')

        return values
    
class UserRequest(UserValidationBase):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)  # Password length must be at least 8 characters

class UserLogin(UserValidationBase):
    email: EmailStr
    password: str = Field(...,min_length=8)

# class UserProfileUpdate(UserValidationBase):
#     username: str  # Made optional for updates
#     email: EmailStr  # Made optional for updates
#     password: Optional[str] = Field(None, min_length=8)  # Made optional for updates

class DeleteUserRequest(UserValidationBase):
    password: str = Field(...,min_length=8)


# Response model
class UserResponse(BaseModel):
    username: str
    email: EmailStr
    score: int

