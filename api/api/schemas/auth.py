from pydantic import BaseModel


class LoginCredentials(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    verification_code: int


class AuthResponse(BaseModel):
    player_id: int
    session_key: str
