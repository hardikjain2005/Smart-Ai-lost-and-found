"""PRIVATE / PUBLIC item visibility: enforced by the backend on every route."""

import json
from datetime import date

import pytest

from test_workflow import ADMIN, AARAV, DIYA, login

SECRET = "gold-chain-private-serial-GC-8841"
HIDDEN_DESC = "hidden-description-engraved-initials-XQ"


def body(title="Gold Chain", type_="LOST", visibility="PRIVATE", **extra):
    return {
        "title": title, "type": type_, "category": "Accessories", "brand": "Tanishq", "color": "Gold",
        "description": "22 carat gold chain with a small pendant", "location": "Sports Complex",
        "date": date.today().isoformat(), "private_details": SECRET, "visibility": visibility, **extra,
    }


def rohan(client):
    return login(client, ("rohan@campusfind.edu", "DemoPass-test1"))


_created: list[int] = []


def make(client, headers, **kw):
    r = client.post("/api/items", json=body(**kw), headers=headers)
    assert r.status_code == 201, r.text
    _created.append(r.json()["id"])
    return r.json()


@pytest.fixture(autouse=True)
def cleanup(client):
    """Remove every item a test created so the shared in-memory DB stays at its seeded state."""
    yield
    admin = login(client, ADMIN)
    while _created:
        client.delete(f"/api/items/{_created.pop()}", headers=admin)


def ids(resp):
    return {i["id"] for i in resp.json()["items"]}


def test_default_is_public_and_seeded_items_stay_public(client):
    items = client.get("/api/items", params={"limit": 100}).json()["items"]
    assert len(items) >= 13 and all(i["visibility"] == "PUBLIC" for i in items)
    created = client.post("/api/items", json={k: v for k, v in body().items() if k != "visibility"},
                          headers=login(client, AARAV)).json()
    _created.append(created["id"])
    assert created["visibility"] == "PUBLIC"


def test_public_item_is_listed_and_searchable(client):
    h = login(client, AARAV)
    pub = make(client, h, title="Public Silver Ring", visibility="PUBLIC")
    assert pub["id"] in ids(client.get("/api/items"))
    assert pub["id"] in ids(client.get("/api/items", params={"q": "silver ring"}))
    assert client.get(f"/api/items/{pub['id']}").status_code == 200


def test_private_item_hidden_from_listing_and_search(client):
    h = login(client, AARAV)
    priv = make(client, h, title="Private Platinum Bracelet")
    assert priv["visibility"] == "PRIVATE"
    for headers in ({}, login(client, DIYA), h):  # anonymous, other student, even the owner
        assert priv["id"] not in ids(client.get("/api/items", headers=headers, params={"limit": 100}))
        for params in ({"q": "platinum"}, {"q": "bracelet"}, {"category": "Accessories"}, {"type": "LOST"},
                       {"location": "Sports Complex"}, {"brand": "tanishq"}, {"color": "gold"},
                       {"visibility": "PRIVATE"}):
            r = client.get("/api/items", headers=headers, params={**params, "limit": 100})
            assert priv["id"] not in ids(r), (params, headers and "auth")
    text = client.get("/api/items", params={"limit": 100}).text
    assert "Platinum" not in text and SECRET not in text


def test_private_item_access_control(client):
    a, b, admin = login(client, AARAV), login(client, DIYA), login(client, ADMIN)
    priv = make(client, a, title="Private Gold Chain Access", description=HIDDEN_DESC)
    url = f"/api/items/{priv['id']}"
    assert client.get(url, headers=a).status_code == 200
    assert client.get(url, headers=admin).status_code == 200
    assert client.get(url, headers=b).status_code == 403
    assert client.get(url).status_code == 401
    # every other route is protected too
    for method, path, kw in (
        ("get", f"{url}/matches", {}),
        ("put", url, {"json": body(title="Hijack")}),
        ("delete", url, {}),
        ("patch", f"{url}/status", {"json": {"status": "CLOSED"}}),
    ):
        assert getattr(client, method)(path, headers=b, **kw).status_code == 403, (method, path)
    # nothing leaked in the error bodies
    leak = client.get(url, headers=b).text
    assert SECRET not in leak and HIDDEN_DESC not in leak and "Gold Chain" not in leak
    # owner sees private details, appears in /my-items with the flag
    mine = client.get("/api/users/me/items", headers=a).json()
    assert priv["id"] in {i["id"] for i in mine}
    assert next(i for i in mine if i["id"] == priv["id"])["visibility"] == "PRIVATE"
    assert client.get(url, headers=a).json()["private_details"] == SECRET
    assert priv["id"] not in {i["id"] for i in client.get("/api/users/me/items", headers=b).json()}
    # admin can list private reports (and only admin can via the filter)
    adm = client.get("/api/items", headers=admin, params={"visibility": "PRIVATE", "limit": 100})
    assert priv["id"] in ids(adm)
    assert all(i["visibility"] == "PRIVATE" for i in adm.json()["items"])
    pend = client.get("/api/admin/pending-items", headers=admin).json()
    assert priv["id"] in {i["id"] for i in pend}


def test_private_item_still_participates_in_matching_without_leaking(client):
    a, b, c, admin = login(client, AARAV), login(client, DIYA), rohan(client), login(client, ADMIN)
    lost = make(client, a, title="Gold Chain Match", type_="LOST", description=HIDDEN_DESC)  # PRIVATE
    found = make(client, b, title="Gold Chain Match", type_="FOUND", visibility="PUBLIC",
                 private_details="finder-private-note-ZZ")

    # owner of the private lost item gets the public found item as a match
    mine = client.get(f"/api/items/{lost['id']}/matches", headers=a).json()
    hit = next(m for m in mine if m["item"]["id"] == found["id"])
    assert hit["match_score"] >= 70 and "same brand" in hit["matching_attributes"]
    assert "finder-private-note-ZZ" not in json.dumps(mine)  # finder's private note is not shown to the owner
    assert HIDDEN_DESC not in hit["explanation"] and SECRET not in hit["explanation"]

    # admin sees the pair from either side
    adm_lost = client.get(f"/api/items/{lost['id']}/matches", headers=admin).json()
    assert any(m["item"]["id"] == found["id"] for m in adm_lost)
    adm_found = client.get(f"/api/items/{found['id']}/matches", headers=admin).json()
    assert any(m["item"]["id"] == lost["id"] for m in adm_found)

    # the finder (another student) is NOT shown the private lost report
    theirs = client.get(f"/api/items/{found['id']}/matches", headers=b).json()
    assert all(m["item"]["id"] != lost["id"] for m in theirs)
    blob = json.dumps(theirs)
    assert SECRET not in blob and HIDDEN_DESC not in blob
    assert str(lost["id"]) not in [str(m["item"]["id"]) for m in theirs]
    # a third student sees no private match either, nor a timeline 'Potential Match' caused by it
    assert all(m["item"]["id"] != lost["id"] for m in client.get(f"/api/items/{found['id']}/matches", headers=c).json())
    tl = client.get(f"/api/items/{found['id']}", headers=b).json()["timeline"]
    assert next(s for s in tl if s["key"] == "match")["done"] is False
    # …but the owner's timeline does show it
    tl_owner = client.get(f"/api/items/{lost['id']}", headers=a).json()["timeline"]
    assert next(s for s in tl_owner if s["key"] == "match")["done"] is True


def test_private_matches_are_visible_to_their_own_reporter(client):
    a, b = login(client, AARAV), login(client, DIYA)
    priv_found = make(client, a, title="Gold Bangle Own", type_="FOUND")
    lost_pub = make(client, b, title="Gold Bangle Own", type_="LOST", visibility="PUBLIC")
    # B's public lost report must not reveal A's private found report
    assert all(m["item"]["id"] != priv_found["id"] for m in client.get(f"/api/items/{lost_pub['id']}/matches", headers=b).json())
    # A (reporter of the private found item) sees B's public lost report
    assert any(m["item"]["id"] == lost_pub["id"] for m in client.get(f"/api/items/{priv_found['id']}/matches", headers=a).json())


def test_private_items_cannot_be_claimed_by_others(client):
    a, b = login(client, AARAV), login(client, DIYA)
    priv = make(client, a, title="Private Found Watch", type_="FOUND")
    claim = {"reason": "Mine", "lost_location": "Gym", "verification_answer": "Engraving on the back"}
    assert client.post(f"/api/items/{priv['id']}/claim", json=claim, headers=b).status_code == 403


def test_visibility_can_be_changed_by_owner_only(client):
    a, b = login(client, AARAV), login(client, DIYA)
    item = make(client, a, title="Switchable Item", visibility="PUBLIC")
    assert item["id"] in ids(client.get("/api/items"))
    r = client.put(f"/api/items/{item['id']}", json=body(title="Switchable Item", visibility="PRIVATE"), headers=a)
    assert r.status_code == 200 and r.json()["visibility"] == "PRIVATE"
    assert item["id"] not in ids(client.get("/api/items", params={"limit": 100}))
    assert client.get(f"/api/items/{item['id']}", headers=b).status_code == 403
    assert client.post("/api/items", json=body(visibility="SECRET"), headers=a).status_code == 422


def test_public_claim_workflow_unaffected(client):
    a, b, admin = login(client, AARAV), login(client, DIYA), login(client, ADMIN)
    found = make(client, b, title="Public Keys Flow", type_="FOUND", visibility="PUBLIC", category="Keys")
    claim = {"reason": "Mine", "lost_location": "Gym", "verification_answer": "Blue keychain"}
    r = client.post(f"/api/items/{found['id']}/claim", json=claim, headers=a)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.patch(f"/api/claims/{cid}/status", json={"status": "APPROVED"}, headers=admin).status_code == 200
    assert client.patch(f"/api/items/{found['id']}/status", json={"status": "RETURNED"}, headers=admin).status_code == 200


def test_private_item_does_not_shift_scores_seen_by_others(client):
    """A private report must not change the public match scores other users see (no side channel)."""
    b = login(client, DIYA)
    lost_bottle = next(i for i in client.get("/api/items", params={"q": "blue water bottle"}).json()["items"])
    before = client.get(f"/api/items/{lost_bottle['id']}/matches", headers=b).json()
    make(client, login(client, AARAV), title="Blue Steel Water Bottle", type_="FOUND", category="Water Bottles",
         brand="Milton", color="Blue", location="Cafeteria", description="Blue steel bottle with a dent")
    after = client.get(f"/api/items/{lost_bottle['id']}/matches", headers=b).json()
    assert [(m["item"]["id"], m["match_score"]) for m in before] == [(m["item"]["id"], m["match_score"]) for m in after]
    admin_view = client.get(f"/api/items/{lost_bottle['id']}/matches", headers=login(client, ADMIN)).json()
    assert len(admin_view) == len(after) + 1  # admin additionally sees the private report
