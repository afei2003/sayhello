import pandas as pd
from sqlalchemy import create_engine, inspect

DB_FILE = "sample.db"
TABLE_NAME = "employees"
ENGINE = create_engine(f"sqlite:///{DB_FILE}")

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
            "name": ["Alice", "Bob", "Charlie", "David"],
            "role": ["Engineer", "Artist", "Teacher", "Doctor"],
            "salary": [70000, 60000, 50000, 90000],
        }
        df = pd.DataFrame(data)
        df.to_sql(TABLE_NAME, ENGINE, index=False)
    else:
        print(f"Table '{TABLE_NAME}' already exists.")

def load_data():
    """Loads the data from the database into a pandas DataFrame."""
    return pd.read_sql(f"SELECT * FROM {TABLE_NAME}", ENGINE, index_col="id")

def save_data(df):
    """Saves the DataFrame back to the database."""
    df.to_sql(TABLE_NAME, ENGINE, if_exists="replace", index=True)

if __name__ == "__main__":
    setup_database()
    print("Database setup complete.")
    df = load_data()
    print("Initial data:")
    print(df)
