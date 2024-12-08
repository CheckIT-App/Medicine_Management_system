import psycopg2

print(psycopg2.__file__)

try:
    conn = psycopg2.connect(
        dbname="medicine_management",
        user="postgres",
        password="manage1234",
        host="localhost",
        port="5432"
    )
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")