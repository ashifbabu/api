from pydantic import BaseModel

class AuthRequest(BaseModel):
    username: str
    apikey: str

class AuthResponse(BaseModel):
    FirstName: str
    LastName: str
    Email: str
    TokenId: str
    Status: int
    Error: str = None