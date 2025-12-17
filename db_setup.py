import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def create_tables():
    con = get_connection()
    with con:
        with con.cursor() as cur:

            # ROLES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description VARCHAR(255)
                );
            """)

            # ADDRESSES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                    id SERIAL PRIMARY KEY,
                    street VARCHAR(255) NOT NULL,
                    postal_code VARCHAR(20) NOT NULL,
                    city VARCHAR(255) NOT NULL,
                    country VARCHAR(255) NOT NULL
                );
            """)

            # REAL ESTATE AGENCIES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS real_estate_agencies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(50),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    website VARCHAR(255),
                    is_freelanse BOOLEAN DEFAULT FALSE,
                    address_id INTEGER REFERENCES addresses(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # USERS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(50),
                    role_id INTEGER NOT NULL REFERENCES roles(id),
                    agency_id INTEGER REFERENCES real_estate_agencies(id),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # LISTING CATEGORIES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listing_categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL
                );
            """)

            # LISTINGS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    living_area INTEGER NOT NULL,
                    rooms INTEGER NOT NULL,
                    address_id INTEGER NOT NULL REFERENCES addresses(id),
                    category_id INTEGER NOT NULL REFERENCES listing_categories(id),
                    agent_id INTEGER NOT NULL REFERENCES users(id),
                    agency_id INTEGER REFERENCES real_estate_agencies(id),
                    status VARCHAR(50) NOT NULL
                        CHECK (status IN ('active', 'upcoming', 'sold', 'archived')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # IMAGES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                    image_url TEXT NOT NULL,
                    description TEXT,
                    position INTEGER,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # BIDS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                    bidder_id INTEGER NOT NULL REFERENCES users(id),
                    amount INTEGER NOT NULL CHECK (amount > 0),
                    is_accepted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # FAVORITES
            cur.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (user_id, listing_id)
                );
            """)

            # VIEWINGS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS viewings (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                    start_time TIMESTAMPTZ NOT NULL,
                    end_time TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    CHECK (end_time IS NULL OR end_time > start_time)
                );
            """)

            # VIEWING REGISTRATIONS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS viewing_registrations (
                    id SERIAL PRIMARY KEY,
                    viewing_id INTEGER NOT NULL REFERENCES viewings(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (viewing_id, user_id)
                );
            """)

            # AGENT REVIEWS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agent_reviews (
                    id SERIAL PRIMARY KEY,
                    agent_id INTEGER NOT NULL REFERENCES users(id),
                    reviewer_id INTEGER NOT NULL REFERENCES users(id),
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    comment TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (agent_id, reviewer_id)
                );
            """)

    con.close()


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")