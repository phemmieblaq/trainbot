#importing data to db from python because i dont have admin permission


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
df = pd.read_csv('/Users/mac/Desktop/Chatbot/assets/data/stations.csv')

# Rename DataFrame columns to match the SQLAlchemy model and your database table
df.rename(columns={
    'column1': 'name',                # Assuming 'column1' in CSV is 'name' in DB
    'longname.name_alias': 'alias',  # Assuming this typo is in your actual CSV file header
    'column3': 'alpha3',              # Assuming 'column3' in CSV is 'alpha3' in DB
    'column4': 'tiploc'               # Assuming 'column4' in CSV is 'tiploc' in DB
}, inplace=True)

# If your CSV does not have a 'tpl' column, you need to create it or derive it somehow
# For the purpose of this example, I'm copying the 'tiploc' into 'tpl'
df['tpl'] = df['tiploc'] 

# Debug to check if DataFrame columns match after renaming
print(df.columns)  # Now it should match ['name', 'alias', 'alpha3', 'tiploc', 'tpl']

# Insert data into the database
df.to_sql('stations', con=engine, schema='train_data', if_exists='append', index=False)

# Close the connection
engine.dispose()
