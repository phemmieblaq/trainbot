# Importing data to db from python because I don't have admin permission
import pandas as pd
from sqlalchemy import create_engine
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
engine = create_engine(connection_string)

# Load CSV data into DataFrame
# Load CSV data into DataFrame
df = pd.read_csv('/Users/mac/Desktop/Chatbot/assets/data/stations.csv',index_col=False)
print(df.iloc[:, 0])

# Debug to check if DataFrame columns match the database table columns
print(df.columns)  # Now it should match ['name', 'longname_name_alias', 'alpha3', 'tiploc']

# Insert data into the database
df.to_sql('stations', con=engine, schema='train_data', if_exists='append', index=False)

# Close the connection
engine.dispose()