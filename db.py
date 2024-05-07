from dotenv import load_dotenv
import psycopg2
import os
import pandas as pd
from typing import List, Tuple

# Load .env file with PostgreSQL details
load_dotenv()

# Function to create a database connection
def connect_to_db():
    connect = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_DATABASE"),
        port=os.environ.get("DB_PORT"),
    )
    return connect

# Get all train station data
def get_train_station_data():
    connect = connect_to_db()
    cursor = connect.cursor()

    # Fetch only 'name' and 'alpha3' from stations table in train_data schema
    query = "SELECT name, alpha3 FROM train_data.stations"
    cursor.execute(query)

    # Fetch all rows from the executed query
    data = cursor.fetchall()

    # Separate the data into two lists: names and alpha3s
    names = [row[0] for row in data]
    alpha3s = [row[1] for row in data]

    cursor.close()
    connect.close()
   
    return names, alpha3s



# Gets all station names and codes and returns them in a tuple of two lists



# if __name__ == "__main__":
#     df = get_train_station_data()
#     print(df)