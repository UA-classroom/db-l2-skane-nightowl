import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


# ---------- CONNECTION ----------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# ---------- USERS ----------

def get_users(con):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, email, first_name, last_name, role_id FROM users;")
        return cur.fetchall()


def get_user_by_id(con, user_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
        return cur.fetchone()


def create_user(con, email, password_hash, first_name, last_name, role_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO users (email, password_hash, first_name, last_name, role_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (email, password_hash, first_name, last_name, role_id),
        )
        return cur.fetchone()


def update_user(con, user_id, first_name, last_name):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE users
            SET first_name = %s, last_name = %s
            WHERE id = %s
            RETURNING *;
            """,
            (first_name, last_name, user_id),
        )
        return cur.fetchone()


def delete_user(con, user_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "DELETE FROM users WHERE id = %s RETURNING id;",
            (user_id,),
        )
        return cur.fetchone()


# ---------- LISTINGS ----------

def get_listings(con):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM listings;")
        return cur.fetchall()


def get_listing_by_id(con, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM listings WHERE id = %s;", (listing_id,))
        return cur.fetchone()


def create_listing(
    con,
    title,
    description,
    price,
    living_area,
    rooms,
    category_id,
    agent_id,
    status,
    address_id,
):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO listings
            (title, description, price, living_area, rooms,
            category_id, agent_id, status, address_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                title,
                description,
                price,
                living_area,
                rooms,
                category_id,
                agent_id,
                status,
                address_id,
            ),
        )
        return cur.fetchone()


def update_listing(con, listing_id, title, description, price):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE listings
            SET title = %s, description = %s, price = %s
            WHERE id = %s
            RETURNING *;
            """,
            (title, description, price, listing_id),
        )
        return cur.fetchone()


def update_listing_status(con, listing_id, status):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE listings
            SET status = %s
            WHERE id = %s
            RETURNING *;
            """,
            (status, listing_id),
        )
        return cur.fetchone()


def delete_listing(con, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "DELETE FROM listings WHERE id = %s RETURNING id;",
            (listing_id,),
        )
        return cur.fetchone()


# ---------- BIDS ----------

def get_bids_for_listing(con, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM bids WHERE listing_id = %s ORDER BY amount DESC;",
            (listing_id,),
        )
        return cur.fetchall()


def create_bid(con, listing_id, bidder_id, amount):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO bids (listing_id, bidder_id, amount)
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (listing_id, bidder_id, amount),
        )
        return cur.fetchone()


def accept_bid(con, bid_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE bids
            SET is_accepted = TRUE
            WHERE id = %s
            RETURNING *;
            """,
            (bid_id,),
        )
        return cur.fetchone()


# ---------- FAVORITES ----------

def add_favorite(con, user_id, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO favorites (user_id, listing_id)
            VALUES (%s, %s)
            RETURNING *;
            """,
            (user_id, listing_id),
        )
        return cur.fetchone()


def remove_favorite(con, user_id, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            DELETE FROM favorites
            WHERE user_id = %s AND listing_id = %s
            RETURNING *;
            """,
            (user_id, listing_id),
        )
        return cur.fetchone()


def get_user_favorites(con, user_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT l.*
            FROM listings l
            JOIN favorites f ON l.id = f.listing_id
            WHERE f.user_id = %s;
            """,
            (user_id,),
        )
        return cur.fetchall()

# ---------- VIEWINGS ----------

def get_viewings_for_listing(con, listing_id):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM viewings WHERE listing_id = %s;",
            (listing_id,)
        )
        return cur.fetchall()


def create_viewing(con, listing_id, start_time, end_time=None):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO viewings (listing_id, start_time, end_time)
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (listing_id, start_time, end_time),
        )
        return cur.fetchone()
    
# ---------- ADDRESSES ----------

def create_address(con, street, postal_code, city, country):
    with con, con.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO addresses (street, postal_code, city, country)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """,
            (street, postal_code, city, country),
        )
        return cur.fetchone()