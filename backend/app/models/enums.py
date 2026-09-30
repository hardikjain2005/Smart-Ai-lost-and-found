from enum import Enum


class Role(str, Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class ItemType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ItemStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MATCHED = "MATCHED"
    CLAIMED = "CLAIMED"
    RETURNED = "RETURNED"
    CLOSED = "CLOSED"


class Visibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


CATEGORIES = [
    "Electronics", "Books & Stationery", "ID & Cards", "Clothing", "Accessories",
    "Keys", "Bags", "Wallets", "Water Bottles", "Other",
]
LOCATIONS = [
    "Central Library", "Cafeteria", "Computer Lab", "Hostel", "Auditorium",
    "Sports Complex", "Main Gate",
]
