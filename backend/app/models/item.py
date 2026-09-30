from datetime import date, datetime
from datetime import time as dtime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ApprovalStatus, ItemStatus, Visibility


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(10), index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    brand: Mapped[str | None] = mapped_column(String(80))
    color: Mapped[str | None] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(80), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    time: Mapped[dtime | None] = mapped_column(Time)
    image_url: Mapped[str | None] = mapped_column(String(255))
    private_details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=ItemStatus.ACTIVE.value, index=True)
    approval_status: Mapped[str] = mapped_column(
        String(20), default=ApprovalStatus.PENDING.value, index=True
    )
    visibility: Mapped[str] = mapped_column(
        String(10), default=Visibility.PUBLIC.value, server_default=Visibility.PUBLIC.value, index=True
    )
    reported_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    reporter = relationship("User", lazy="joined")
    claims = relationship("Claim", back_populates="item", cascade="all, delete-orphan")

    @property
    def reporter_name(self) -> str:
        return self.reporter.full_name
