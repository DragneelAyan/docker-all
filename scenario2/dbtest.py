import psycopg2
print("Attempting connection...")

conn = psycopg2.connect(
    host="mydb",       # this will FAIL inside container
    port=5432,
    dbname="postgres",
    user="postgres",
    password="pass"
)

print("Connected successfully!")
