from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.items import serialize
from app.db.session import get_db
from app.models import Claim, Item, User
from app.models.enums import ApprovalStatus, ClaimStatus, ItemStatus, ItemType
from app.schemas.admin import ActivityEntry, AdminStats
from app.schemas.item import ItemOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _count(db: Session, *where) -> int:
    return db.scalar(select(func.count()).select_from(Item).where(*where)) or 0


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db)):
    rejected = Item.approval_status != ApprovalStatus.REJECTED.value
    return AdminStats(
        total_users=db.scalar(select(func.count()).select_from(User)) or 0,
        lost_items=_count(db, Item.type == ItemType.LOST.value, rejected),
        found_items=_count(db, Item.type == ItemType.FOUND.value, rejected),
        pending_claims=db.scalar(
            select(func.count()).select_from(Claim).where(Claim.status == ClaimStatus.PENDING.value)
        ) or 0,
        active_items=_count(db, Item.status == ItemStatus.ACTIVE.value, rejected),
        returned_items=_count(db, Item.status == ItemStatus.RETURNED.value),
        pending_reports=_count(db, Item.approval_status == ApprovalStatus.PENDING.value),
    )


@router.get("/pending-items", response_model=list[ItemOut])
def pending_items(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(
        select(Item).where(Item.approval_status == ApprovalStatus.PENDING.value)
        .order_by(Item.created_at.desc(), Item.id.desc())
    ).unique().all()
    return [serialize(i, admin) for i in rows]


@router.get("/activity", response_model=list[ActivityEntry])
def activity(db: Session = Depends(get_db)):
    entries: list[ActivityEntry] = []
    for i in db.scalars(select(Item).order_by(Item.created_at.desc()).limit(10)).unique():
        entries.append(ActivityEntry(
            kind="report", item_id=i.id, at=i.created_at,
            message=f"{i.reporter_name} reported a {i.type.lower()} item: {i.title}",
        ))
    for c in db.scalars(select(Claim).order_by(Claim.updated_at.desc()).limit(10)).unique():
        verb = {"PENDING": "submitted a claim for", "APPROVED": "had a claim approved for",
                "REJECTED": "had a claim rejected for", "COMPLETED": "received"}[c.status]
        entries.append(ActivityEntry(
            kind="claim", item_id=c.item_id, at=c.updated_at,
            message=f"{c.claimant.full_name} {verb} {c.item.title}",
        ))
    entries.sort(key=lambda e: e.at, reverse=True)
    return entries[:10]
