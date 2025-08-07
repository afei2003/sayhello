import pandas as pd
from sqlalchemy import create_engine, inspect
import urllib

# --- MSSQL Configuration ---
SERVER = "192.168.100.88"
DATABASE = "test"
USERNAME = "sa"
PASSWORD = "abc123..."
TABLE_NAME = "user"

# Connection string for pyodbc
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
)
ENGINE = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


def setup_database():
    """
    Sets up the database, creating the table and populating it with
    initial data if it doesn't exist.
    """
    inspector = inspect(ENGINE)
    if not inspector.has_table(TABLE_NAME):
        print(f"Table '{TABLE_NAME}' not found. Creating and populating it.")
        data = {
            "id": [1, 2, 3, 4],
            "username": ["admin", "guest", "user1", "user2"],
            "nickname": ["Administrator", "Guest User", "First User", "Second User"],
            "note": ["System admin", "Limited access", "Regular user", "Regular user"],
        }
        df = pd.DataFrame(data)
        # For MSSQL, it's often better to let the database handle the primary key.
        # We will set 'id' as the index and let the database create it.
        df.set_index("id", inplace=True)
        df.to_sql(TABLE_NAME, ENGINE, index=True, index_label='id')
    else:
        print(f"Table '{TABLE_NAME}' already exists.")


def load_data():
    """Loads the data from the database into a pandas DataFrame."""
    return pd.read_sql(f"SELECT * FROM {TABLE_NAME}", ENGINE, index_col="id")


def save_data(df):
    """Saves the DataFrame back to the database."""
    # Using 'replace' can be risky. A more robust solution would be to
    # update existing records and insert new ones. But for this example,
    # we will stick to a simple replace.
    df.to_sql(TABLE_NAME, ENGINE, if_exists="replace", index=True, index_label='id')


if __name__ == "__main__":
    try:
        setup_database()
        print("Database setup complete.")
        df = load_data()
        print("Initial data:")
        print(df)
    except Exception as e:
        print(f"An error occurred: {e}")
