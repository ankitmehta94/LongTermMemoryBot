import psycopg2
import json
import os

# Database connection details
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')
DB_HOST = "db"
DB_PORT = 5432

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

print('This is the db connection')
print(conn)

# Function to add a new transcription


def add_transcription(transcription, user_id, transcription_type=None):
    # Prepare SQL statement to insert a new row
    insert_statement = """
        INSERT INTO Transcriptions (transcription, user_id, transcription_type)
        VALUES (%s, %s, %s)
        RETURNING id;
    """

    # Execute SQL statement with provided data
    cur = conn.cursor()
    cur.execute(insert_statement, (transcription, user_id, transcription_type))
    row_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    # Return the ID of the new row
    return row_id

# Function to get a transcription by ID


def get_transcription(transcription_id):
    # Prepare SQL statement to retrieve row by ID
    select_statement = """
        SELECT id, transcription, user_id, transcription_type
        FROM Transcriptions
        WHERE id = %s;
    """

    # Execute SQL statement with provided ID
    cur = conn.cursor()
    cur.execute(select_statement, (transcription_id,))
    row = cur.fetchone()
    cur.close()

    # If no row was found, return None
    if row is None:
        return None

    # Otherwise, return row data as a JSON object
    return json.dumps({
        "id": row[0],
        "transcription": row[1],
        "user_id": row[2],
        "transcription_type": row[3]
    })
