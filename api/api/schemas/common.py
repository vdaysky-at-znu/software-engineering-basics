from typing import Dict, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    message: str
    payload: Optional[Dict] = None
