from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from dataclasses import dataclass

class PredictRequest(BaseModel):
    """Input features for GDP shock prediction"""
    gdp_per_capita: float = Field(..., gt=0, description="GDP per capita (USD)")
    gov_expenditure: Optional[float] = None
    debt_service_pct: Optional[float] = None
    external_debt_pct: Optional[float] = None
    gni_per_capita_growth: Optional[float] = None
    unemployment: Optional[float] = Field(None, ge=0, le=100)
    fx_reserves_months: Optional[float] = Field(None, ge=0)
    current_account_pct: Optional[float] = None
    trade_openness: Optional[float] = Field(None, ge=0)
    inflation: Optional[float] = None
    fdi_inflows: Optional[float] = None
    region: str
    income_group: str
    lending_type: str
    is_crisis_decade: str

class PredictResponse(BaseModel):
    """Prediction response from model API"""
    prediction: Literal["choc", "normal"]
    probability: float
    threshold: float
    confidence: Literal["high", "medium", "low"]

class UserOut(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    date_of_birth: datetime

class RegisterReq(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    date_of_birth: datetime

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class ChatHistoryOut(BaseModel):
    id: int
    name: str
    input_type: str
    output_type: str
    input_file_url: Optional[str]
    output_file_url: Optional[str]
    created_at: datetime

@dataclass
class UserSession:
    """User session data"""
    user_id: int
    email: str
    firstname: str
    lastname: str
    is_authenticated: bool = False