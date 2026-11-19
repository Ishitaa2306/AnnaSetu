import psycopg
import getpass

password = getpass.getpass("Enter PostgreSQL password: ")

try:
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="hackathon_db",
        user="postgres",
        password=password
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user;"
            )

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError("No database result returned.")

            print("\nDatabase connection successful!")
            print("Database:", result[0])
            print("User:", result[1])

except Exception as error:
    print("\nDatabase connection failed:", error)