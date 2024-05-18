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
    query = "SELECT name, tiploc FROM train_data.stations"
    cursor.execute(query)

    # Fetch all rows from the executed query
    data = cursor.fetchall()

    # Separate the data into two lists: names and alpha3s
    names = [row[0] for row in data]
    alpha3s = [row[1] for row in data]

    cursor.close()
    connect.close()
   
    return names, alpha3s

def get_tiploc_by_name(station_name):
    connect = connect_to_db()
    cursor = connect.cursor()


    # Convert station_name to uppercase
    station_name = station_name.upper()

    # Prepare the query
    query = "SELECT tiploc FROM train_data.stations WHERE name = %s"
    cursor.execute(query, (station_name,))

    # Fetch the first row from the executed query
    data = cursor.fetchone()

    cursor.close()
    connect.close()

    # If data is not None, return the tiploc, otherwise return None
    return data[0] if data else None


# Gets all station names and codes and returns them in a tuple of two lists

def get_tpl_by_name(station_name):
    connect = connect_to_db()
    cursor = connect.cursor()


    # Convert station_name to uppercase
    station_name = station_name.upper()

    # Prepare the query
    query = "SELECT tpl FROM train_data.stations WHERE name = %s"
    cursor.execute(query, (station_name,))

    # Fetch the first row from the executed query
    data = cursor.fetchone()

    cursor.close()
    connect.close()

    # If data is not None, return the tiploc, otherwise return None
    return data[0] if data else None



if __name__ == "__main__":
    df = get_tpl_by_name("ACLE")
    print(df)
