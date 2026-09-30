from datetime import datetime

from pydantic import BaseModel


class AdminStats(BaseModel):
    total_users: int
    lost_items: int
    found_items: int
    pending_claims: int
    active_items: int
    returned_items: int
    pending_reports: int


class ActivityEntry(BaseModel):
    kind: str  # "report" | "claim"
    message: str
    item_id: int
    at: datetime
