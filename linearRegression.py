import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import os
from calendar import monthrange

def preprocess_data(file_paths):
    data = pd.DataFrame()  # Initialize data as an empty DataFrame

    for file_path in file_paths:
        if os.path.exists(file_path):  # Check if the file exists
            # Load the dataset
            temp_data = pd.read_csv(file_path)

            # Data preprocessing
            temp_data['arr_at'] = pd.to_datetime(temp_data['arr_at'], format='%H:%M').dt.hour * 60 + pd.to_datetime(temp_data['arr_at'], format='%H:%M').dt.minute
            temp_data['dep_at'] = pd.to_datetime(temp_data['dep_at'], format='%H:%M').dt.hour * 60 + pd.to_datetime(temp_data['dep_at'], format='%H:%M').dt.minute
            temp_data['scheduled_arrival'] = pd.to_datetime(temp_data['pta'], format='%H:%M', errors='coerce').dt.hour * 60 + pd.to_datetime(temp_data['pta'], format='%H:%M', errors='coerce').dt.minute
            temp_data['delay'] = temp_data['arr_at'] - temp_data['scheduled_arrival']

            # Create 'hour_of_day' column
            temp_data['hour_of_day'] = temp_data['scheduled_arrival'] // 60

            # Handle missing values
            # Drop rows with NaN values in 'hour_of_day' and 'delay' columns
            temp_data.dropna(subset=['hour_of_day', 'delay'], inplace=True)

            data = pd.concat([data, temp_data], ignore_index=True)

    # Prepare the training dataset
    X = data[['hour_of_day']]  # You can add more features
    y = data['delay']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    return X_train, X_test, y_train, y_test
def linear_regression(X_train, X_test, y_train, y_test):
    # Model Training
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict on the test set
    predictions = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    print(f'Linear Regression - Root Mean Squared Error: {rmse}')

def knn(X_train, X_test, y_train, y_test):
    # Model Training
    model = KNeighborsRegressor()
    model.fit(X_train, y_train)

    # Predict on the test set
    predictions = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    print(f'K-Nearest Neighbors - Root Mean Squared Error: {rmse}')




# Generate file paths
file_paths = []
base_path = "/Users/mac/Desktop/Chatbot/assets/data/LIVST_NRCH_OD_a51_{}"

for year in ['2022', '2021', '2020', '2019', '2018', '2017']:
    for month in range(1, 13):
        _, num_days = monthrange(int(year), month)  # Get the number of days in the month
        for day in range(1, num_days + 1):  # Iterate over each day in the month
            file_path = f"{base_path.format(year)}/LIVST_NRCH_OD_a51_{year}_{month:02}_{day:02}.csv"
             # Check if the file path exists
            
            if os.path.exists(file_path):  # Print the file path
                file_paths.append(file_path)

# Convert list to set to remove duplicates, then convert back to list
file_paths = list(set(file_paths))


X_train, X_test, y_train, y_test = preprocess_data(file_paths)


print(len(file_paths))

linear_regression(X_train, X_test, y_train, y_test)
knn(X_train, X_test, y_train, y_test)

#