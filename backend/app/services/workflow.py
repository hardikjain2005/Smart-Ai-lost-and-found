"""State transitions shared by the item and claim endpoints."""

from sqlalchemy.orm import Session

from app.models import Claim, Item
from app.models.enums import ClaimStatus, ItemStatus


def submit_claim(db: Session, item: Item, claim: Claim) -> None:
    db.add(claim)
    if item.status == ItemStatus.ACTIVE.value:
        item.status = ItemStatus.MATCHED.value


def approve_claim(db: Session, claim: Claim, comment: str | None) -> None:
    claim.status = ClaimStatus.APPROVED.value
    claim.review_comment = comment
    claim.item.status = ItemStatus.CLAIMED.value
    for other in claim.item.claims:
        if other.id != claim.id and other.status == ClaimStatus.PENDING.value:
            other.status = ClaimStatus.REJECTED.value
            other.review_comment = "Another claim for this item was approved."


def reject_claim(db: Session, claim: Claim, comment: str | None) -> None:
    claim.status = ClaimStatus.REJECTED.value
    claim.review_comment = comment
    item = claim.item
    still_pending = any(
        c.status == ClaimStatus.PENDING.value for c in item.claims if c.id != claim.id
    )
    if item.status == ItemStatus.MATCHED.value and not still_pending:
        item.status = ItemStatus.ACTIVE.value


def complete_item(db: Session, item: Item, comment: str | None = None) -> None:
    """Mark the item RETURNED and complete its approved claim."""
    item.status = ItemStatus.RETURNED.value
    for c in item.claims:
        if c.status == ClaimStatus.APPROVED.value:
            c.status = ClaimStatus.COMPLETED.value
            if comment:
                c.review_comment = comment
