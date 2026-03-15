import psycopg2 
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",   # 👈 MUST be car_rental
        user="postgres",
        password="Toughluck@2015"
    )
