from datetime import date, datetime
from datetime import time as dtime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CATEGORIES, LOCATIONS, ApprovalStatus, ItemStatus, ItemType, Visibility


class ItemBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    type: ItemType
    category: str
    brand: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=2000)
    location: str
    date: date
    time: dtime | None = None
    image_url: str | None = None
    private_details: str | None = Field(default=None, max_length=2000)
    visibility: Visibility = Visibility.PUBLIC

    @field_validator("title", "brand", "color", "description", "private_details", "image_url", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        return v

    @field_validator("location")
    @classmethod
    def valid_location(cls, v: str) -> str:
        if v not in LOCATIONS:
            raise ValueError(f"location must be one of {LOCATIONS}")
        return v

    @field_validator("date")
    @classmethod
    def not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date cannot be in the future")
        return v

    @field_validator("image_url")
    @classmethod
    def local_upload_only(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("/uploads/"):
            raise ValueError("image_url must reference an uploaded image")
        return v


class ItemCreate(ItemBase):
    pass


class ItemOut(BaseModel):
    """Public item representation. private_details is only populated for owner/admin."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: ItemType
    category: str
    brand: str | None
    color: str | None
    description: str | None
    location: str
    date: date
    time: dtime | None
    image_url: str | None
    private_details: str | None = None
    status: ItemStatus
    approval_status: ApprovalStatus
    visibility: Visibility
    reported_by: int
    reporter_name: str
    created_at: datetime
    updated_at: datetime


class TimelineStep(BaseModel):
    key: str
    label: str
    done: bool


class ItemDetail(ItemOut):
    timeline: list[TimelineStep]


class ItemList(BaseModel):
    items: list[ItemOut]
    total: int


class StatusUpdate(BaseModel):
    status: ItemStatus


class ApprovalUpdate(BaseModel):
    approval_status: ApprovalStatus


class MatchOut(BaseModel):
    match_score: int
    matching_attributes: list[str]
    explanation: str
    item: ItemOut
