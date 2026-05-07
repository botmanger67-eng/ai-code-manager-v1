from pydantic import BaseModel
from typing import Optional, List, Dict

class SessionOut(BaseModel):
    id: str
    name: str
    status: str
    created_at: str

class PlanFile(BaseModel):
    name: str
    description: str
    language: str

class PlanResponse(BaseModel):
    session_id: str
    plan: dict