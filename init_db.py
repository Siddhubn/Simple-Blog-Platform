import sqlite3

# Function to create tables in the database
def init_db():
    conn = sqlite3.connect('database.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Call the function to initialize the database
if __name__ == "__main__":
    init_db()
