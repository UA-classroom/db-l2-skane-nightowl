import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",  # change if needed
        password=PASSWORD,
        host="localhost",  # change if needed
        port="5432",  # change if needed
    )


def create_tables():
    """
    A function to create the necessary tables for the project.
    """
    connection = get_connection()

    # USERS
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    role VARCHAR(50) NOT NULL,
                    permission VARCHAR(50),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # LOGINS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logins (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    ip_address VARCHAR(100)
                );
            """)

        #REAL ESTATE AGENCIES
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS real_estate_agencies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    address VARCHAR(255),
                    phone VARCHAR(50),
                    website VARCHAR(255)
                );
            """)
        
        #LISTING CATEGORIES
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listing_categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE
                );
            """)
        #LISTINGS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    price INTEGER,
                    area INTEGER,
                    rooms INTEGER,
                    address VARCHAR(255),
                    postal_code VARCHAR(20),
                    city VARCHAR(100),
                    category_id INTEGER NOT NULL REFERENCES listing_categories(id),
                    agent_id INTEGER NOT NULL REFERENCES users(id),
                    agency_id INTEGER NOT NULL REFERENCES real_estate_agencies(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # IMAGES
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id),
                    url TEXT NOT NULl
                );
            """)

        # BIDS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id),
                    bidder_id INTEGER NOT NULL REFERENCES users(id),
                    amount INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # FAVORITES (M2M)
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    listing_id INTEGER NOT NULL REFERENCES listings(id),
                    PRIMARY KEY (user_id, listing_id)
                );
            """)

        # VIEWINGS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS viewings (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id),
                    start_time TIMESTAMPTZ NOT NULL,
                    end_time TIMESTAMPTZ
                );
            """)
        
        # VIEWING REGISTRATIONS (M2M)
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS viewing_registrations (
                    id SERIAL PRIMARY KEY,
                    viewing_id INTEGER NOT NULL REFERENCES viewings(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # AGENT REVIEWS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_reviews (
                    id SERIAL PRIMARY KEY,
                    agent_id INTEGER NOT NULL REFERENCES users(id),
                    reviewer_id INTEGER NOT NULL REFERENCES users(id),
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # MESSAGES
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    sender_id INTEGER NOT NULL REFERENCES users(id),
                    receiver_id INTEGER NOT NULL REFERENCES users(id),
                    listing_id INTEGER REFERENCES listings(id),
                    content TEXT NOT NULL,
                    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        # SOLD LISTINGS
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sold_listings (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL UNIQUE REFERENCES listings(id),
                    sold_price INTEGER,
                    sold_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")