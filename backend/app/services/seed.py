"""Development seed data (only when SEED_DEMO_DATA=true). Safe to run on every startup."""

import logging
import shutil
from pathlib import Path
from datetime import date, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import Item, User
from app.models.enums import ApprovalStatus, Role

log = logging.getLogger("campusfind")


ASSETS = Path(__file__).resolve().parents[1] / "seed_assets"
DEMO_DOMAIN = "@campusfind.edu"


def _install_demo_images() -> None:
    """Copy the bundled demo images into UPLOAD_DIR so they are served by the normal /uploads mount."""
    target = Path(get_settings().upload_dir)
    target.mkdir(parents=True, exist_ok=True)
    for src in ASSETS.glob("*.jpg"):
        dest = target / f"demo-{src.name}"
        if not dest.exists():
            shutil.copyfile(src, dest)


def seed_demo_data(db: Session) -> None:
    """Idempotent: creates demo users when the DB is empty, and (re)syncs demo items and images."""
    s = get_settings()
    if not s.seed_demo_data:
        return
    if not db.scalar(select(User.id).limit(1)):
        if not s.seed_admin_password or not s.seed_demo_password:
            log.warning("SEED_DEMO_DATA is on but SEED_ADMIN_PASSWORD/SEED_DEMO_PASSWORD are empty; skipping seed")
            return
        for name, email, role, pw in (
            ("Campus Admin", s.seed_admin_email, Role.ADMIN, s.seed_admin_password),
            ("Aarav Sharma", "aarav@campusfind.edu", Role.STUDENT, s.seed_demo_password),
            ("Diya Patel", "diya@campusfind.edu", Role.STUDENT, s.seed_demo_password),
            ("Rohan Mehta", "rohan@campusfind.edu", Role.STUDENT, s.seed_demo_password),
            ("Dr. Meera Iyer", "meera@campusfind.edu", Role.FACULTY, s.seed_demo_password),
        ):
            db.add(User(full_name=name, email=email, role=role.value, password_hash=hash_password(pw)))
        db.commit()

    owners = {
        k: db.scalar(select(User).where(User.email == f"{k}{DEMO_DOMAIN}"))
        for k in ("aarav", "diya", "rohan", "meera")
    }
    if not all(owners.values()):
        return  # a real database without the demo users: leave it alone
    _install_demo_images()

    today = date.today()
    existing = {(i.title, i.type): i for i in db.scalars(select(Item).where(Item.reported_by.in_([u.id for u in owners.values()]))).unique()}

    # (owner, type, title, category, brand, color, description, location, days_ago, hour, private, image)
    specs = [
        # the obvious matching pair (lost yesterday, found today)
        ("aarav", "LOST", "Black Dell Laptop", "Electronics", "Dell", "Black",
         "Dell laptop with black cover", "Central Library", 1, 15,
         "Small scratch near the Dell logo and a green sticker under the keyboard", "laptop"),
        ("diya", "FOUND", "Black Dell Laptop", "Electronics", "Dell", "Black",
         "Black Dell laptop found near library", "Central Library", 0, 9,
         "Small scratch near the Dell logo", "laptop"),
        ("diya", "LOST", "Blue Water Bottle", "Water Bottles", "Milton", "Blue",
         "Blue steel water bottle with a dent on the side", "Cafeteria", 3, 13,
         "Initials D.P. scratched on the bottom", "bottle"),
        ("rohan", "LOST", "Silver Casio Watch", "Accessories", "Casio", "Silver",
         "Silver digital wrist watch with metal strap", "Sports Complex", 4, 17, "Cracked corner on the glass", "watch"),
        ("diya", "LOST", "Student ID Card", "ID & Cards", None, "White",
         "College ID card in a clear plastic holder", "Hostel", 2, 20, "ID number ends with 4471", "idcard"),
        ("rohan", "LOST", "Physics Textbook", "Books & Stationery", "Pearson", "Red",
         "University Physics textbook, red cover, highlighted pages", "Computer Lab", 5, 11,
         "Name written inside back cover", "textbook"),
        ("diya", "LOST", "Green Backpack", "Bags", "Wildcraft", "Green",
         "Green backpack with a front zip pocket and two side pockets", "Hostel", 2, 19,
         "Keychain with a small panda attached to the zip", "backpack"),
        ("meera", "FOUND", "Red Umbrella", "Accessories", None, "Red",
         "Large red folding umbrella", "Main Gate", 1, 10, "Wooden handle with a small tag", "umbrella"),
        ("rohan", "FOUND", "Set of Keys", "Keys", None, "Silver",
         "Three keys on a ring with a blue keychain", "Auditorium", 2, 18, "Keychain shows a football logo", "keys"),
        ("aarav", "FOUND", "Black Leather Wallet", "Wallets", "Wildcraft", "Black",
         "Black leather wallet found on a cafeteria table", "Cafeteria", 1, 14, "Contains a library card", "wallet"),
        ("meera", "FOUND", "Blue Steel Bottle", "Water Bottles", "Milton", "Blue",
         "Blue steel water bottle with a dent, left near the counter", "Cafeteria", 2, 12,
         "Initials scratched on the bottom", "bottle"),
        ("aarav", "FOUND", "Scientific Calculator", "Electronics", "Casio", "Black",
         "Casio scientific calculator left on a desk", "Computer Lab", 3, 16, "Name sticker on the back", "calculator"),
        ("rohan", "FOUND", "Black Smartphone", "Electronics", "Samsung", "Black",
         "Black smartphone with a purple lock-screen wallpaper", "Sports Complex", 0, 8,
         "Cracked screen protector in the top-left corner", "smartphone"),
    ]
    for owner, type_, title, cat, brand, color, desc, loc, days_ago, hh, private, image in specs:
        url = f"/uploads/demo-{image}.jpg"
        item = existing.get((title, type_))
        if item:
            if not item.image_url:  # backfill images on databases seeded before images existed
                item.image_url = url
            continue
        db.add(Item(
            title=title, type=type_, category=cat, brand=brand, color=color, description=desc,
            location=loc, date=today - timedelta(days=days_ago), time=time(hh, 0),
            private_details=private, image_url=url, reported_by=owners[owner].id,
            approval_status=ApprovalStatus.APPROVED.value,
        ))
    db.commit()
    log.info("Demo data synced")
