"""End-to-end demo workflow against the real FastAPI app (in-memory DB, seeded demo data)."""

import io
from datetime import date

import pytest
from PIL import Image

ADMIN = ("admin@campusfind.edu", "AdminPass-test1")
AARAV = ("aarav@campusfind.edu", "DemoPass-test1")
DIYA = ("diya@campusfind.edu", "DemoPass-test1")
SECRET = "xyzzy-unique-private-marking"


def login(client, creds):
    r = client.post("/api/auth/login", json={"email": creds[0], "password": creds[1]})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def png_bytes(fmt="PNG"):
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), "red").save(buf, fmt)
    return buf.getvalue()


# ---------- auth ----------
def test_register_login_me_and_no_password_leak(client):
    r = client.post("/api/auth/register", json={
        "full_name": "New Student", "email": "New.Student@campusfind.edu", "password": "S3cretPass!"})
    assert r.status_code == 201
    assert "password" not in r.text
    assert r.json()["role"] == "STUDENT"
    assert client.post("/api/auth/register", json={
        "full_name": "Dup", "email": "new.student@campusfind.edu", "password": "S3cretPass!"}).status_code == 409
    h = login(client, ("new.student@campusfind.edu", "S3cretPass!"))
    me = client.get("/api/auth/me", headers=h)
    assert me.status_code == 200 and "password" not in me.text


def test_auth_rejections(client):
    assert client.post("/api/auth/login", json={"email": AARAV[0], "password": "wrong-password"}).status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401
    r = client.post("/api/auth/register", json={
        "full_name": "Evil", "email": "evil@campusfind.edu", "password": "S3cretPass!", "role": "ADMIN"})
    assert r.status_code == 422


# ---------- items, privacy, search ----------
def test_item_privacy_and_permissions(client):
    h = login(client, AARAV)
    body = {"title": "Green Backpack", "type": "LOST", "category": "Bags", "brand": "Wildcraft",
            "color": "Green", "description": "Green backpack", "location": "Hostel",
            "date": date.today().isoformat(), "private_details": SECRET}
    created = client.post("/api/items", json=body, headers=h)
    assert created.status_code == 201
    iid = created.json()["id"]
    assert created.json()["private_details"] == SECRET  # owner sees it

    assert SECRET not in client.get(f"/api/items/{iid}").text  # anonymous
    assert SECRET not in client.get("/api/items").text
    assert SECRET not in client.get(f"/api/items/{iid}", headers=login(client, DIYA)).text
    assert SECRET in client.get(f"/api/items/{iid}", headers=login(client, ADMIN)).text

    assert client.put(f"/api/items/{iid}", json=body, headers=login(client, DIYA)).status_code == 403
    assert client.delete(f"/api/items/{iid}", headers=login(client, DIYA)).status_code == 403
    body["title"] = "Green Backpack v2"
    assert client.put(f"/api/items/{iid}", json=body, headers=h).json()["title"] == "Green Backpack v2"
    assert client.get("/api/users/me/items", headers=h).json()[0]["id"] == iid
    assert client.delete(f"/api/items/{iid}", headers=h).status_code == 204
    assert client.get(f"/api/items/{iid}").status_code == 404


def test_item_validation(client):
    h = login(client, AARAV)
    base = {"title": "X item", "type": "LOST", "category": "Bags", "location": "Hostel",
            "date": date.today().isoformat()}
    assert client.post("/api/items", json={**base, "category": "Nope"}, headers=h).status_code == 422
    assert client.post("/api/items", json={**base, "location": "Moon"}, headers=h).status_code == 422
    assert client.post("/api/items", json={**base, "date": "2999-01-01"}, headers=h).status_code == 422
    assert client.post("/api/items", json={**base, "image_url": "http://evil/x.png"}, headers=h).status_code == 422
    assert client.post("/api/items", json=base).status_code == 401


def test_search_and_filters(client):
    def ids(**params):
        r = client.get("/api/items", params=params)
        assert r.status_code == 200
        return r.json()["items"]

    assert len(ids()) >= 11
    assert all(i["type"] == "FOUND" for i in ids(type="FOUND"))
    assert all(i["category"] == "Electronics" for i in ids(category="Electronics"))
    assert all(i["location"] == "Cafeteria" for i in ids(location="Cafeteria"))
    assert {i["title"] for i in ids(q="umbrella")} == {"Red Umbrella"}
    assert all(i["brand"] == "Dell" for i in ids(brand="dell"))
    assert ids(q="zzz-no-such-thing") == []
    assert all(i["status"] == "ACTIVE" for i in ids(status="ACTIVE"))
    assert ids(date="2000-01-01") == []


def test_image_upload_validation(client):
    h = login(client, AARAV)
    ok = client.post("/api/uploads", files={"file": ("a.png", png_bytes(), "image/png")}, headers=h)
    assert ok.status_code == 201
    url = ok.json()["image_url"]
    assert client.get(url).status_code == 200
    assert client.post("/api/uploads", files={"file": ("a.png", png_bytes(), "image/png")}).status_code == 401
    assert client.post("/api/uploads", files={"file": ("a.gif", png_bytes("GIF"), "image/gif")}, headers=h).status_code == 415
    assert client.post("/api/uploads", files={"file": ("a.png", b"not an image", "image/png")}, headers=h).status_code == 415
    big = b"\x89PNG" + b"0" * (16 * 1024 * 1024)
    assert client.post("/api/uploads", files={"file": ("a.png", big, "image/png")}, headers=h).status_code == 413


# ---------- the demo flow ----------
def test_full_demo_flow(client):
    aarav, diya, admin = login(client, AARAV), login(client, DIYA), login(client, ADMIN)
    stats0 = client.get("/api/admin/stats", headers=admin).json()

    lost = next(i for i in client.get("/api/users/me/items", headers=aarav).json() if i["title"] == "Black Dell Laptop")
    found = next(i for i in client.get("/api/items", params={"type": "FOUND", "q": "dell"}).json()["items"])
    assert lost["type"] == "LOST" and found["type"] == "FOUND"

    # AI match detects the obvious pair, in both directions
    matches = client.get(f"/api/items/{lost['id']}/matches", headers=aarav).json()
    assert matches[0]["item"]["id"] == found["id"]
    assert matches[0]["match_score"] >= 80
    assert {"same category", "same brand", "same color", "same location"} <= set(matches[0]["matching_attributes"])
    assert matches[0]["explanation"]
    assert all(m["item"]["type"] == "FOUND" for m in matches)
    back = client.get(f"/api/items/{found['id']}/matches", headers=diya).json()
    assert back[0]["item"]["id"] == lost["id"]
    assert client.get(f"/api/items/{lost['id']}/matches").status_code == 401

    # claim rules
    claim_body = {"reason": "It is my laptop", "lost_location": "Central Library",
                  "verification_answer": "Small scratch near the Dell logo and a green sticker"}
    assert client.post(f"/api/items/{found['id']}/claim", json=claim_body, headers=diya).status_code == 400  # own report
    assert client.post(f"/api/items/{lost['id']}/claim", json=claim_body, headers=diya).status_code == 400  # lost item
    assert client.post(f"/api/items/{found['id']}/claim", json=claim_body).status_code == 401
    r = client.post(f"/api/items/{found['id']}/claim", json=claim_body, headers=aarav)
    assert r.status_code == 201, r.text
    claim = r.json()
    assert claim["status"] == "PENDING" and claim["item"]["private_details"] is None
    assert client.post(f"/api/items/{found['id']}/claim", json=claim_body, headers=aarav).status_code == 409
    assert client.get(f"/api/items/{found['id']}").json()["status"] == "MATCHED"

    # access control
    assert client.get("/api/claims", headers=diya).json() == []  # diya has no claims
    assert client.get(f"/api/claims/{claim['id']}", headers=diya).status_code == 404
    assert client.patch(f"/api/claims/{claim['id']}/status", json={"status": "APPROVED"}, headers=aarav).status_code == 403
    assert client.get("/api/admin/stats", headers=aarav).status_code == 403
    assert client.get("/api/admin/stats").status_code == 401

    # admin sees the claim plus the private details needed to verify it
    admin_claims = client.get("/api/claims", params={"status": "PENDING"}, headers=admin).json()
    seen = next(c for c in admin_claims if c["id"] == claim["id"])
    assert seen["verification_answer"] == claim_body["verification_answer"]
    assert "scratch" in seen["item"]["private_details"]
    assert client.get("/api/admin/stats", headers=admin).json()["pending_claims"] >= 1

    # cannot skip steps
    assert client.patch(f"/api/items/{found['id']}/status", json={"status": "RETURNED"}, headers=admin).status_code == 400
    assert client.patch(f"/api/claims/{claim['id']}/status", json={"status": "COMPLETED"}, headers=admin).status_code == 400

    r = client.patch(f"/api/claims/{claim['id']}/status",
                     json={"status": "APPROVED", "review_comment": "Verified"}, headers=admin)
    assert r.status_code == 200 and r.json()["status"] == "APPROVED"
    detail = client.get(f"/api/items/{found['id']}").json()
    assert detail["status"] == "CLAIMED"
    assert [s["done"] for s in detail["timeline"]] == [True, True, True, True, False]

    r = client.patch(f"/api/items/{found['id']}/status", json={"status": "RETURNED"}, headers=admin)
    assert r.status_code == 200 and r.json()["status"] == "RETURNED"
    detail = client.get(f"/api/items/{found['id']}").json()
    assert all(s["done"] for s in detail["timeline"])
    assert client.get(f"/api/claims/{claim['id']}", headers=aarav).json()["status"] == "COMPLETED"

    stats1 = client.get("/api/admin/stats", headers=admin).json()
    assert stats1["returned_items"] == stats0["returned_items"] + 1
    assert stats1["pending_claims"] == stats0["pending_claims"]
    assert client.get("/api/admin/activity", headers=admin).json()
    # returned items are no longer offered as matches
    assert all(m["item"]["id"] != found["id"] for m in client.get(f"/api/items/{lost['id']}/matches", headers=aarav).json())


def test_admin_report_moderation(client):
    h, admin = login(client, DIYA), login(client, ADMIN)
    body = {"title": "Suspicious Post", "type": "FOUND", "category": "Other", "location": "Main Gate",
            "date": date.today().isoformat()}
    iid = client.post("/api/items", json=body, headers=h).json()["id"]
    pending = client.get("/api/admin/pending-items", headers=admin).json()
    assert iid in [i["id"] for i in pending]
    assert client.get("/api/admin/pending-items", headers=h).status_code == 403
    assert client.patch(f"/api/admin/items/{iid}/approval", json={"approval_status": "APPROVED"}, headers=h).status_code == 403
    r = client.patch(f"/api/admin/items/{iid}/approval", json={"approval_status": "REJECTED"}, headers=admin)
    assert r.json()["approval_status"] == "REJECTED"
    assert client.get(f"/api/items/{iid}").status_code == 404  # hidden from public
    assert client.get(f"/api/items/{iid}", headers=h).status_code == 200  # owner still sees it


def test_claim_rejection_reopens_item(client):
    aarav, diya, admin = login(client, AARAV), login(client, DIYA), login(client, ADMIN)
    wallet = next(i for i in client.get("/api/items", params={"q": "wallet"}).json()["items"])
    body = {"reason": "Mine", "lost_location": "Cafeteria", "verification_answer": "A red card inside"}
    c = client.post(f"/api/items/{wallet['id']}/claim", json=body, headers=diya).json()
    assert client.get(f"/api/items/{wallet['id']}").json()["status"] == "MATCHED"
    r = client.patch(f"/api/claims/{c['id']}/status", json={"status": "REJECTED", "review_comment": "No match"}, headers=admin)
    assert r.json()["status"] == "REJECTED" and r.json()["review_comment"] == "No match"
    assert client.get(f"/api/items/{wallet['id']}").json()["status"] == "ACTIVE"


def test_weak_matches_are_filtered(client):
    from campusfind_ml.matching import ItemFeatures, find_matches

    q = ItemFeatures(1, "Black Leather Wallet", "wallet", "Wallets", "Wildcraft", "Black", "Cafeteria", date.today())
    weak = ItemFeatures(2, "Black Dell Laptop", "laptop", "Electronics", "Dell", "Black", "Central Library", date.today())
    assert find_matches(q, [weak]) == []


def test_seeded_items_have_servable_demo_images(client):
    items = client.get("/api/items", params={"limit": 100}).json()["items"]
    seeded = [i for i in items if i["reporter_name"] != "Test Student" and i["reporter_name"] != "New Student"]
    assert len(seeded) >= 13
    for item in seeded:
        assert item["image_url"], f"{item['title']} has no image"
        r = client.get(item["image_url"])
        assert r.status_code == 200, item["image_url"]
        with Image.open(io.BytesIO(r.content)) as img:
            assert img.format in {"JPEG", "PNG", "WEBP"}
            img.verify()
        assert len(r.content) < 5 * 1024 * 1024
    titles = {i["title"] for i in seeded}
    assert {"Black Smartphone", "Green Backpack", "Black Leather Wallet", "Scientific Calculator"} <= titles


def test_seed_is_idempotent(client):
    from app.db.session import SessionLocal
    from app.services.seed import seed_demo_data

    before = client.get("/api/items", params={"limit": 100}).json()["total"]
    with SessionLocal() as db:
        seed_demo_data(db)
        seed_demo_data(db)
    assert client.get("/api/items", params={"limit": 100}).json()["total"] == before
