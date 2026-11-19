import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

# Read database settings
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(database_url)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        ).fetchone()

        if result is None:
            raise RuntimeError("No database result returned.")

        print("SQLAlchemy connection successful!")
        print("Database:", result[0])
        print("User:", result[1])

except Exception as error:
    print("Connection failed:", error)

finally:
    engine.dispose()