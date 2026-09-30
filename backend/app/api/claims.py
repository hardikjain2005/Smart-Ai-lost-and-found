from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, is_admin, require_admin
from app.api.items import ensure_access
from app.db.session import get_db
from app.models import Claim, Item, User
from app.models.enums import ApprovalStatus, ClaimStatus, ItemStatus, ItemType
from app.schemas.claim import ClaimCreate, ClaimOut, ClaimStatusUpdate
from app.services import workflow

router = APIRouter(tags=["claims"])


def serialize(claim: Claim, viewer: User) -> ClaimOut:
    out = ClaimOut.model_validate(claim)
    # the found item's private details are for the admin's verification only
    out.item.private_details = claim.item.private_details if is_admin(viewer) else None
    return out


@router.post("/items/{item_id}/claim", response_model=ClaimOut, status_code=status.HTTP_201_CREATED)
def submit_claim(item_id: int, body: ClaimCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item or item.approval_status == ApprovalStatus.REJECTED.value:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    ensure_access(item, user)
    if item.type != ItemType.FOUND.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only found items can be claimed")
    if item.reported_by == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot claim an item you reported")
    if item.status not in (ItemStatus.ACTIVE.value, ItemStatus.MATCHED.value):
        raise HTTPException(status.HTTP_409_CONFLICT, "This item can no longer be claimed")
    if any(c.claimant_id == user.id and c.status in (ClaimStatus.PENDING.value, ClaimStatus.APPROVED.value) for c in item.claims):
        raise HTTPException(status.HTTP_409_CONFLICT, "You already have an open claim for this item")
    claim = Claim(item=item, claimant=user, **body.model_dump())
    workflow.submit_claim(db, item, claim)
    db.commit()
    db.refresh(claim)
    return serialize(claim, user)


@router.get("/claims", response_model=list[ClaimOut])
def list_claims(
    status_: ClaimStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    stmt = select(Claim)
    if not is_admin(user):
        stmt = stmt.where(Claim.claimant_id == user.id)
    if status_:
        stmt = stmt.where(Claim.status == status_.value)
    rows = db.scalars(stmt.order_by(Claim.created_at.desc(), Claim.id.desc())).unique().all()
    return [serialize(c, user) for c in rows]


@router.get("/claims/{claim_id}", response_model=ClaimOut)
def get_claim(claim_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    claim = db.get(Claim, claim_id)
    if not claim or not (is_admin(user) or claim.claimant_id == user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    return serialize(claim, user)


@router.patch("/claims/{claim_id}/status", response_model=ClaimOut)
def update_claim_status(claim_id: int, body: ClaimStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    current, new = ClaimStatus(claim.status), body.status
    allowed = {
        ClaimStatus.PENDING: {ClaimStatus.APPROVED, ClaimStatus.REJECTED},
        ClaimStatus.APPROVED: {ClaimStatus.COMPLETED},
    }
    if new not in allowed.get(current, set()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot change claim from {current.value} to {new.value}")
    if new == ClaimStatus.APPROVED:
        workflow.approve_claim(db, claim, body.review_comment)
    elif new == ClaimStatus.REJECTED:
        workflow.reject_claim(db, claim, body.review_comment)
    else:
        workflow.complete_item(db, claim.item, body.review_comment)
    db.commit()
    db.refresh(claim)
    return serialize(claim, admin)
