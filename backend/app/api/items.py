from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from campusfind_ml.matching import ItemFeatures, find_matches

from app.api.deps import get_current_user, get_optional_user, is_admin, require_admin
from app.db.session import get_db
from app.models import Claim, Item, User
from app.models.enums import (
    CATEGORIES, LOCATIONS, ApprovalStatus, ClaimStatus, ItemStatus, ItemType, Visibility,
)
from app.schemas.item import (
    ApprovalUpdate, ItemCreate, ItemDetail, ItemList, ItemOut, MatchOut, StatusUpdate,
    TimelineStep,
)
from app.services import workflow

router = APIRouter(tags=["items"])


def _can_see_private(item: Item, viewer: User | None) -> bool:
    return bool(viewer and (is_admin(viewer) or item.reported_by == viewer.id))


def serialize(item: Item, viewer: User | None) -> ItemOut:
    out = ItemOut.model_validate(item)
    if not _can_see_private(item, viewer):
        out.private_details = None
    return out


def _visible(item: Item, viewer: User | None) -> bool:
    return item.approval_status != ApprovalStatus.REJECTED.value or _can_see_private(item, viewer)


def ensure_access(item: Item, viewer: User | None) -> None:
    """PRIVATE items are only for their reporter and admins. Enforced server-side for every route."""
    if item.visibility == Visibility.PRIVATE.value and not _can_see_private(item, viewer):
        if viewer is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This report is private")


def _get_item_or_404(db: Session, item_id: int, viewer: User | None) -> Item:
    item = db.get(Item, item_id)
    if not item or not _visible(item, viewer):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    ensure_access(item, viewer)
    return item


def _require_owner_or_admin(item: Item, user: User) -> None:
    if not _can_see_private(item, user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only modify your own items")


@router.get("/meta")
def meta():
    return {"categories": CATEGORIES, "locations": LOCATIONS}


@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(body: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = Item(**body.model_dump(mode="python"), reported_by=user.id)
    item.type = body.type.value
    item.visibility = body.visibility.value
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item, user)


@router.get("/items", response_model=ItemList)
def list_items(
    q: str | None = None,
    type: ItemType | None = None,
    category: str | None = None,
    brand: str | None = None,
    color: str | None = None,
    location: str | None = None,
    date_on: date | None = Query(None, alias="date"),
    status_: ItemStatus | None = Query(None, alias="status"),
    visibility: Visibility | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
):
    stmt = select(Item)
    if is_admin(viewer):
        pass
    elif viewer:
        stmt = stmt.where(
            or_(Item.approval_status != ApprovalStatus.REJECTED.value, Item.reported_by == viewer.id)
        )
    else:
        stmt = stmt.where(Item.approval_status != ApprovalStatus.REJECTED.value)

    if not is_admin(viewer):
        # PRIVATE reports never appear in listings/search (owners use /users/me/items).
        stmt = stmt.where(Item.visibility != Visibility.PRIVATE.value)
    elif visibility:
        stmt = stmt.where(Item.visibility == visibility.value)

    if q and q.strip():
        like = f"%{q.strip().lower()}%"
        stmt = stmt.where(or_(*[
            func.lower(col).like(like)
            for col in (Item.title, Item.description, Item.brand, Item.color, Item.category, Item.location)
        ]))
    if type:
        stmt = stmt.where(Item.type == type.value)
    if category:
        stmt = stmt.where(Item.category == category)
    if brand:
        stmt = stmt.where(func.lower(Item.brand).like(f"%{brand.strip().lower()}%"))
    if color:
        stmt = stmt.where(func.lower(Item.color).like(f"%{color.strip().lower()}%"))
    if location:
        stmt = stmt.where(Item.location == location)
    if date_on:
        stmt = stmt.where(Item.date == date_on)
    if status_:
        stmt = stmt.where(Item.status == status_.value)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(
        stmt.order_by(Item.created_at.desc(), Item.id.desc()).limit(limit).offset(offset)
    ).unique().all()
    return ItemList(items=[serialize(i, viewer) for i in rows], total=total or 0)


def _candidates(db: Session, item: Item) -> list[Item]:
    opposite = ItemType.FOUND if item.type == ItemType.LOST.value else ItemType.LOST
    return list(db.scalars(
        select(Item).where(
            Item.type == opposite.value,
            Item.status == ItemStatus.ACTIVE.value,
            Item.approval_status != ApprovalStatus.REJECTED.value,
            Item.id != item.id,
        )
    ).unique().all())


def _features(i: Item) -> ItemFeatures:
    return ItemFeatures(i.id, i.title, i.description, i.category, i.brand, i.color, i.location, i.date)


def _can_view_match(candidate: Item, viewer: User | None) -> bool:
    return candidate.visibility != Visibility.PRIVATE.value or _can_see_private(candidate, viewer)


def _matches(db: Session, item: Item, viewer: User | None) -> list[MatchOut]:
    # Candidates are limited to reports this viewer may see *before* scoring, so a PRIVATE report can
    # never influence (or appear in) what another user sees - not even through TF-IDF weights.
    # PRIVATE reports still match normally for their reporter and for admins, who can see them.
    cands = [c for c in _candidates(db, item) if _can_view_match(c, viewer)]
    by_id = {c.id: c for c in cands}
    results = find_matches(_features(item), [_features(c) for c in cands])
    return [
        MatchOut(
            match_score=r.score, matching_attributes=r.attributes, explanation=r.explanation,
            item=serialize(by_id[r.item_id], viewer),
        )
        for r in results
    ]


@router.get("/items/{item_id}", response_model=ItemDetail)
def get_item(item_id: int, db: Session = Depends(get_db), viewer: User | None = Depends(get_optional_user)):
    item = _get_item_or_404(db, item_id, viewer)
    claim_statuses = {c.status for c in item.claims}
    returned = item.status == ItemStatus.RETURNED.value
    has_match = item.status != ItemStatus.ACTIVE.value or bool(_matches(db, item, viewer))
    timeline = [
        TimelineStep(key="reported", label="Reported", done=True),
        TimelineStep(key="match", label="Potential Match", done=has_match),
        TimelineStep(key="claim", label="Claim Submitted", done=bool(claim_statuses) or returned),
        TimelineStep(
            key="approved", label="Claim Approved",
            done=bool(claim_statuses & {ClaimStatus.APPROVED.value, ClaimStatus.COMPLETED.value}) or returned,
        ),
        TimelineStep(key="returned", label="Item Returned", done=returned),
    ]
    base = serialize(item, viewer)
    return ItemDetail(**base.model_dump(), timeline=timeline)


@router.get("/items/{item_id}/matches", response_model=list[MatchOut])
def item_matches(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = _get_item_or_404(db, item_id, user)
    return _matches(db, item, user)


@router.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, body: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = _get_item_or_404(db, item_id, user)
    _require_owner_or_admin(item, user)
    if not is_admin(user) and item.status != ItemStatus.ACTIVE.value:
        raise HTTPException(status.HTTP_409_CONFLICT, "Items with claims can no longer be edited")
    for k, v in body.model_dump(mode="python").items():
        setattr(item, k, v.value if hasattr(v, "value") else v)
    db.commit()
    db.refresh(item)
    return serialize(item, user)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = _get_item_or_404(db, item_id, user)
    _require_owner_or_admin(item, user)
    if item.claims and not is_admin(user):
        raise HTTPException(status.HTTP_409_CONFLICT, "Items with claims can only be deleted by an admin")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/items/{item_id}/status", response_model=ItemOut)
def update_status(item_id: int, body: StatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = _get_item_or_404(db, item_id, user)
    _require_owner_or_admin(item, user)
    new = body.status
    if not is_admin(user):
        if new != ItemStatus.CLOSED or item.status != ItemStatus.ACTIVE.value:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only close your own active items")
    if new == ItemStatus.RETURNED:
        if item.status != ItemStatus.CLAIMED.value:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only items with an approved claim can be marked returned")
        workflow.complete_item(db, item)
    else:
        item.status = new.value
    db.commit()
    db.refresh(item)
    return serialize(item, user)


@router.get("/users/me/items", response_model=list[ItemOut])
def my_items(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(Item).where(Item.reported_by == user.id).order_by(Item.created_at.desc(), Item.id.desc())
    ).unique().all()
    return [serialize(i, user) for i in rows]


@router.patch("/admin/items/{item_id}/approval", response_model=ItemOut)
def set_approval(item_id: int, body: ApprovalUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    item.approval_status = body.approval_status.value
    db.commit()
    db.refresh(item)
    return serialize(item, admin)
