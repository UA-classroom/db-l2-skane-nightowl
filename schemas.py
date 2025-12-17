from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ---------- USERS ----------

class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role_id: int
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    role_id: int
    is_active: bool

    class Config:
        from_attributes = True


# ---------- LISTINGS ----------

class ListingCreate(BaseModel):
    title: str
    description: str
    price: int
    living_area: int
    rooms: int
    category_id: int
    agent_id: int
    address_id: int


class ListingResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    status: str

    class Config:
        from_attributes = True


# ---------- BIDS ----------

class BidCreate(BaseModel):
    bidder_id: int
    amount: int = Field(gt=0)


class BidResponse(BaseModel):
    id: int
    listing_id: int
    bidder_id: int
    amount: int
    is_accepted: bool

    class Config:
        from_attributes = True


# ---------- FAVORITES ----------

class FavoriteCreate(BaseModel):
    user_id: int
    listing_id: int

# ---------- VIEWINGS ----------

class ViewingCreate(BaseModel):
    start_time: datetime
    end_time: datetime | None = None