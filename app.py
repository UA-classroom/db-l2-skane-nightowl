from typing import List

from fastapi import FastAPI, HTTPException, status
from psycopg2.extras import RealDictCursor

from db import (
    accept_bid,
    add_favorite,
    create_address,
    create_bid,
    create_listing,
    create_user,
    create_viewing,
    delete_listing,
    delete_user,
    get_bids_for_listing,
    get_connection,
    get_listing_by_id,
    get_listings,
    get_user_by_id,
    get_user_favorites,
    get_users,
    get_viewings_for_listing,
    remove_favorite,
    update_listing,
    update_listing_status,
    update_user,
)
from schemas import BidCreate, ListingCreate, UserCreate, ViewingCreate

app = FastAPI()


# ---------- USERS ----------

@app.get("/users", status_code=status.HTTP_200_OK)
def api_get_users():
    con = get_connection()
    users = get_users(con)
    con.close()
    return users


@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def api_get_user(user_id: int):
    con = get_connection()
    user = get_user_by_id(con, user_id)
    con.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", status_code=status.HTTP_201_CREATED)
def api_create_user(user: UserCreate):
    con = get_connection()
    created = create_user(
        con,
        user.email,
        user.password_hash,
        user.first_name,
        user.last_name,
        user.role_id,
    )
    con.close()
    return created


@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
def api_update_user(user_id: int, first_name: str, last_name: str):
    con = get_connection()
    updated = update_user(con, user_id, first_name, last_name)
    con.close()
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def api_delete_user(user_id: int):
    con = get_connection()
    deleted = delete_user(con, user_id)
    con.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted_user_id": deleted["id"]}


# ---------- LISTINGS ----------

@app.get("/listings", status_code=status.HTTP_200_OK)
def api_get_listings():
    con = get_connection()
    listings = get_listings(con)
    con.close()
    return listings


@app.get("/listings/{listing_id}", status_code=status.HTTP_200_OK)
def api_get_listing(listing_id: int):
    con = get_connection()
    listing = get_listing_by_id(con, listing_id)
    con.close()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@app.post("/listings", status_code=status.HTTP_201_CREATED)
def api_create_listing(listing: ListingCreate):
    con = get_connection()
    created = create_listing(
        con,
        listing.title,
        listing.description,
        listing.price,
        listing.living_area,
        listing.rooms,
        listing.category_id,
        listing.agent_id,
        "active",
        listing.address_id
    )
    con.close()
    return created


@app.put("/listings/{listing_id}", status_code=status.HTTP_200_OK)
def api_update_listing(listing_id: int, title: str, description: str, price: int):
    con = get_connection()
    updated = update_listing(con, listing_id, title, description, price)
    con.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@app.patch("/listings/{listing_id}/status", status_code=status.HTTP_200_OK)
def api_update_listing_status(listing_id: int, status_value: str):
    con = get_connection()
    updated = update_listing_status(con, listing_id, status_value)
    con.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@app.delete("/listings/{listing_id}", status_code=status.HTTP_200_OK)
def api_delete_listing(listing_id: int):
    con = get_connection()
    deleted = delete_listing(con, listing_id)
    con.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"deleted_listing_id": deleted["id"]}


# ---------- BIDS ----------

@app.get("/listings/{listing_id}/bids", status_code=status.HTTP_200_OK)
def api_get_bids(listing_id: int):
    con = get_connection()
    bids = get_bids_for_listing(con, listing_id)
    con.close()
    return bids


@app.post("/listings/{listing_id}/bids", status_code=status.HTTP_201_CREATED)
def api_create_bid(listing_id: int, bid: BidCreate):
    con = get_connection()
    created = create_bid(con, listing_id, bid.bidder_id, bid.amount)
    con.close()
    return created


@app.patch("/bids/{bid_id}/accept", status_code=status.HTTP_200_OK)
def api_accept_bid(bid_id: int):
    con = get_connection()
    accepted = accept_bid(con, bid_id)
    con.close()
    if not accepted:
        raise HTTPException(status_code=404, detail="Bid not found")
    return accepted


# ---------- FAVORITES ----------

@app.post("/favorites", status_code=status.HTTP_201_CREATED)
def api_add_favorite(user_id: int, listing_id: int):
    con = get_connection()
    favorite = add_favorite(con, user_id, listing_id)
    con.close()
    return favorite


@app.delete("/favorites", status_code=status.HTTP_200_OK)
def api_remove_favorite(user_id: int, listing_id: int):
    con = get_connection()
    removed = remove_favorite(con, user_id, listing_id)
    con.close()
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return removed


@app.get("/users/{user_id}/favorites", status_code=status.HTTP_200_OK)
def api_get_user_favorites(user_id: int):
    con = get_connection()
    favorites = get_user_favorites(con, user_id)
    con.close()
    return favorites

@app.get("/categories")
def get_categories():
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM listing_categories;")
            data = cur.fetchall()
    con.close()
    return data

@app.post("/categories", status_code=201)
def create_category(name: str):
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute(
                "INSERT INTO listing_categories (name) VALUES (%s) RETURNING *;",
                (name,)
            )
            created = cur.fetchone()
    con.close()
    return created

@app.get("/agencies")
def get_agencies():
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM real_estate_agencies;")
            data = cur.fetchall()
    con.close()
    return data

@app.get("/agencies/{agency_id}/listings")
def get_agency_listings(agency_id: int):
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute(
                "SELECT * FROM listings WHERE agency_id = %s;",
                (agency_id,)
            )
            data = cur.fetchall()
    con.close()
    return data

# ---------- VIEWINGS ----------

@app.get("/listings/{listing_id}/viewings", status_code=200)
def api_get_viewings(listing_id: int):
    con = get_connection()
    viewings = get_viewings_for_listing(con, listing_id)
    con.close()
    return viewings


@app.post("/listings/{listing_id}/viewings", status_code=201)
def api_create_viewing(listing_id: int, viewing: ViewingCreate):
    con = get_connection()
    created = create_viewing(
        con,
        listing_id,
        viewing.start_time,
        viewing.end_time
    )
    con.close()
    return created

# ---------- AGENT REVIEWS ----------
@app.get("/agents/{agent_id}/reviews")
def get_agent_reviews(agent_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM agent_reviews WHERE agent_id = %s;",
                (agent_id,)
            )
            reviews = cur.fetchall()
    con.close()
    return reviews

@app.post("/agents/{agent_id}/reviews")
def create_agent_review(agent_id: int, reviewer_id: int, rating: int, comment: str = None):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO agent_reviews (agent_id, reviewer_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                RETURNING *;
                """,
                (agent_id, reviewer_id, rating, comment)
            )
            review = cur.fetchone()
    con.close()
    return review

# ---------- IMAGES ----------
@app.get("/listings/{listing_id}/images")
def get_listing_images(listing_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM images WHERE listing_id = %s ORDER BY position ASC;",
                (listing_id,)
            )
            images = cur.fetchall()
    con.close()
    return images

@app.post("/listings/{listing_id}/images")
def create_listing_image(listing_id: int, image_url: str, position: int = None):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO images (listing_id, image_url, position)
                VALUES (%s, %s, %s)
                RETURNING *;
                """,
                (listing_id, image_url, position)
            )
            image = cur.fetchone()
    con.close()
    return image

# ---------- ADDRESSES ----------
@app.post("/addresses", status_code=201)
def api_create_address(street: str, postal_code: str, city: str, country: str):
    con = get_connection()
    created = create_address(con, street, postal_code, city, country)
    con.close()
    return created