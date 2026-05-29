from __future__ import annotations
from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator




class RegisterReq(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    date_of_birth: date

    model_config = {"json_schema_extra": {"example": {
        "firstname": "Jon",
        "lastname": "Doe",
        "email": "jon@doe.com",
        "password": "securepass",
        "date_of_birth": "1990-01-15"
    }}}


class LoginReq(BaseModel):
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {"example": {
        "email": "jon@doe.com",
        "password": "securepass"
    }}}


class UserOut(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    date_of_birth: date

    model_config = {"from_attributes": True}




class PredictRequest(BaseModel):
    """
    Input features for GDP shock prediction.
    All numeric features from the preprocessing pipeline.
    """
    gdp_per_capita: float = Field(..., gt=0, description="GDP per capita (USD)")
    gov_expenditure: Optional[float] = Field(None, description="Government expenditure (% of GDP)")
    debt_service_pct: Optional[float] = Field(None, description="Debt service (% of GNI)")
    external_debt_pct: Optional[float] = Field(None, description="External debt stocks (% of GNI)")
    gni_per_capita_growth: Optional[float] = Field(None, description="GNI per capita growth (annual %)")
    unemployment: Optional[float] = Field(None, ge=0, le=100, description="Unemployment rate (%)")
    fx_reserves_months: Optional[float] = Field(None, ge=0, description="FX reserves (months of imports)")
    current_account_pct: Optional[float] = Field(None, description="Current account balance (% of GDP)")
    trade_openness: Optional[float] = Field(None, ge=0, description="Trade openness (% of GDP)")
    inflation: Optional[float] = Field(None, description="Inflation, consumer prices (annual %)")
    fdi_inflows: Optional[float] = Field(None, description="FDI inflows (% of GDP)")
    region: str = Field(..., description="World Bank region code")
    income_group: str = Field(..., description="World Bank income group")
    lending_type: str = Field(..., description="World Bank lending type")
    is_crisis_decade: str = Field(..., description="Decade label, e.g. '2000s'")

    model_config = {"json_schema_extra": {"example": {
        "gdp_per_capita": 3200.0,
        "gov_expenditure": 18.5,
        "debt_service_pct": 12.0,
        "external_debt_pct": 55.0,
        "gni_per_capita_growth": -2.1,
        "unemployment": 14.5,
        "fx_reserves_months": 2.1,
        "current_account_pct": -6.5,
        "trade_openness": 72.0,
        "inflation": 8.3,
        "fdi_inflows": 1.2,
        "region": "Middle East & North Africa",
        "income_group": "Lower middle income",
        "lending_type": "IBRD",
        "is_crisis_decade": "2010s"
    }}}


class PredictResponse(BaseModel):
    prediction: Literal["choc", "normal"]
    probability: float = Field(..., ge=0.0, le=1.0)
    threshold: float
    confidence: Literal["high", "medium", "low"]




class ChatHistoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    input_type: Literal["single", "csv"] = "single"
    input_data: Optional[str] = None
    input_file_url: Optional[str] = None
    output_type: Literal["single", "csv"] = "single"
    output_data: Optional[str] = None
    output_file_url: Optional[str] = None


class ChatHistoryOut(BaseModel):
    id: int
    name: str
    input_type: str
    output_type: str
    input_file_url: Optional[str]
    output_file_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}