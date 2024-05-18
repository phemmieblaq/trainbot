import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')

# Connection string
connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
engine = create_engine(connection_string, echo=True)

# Load CSV data into DataFrame
df = pd.read_csv('/Users/mac/Desktop/Chatbot/assets/data/stations.csv')

# Handle missing values correctly without chained assignment
df['tiploc'] = df['tiploc'].fillna('')

# Ensure no duplicates in primary and unique key columns
df.drop_duplicates(subset=['tiploc'], inplace=True)

# Check if 'tpl' column exists; if not, create it by copying 'tiploc'
if 'tpl' not in df.columns:
    df['tpl'] = df['tiploc']

# Replace '\N' with None
df.replace('\\N', None, inplace=True)

# Rename DataFrame columns to match the SQLAlchemy model and your database table
df.rename(columns={
    'name': 'name',
    'longname_name_alias': 'longname_name_alias',
    'alpha3': 'alpha3',
    'tiploc': 'tiploc',
    'tpl': 'tpl'
}, inplace=True)

# Drop rows with None in 'name', 'tiploc', and 'tpl' columns (required columns)
df.dropna(subset=['name', 'tiploc', 'tpl'], inplace=True)

# Debug to check if DataFrame columns match after renaming
print("DataFrame columns after renaming:")
for col in df.columns:
    print(f"'{col}'")

# Check if DataFrame is not empty
if df.empty:
    print("DataFrame is empty after cleaning, nothing to insert.")
else:
    print(f"DataFrame has {len(df)} rows to insert after cleaning.")

# Manual insertion query
insert_query = text("""
    INSERT INTO train_data.delStations (name, longname_name_alias, alpha3, tiploc, tpl)
    VALUES (:name, :longname_name_alias, :alpha3, :tiploc, :tpl)
""")

# Insert rows individually to capture detailed errors and commit explicitly
try:
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        print(f"Inserting row {index}: {row_dict}")
        try:
            with engine.connect() as connection:
                with connection.begin():
                    connection.execute(insert_query, row_dict)
                    print(f"Row {index} inserted successfully.")
        except Exception as e:
            print(f"Error inserting row {index}: {e}")
            # Continue to next row on error
finally:
    # Verify final row count
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM train_data.delStations"))
            count = result.fetchone()[0]
            print(f"Number of rows in 'delStations': {count}")
    except Exception as e:
        print(f"Error verifying final row count: {e}")

# Close the connection
engine.dispose()
