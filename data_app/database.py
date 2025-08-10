import pandas as pd
from sqlalchemy import create_engine, inspect
import urllib

# --- MSSQL Configuration ---
SERVER = "192.168.100.88"
DATABASE = "test"
USERNAME = "sa"
PASSWORD = "abc123..."
TABLE_NAME = "`user`" # Use backticks for safety as user is a keyword

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
    # The table name in has_table should not have quotes
    if not inspector.has_table(TABLE_NAME.strip('`')):
        print(f"Table {TABLE_NAME} not found. Creating and populating it.")
        data = {
            "id": [1, 2, 3, 4],
            "username": ["admin", "guest", "user1", "user2"],
            "nickname": ["Administrator", "Guest User", "First User", "Second User"],
            "note": ["System admin", "Limited access", "Regular user", "Regular user"],
        }
        df = pd.DataFrame(data)
        # id is now a regular column, so index=False is correct.
        df.to_sql(TABLE_NAME.strip('`'), ENGINE, index=False, if_exists='replace')
    else:
        print(f"Table {TABLE_NAME} already exists.")


def load_data():
    """Loads the data from the database into a pandas DataFrame."""
    # id is now a regular column
    return pd.read_sql(f"SELECT * FROM {TABLE_NAME}", ENGINE)


from sqlalchemy import text

def save_data(df):
    """
    Saves the DataFrame back to the database using a MERGE statement
    to handle inserts, updates, and deletes.
    """
    temp_table_name = f"temp_{TABLE_NAME.strip('`')}"
    target_table = TABLE_NAME.strip('`')

    # Make a copy to avoid modifying the original DataFrame in the model
    df_to_save = df.copy()

    # Ensure the 'id' column is a nullable integer type for the database
    df_to_save['id'] = pd.to_numeric(df_to_save['id'], errors='coerce').astype('Int64')

    with ENGINE.begin() as connection:
        # Step 1: Upload the current data to a temporary table
        df_to_save.to_sql(temp_table_name, connection, if_exists='replace', index=False)

        # Step 2: Construct and execute the MERGE statement
        cols_for_insert = [col for col in df_to_save.columns if col != 'id']
        cols_for_update = [f"target.{col} = source.{col}" for col in cols_for_insert]

        merge_sql = text(f"""
        MERGE {target_table} AS target
        USING {temp_table_name} AS source
        ON (target.id = source.id)

        -- For updating existing records that have changed
        WHEN MATCHED AND ({' OR '.join([f'target.{c} <> source.{c}' for c in cols_for_insert if df_to_save[c].dtype != 'object'] + [f'ISNULL(target.{c}, \'\') <> ISNULL(source.{c}, \'\')' for c in cols_for_insert if df_to_save[c].dtype == 'object'])}) THEN
            UPDATE SET {', '.join(cols_for_update)}

        -- For inserting new records
        WHEN NOT MATCHED BY TARGET THEN
            INSERT ({', '.join(cols_for_insert)})
            VALUES ({', '.join([f'source.{c}' for c in cols_for_insert])})

        -- For deleting records that are no longer in the dataframe
        WHEN NOT MATCHED BY SOURCE THEN
            DELETE;
        """)

        connection.execute(merge_sql)


if __name__ == "__main__":
    try:
        setup_database()
        print("Database setup complete.")
        df = load_data()
        print("Initial data:")
        print(df)
    except Exception as e:
        print(f"An error occurred: {e}")
