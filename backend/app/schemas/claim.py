from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ClaimStatus, ItemStatus, ItemType


class ClaimCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
    lost_location: str = Field(min_length=2, max_length=120)
    verification_answer: str = Field(min_length=3, max_length=1000)

    @field_validator("reason", "lost_location", "verification_answer")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    review_comment: str | None = Field(default=None, max_length=1000)


class ClaimItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: ItemType
    status: ItemStatus
    location: str
    image_url: str | None
    private_details: str | None = None  # admin only


class ClaimClaimant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    claimant_id: int
    reason: str
    lost_location: str | None
    verification_answer: str
    status: ClaimStatus
    review_comment: str | None
    created_at: datetime
    updated_at: datetime
    item: ClaimItem
    claimant: ClaimClaimant
