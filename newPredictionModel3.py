import sys
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
from sklearn.metrics import mean_squared_error
from difflib import SequenceMatcher


class Predictions:
    def __init__(self):
        self.stations = {
            "norwich": "NRCH",
            "diss": "DISS",
            "stowmarket": "STWMRKT",
            "ipswich": "IPSWICH",
            "manningtree": "MANNGTR",
            "colchester": "CLCHSTR",
            "witham": "WITHAME",
            "chelmsford": "CHLMSFD",
            "ingatestone": "INT",
            "shenfield": "SHENFLD",
            "stanford": "STFD",
            "stanford-le-hope": "STFD",
            "london liverpool street": "LIVST",
            "london liverpool st": "LIVST",
            "liverpool street": "LIVST"
        }
        self.segment_of_day = None
        self.rush_hour = None
        self.day_of_week = datetime.today().weekday()
        self.weekend = self.is_weekend(self.day_of_week)
        self.departure_station = None
        self.arrival_station = None
        self.exp_dep = None
        self.delay = None

    def station_finder(self, station):
        x = station.lower()
        if x in self.stations:
            return self.stations[x]
        else:
            for s in self.stations:
                ratio = SequenceMatcher(None, x, s).ratio() * 100
                if ratio >= 60:
                    similar = s
                    print(f"The city you've provided has not been found. Closest match to {station} is: {s.upper()}")
                    return self.stations[similar]
            raise Exception(f"No similar cities to {station} have been found. Please type the station again.")

    def harvest_data(self):
        df = pd.read_csv('assets/data/combined_Dataset.csv', usecols=['rid', 'tpl', 'ptd', 'dep_at', 'pta', 'arr_at'])
        df_depart = df[df['tpl'] == self.departure_station]
        df_arrive = df[df['tpl'] == self.arrival_station]
        merged_df = pd.merge(df_depart, df_arrive, on='rid', suffixes=('_FROM', '_TO'))

        return merged_df

    @staticmethod
    def convert_time(time):
        hh = int(time[0] / 3600)
        mm = int((time[0] % 3600) / 60)
        ss = int(time[0] % 60)
        return [hh, mm, ss]

    @staticmethod
    def is_weekend(day):
        return 1 if day >= 5 else 0

    @staticmethod
    def check_day_segment(hour_of_day):
        if 5 <= hour_of_day < 10:
            return 1
        elif 10 <= hour_of_day < 15:
            return 2
        elif 15 <= hour_of_day < 20:
            return 3
        else:
            return 4

    @staticmethod
    def is_rush_hour(hour, minute):
        if (5 <= hour < 10) or (16 <= hour < 19):
            return 1
        return 0

    @staticmethod
    def is_valid_date(date_string):
        try:
            datetime.strptime(date_string, '%Y%m%d')
            return True
        except ValueError:
            return False

    def prepare_datasets(self):
        result = self.harvest_data()
        data = []

        for _, row in result.iterrows():
            if (pd.notnull(row['ptd_FROM']) and pd.notnull(row['dep_at_FROM']) and
                pd.notnull(row['pta_TO']) and pd.notnull(row['arr_at_TO']) and
                isinstance(row['dep_at_FROM'], str) and isinstance(row['arr_at_TO'], str)):

                rid = str(row['rid'])
                if not self.is_valid_date(rid[:8]):
                    print(f"Invalid date in RID: {rid}")
                    continue

                try:
                    day_of_week = datetime(int(rid[:4]), int(rid[4:6]), int(rid[6:8])).weekday()
                except ValueError as e:
                    print(f"Error converting RID to date: {rid} -> {e}")
                    continue

                try:
                    hour_of_day = int(row['dep_at_FROM'].split(":")[0])
                    minute_of_day = int(row['dep_at_FROM'].split(":")[1])
                except (ValueError, AttributeError) as e:
                    print(f"Error processing time: {row['dep_at_FROM']} -> {e}")
                    continue

                weekend = self.is_weekend(day_of_week)
                day_segment = self.check_day_segment(hour_of_day)
                rush_hour = self.is_rush_hour(hour_of_day, minute_of_day)

                try:
                    time_dep = (datetime.strptime(row['dep_at_FROM'], '%H:%M') - datetime(1900, 1, 1)).total_seconds()
                except ValueError as e:
                    print(f"Unable to get time_dep: {row['dep_at_FROM']} -> {e}")
                    continue

                try:
                    journey_delay = ((datetime.strptime(row['dep_at_FROM'], '%H:%M') - datetime(1900, 1, 1)).total_seconds() -
                                     (datetime.strptime(row['ptd_FROM'], '%H:%M') - datetime(1900, 1, 1)).total_seconds())
                except ValueError as e:
                    print(f"Unable to get journey_delay: {row['dep_at_FROM']}, {row['ptd_FROM']} -> {e}")
                    continue

                try:
                    time_arr = ((datetime.strptime(row['arr_at_TO'], '%H:%M') - datetime(1900, 1, 1)).total_seconds() -
                                (datetime.strptime(row['pta_TO'], '%H:%M') - datetime(1900, 1, 1)).total_seconds())
                except ValueError as e:
                    print(f"Unable to get time_arrival: {row['arr_at_TO']}, {row['pta_TO']} -> {e}")
                    continue

                data.append([rid, time_dep, journey_delay, day_of_week, weekend, day_segment, rush_hour, time_arr])

        return data

    def predict(self, data):
        if not data:
            raise ValueError("No valid data available for prediction.")

        dep_time_s = (datetime.strptime(self.exp_dep, '%H:%M') - datetime(1900, 1, 1)).total_seconds()
        delay_s = int(self.delay) * 60
        journeys = pd.DataFrame(data, columns=["rid", "time_dep", "delay", "day_of_week", "weekend", "day_segment", "rush_hour", "arrival_time"])

        X = journeys.drop(['rid', 'arrival_time'], axis=1)
        y = journeys['arrival_time'].values
        
        clf = RandomForestRegressor(n_estimators=100)
        clf.fit(X, y)

        prediction = clf.predict([[dep_time_s, delay_s, self.day_of_week, self.weekend, self.segment_of_day, self.rush_hour]])
        
        prediction = self.convert_time(prediction)

        return prediction, clf, X, y

    def display_results(self, from_st, to_st, exp_dep, delay):
        self.departure_station = self.station_finder(from_st)
        self.arrival_station = self.station_finder(to_st)
        self.exp_dep = exp_dep
        hour_of_day = int(exp_dep.split(":")[0])
        minute_of_day = int(exp_dep.split(":")[1])
        self.delay = delay
        self.segment_of_day = self.check_day_segment(hour_of_day)
        self.rush_hour = self.is_rush_hour(hour_of_day, minute_of_day)

        data = self.prepare_datasets()
        if not data:
            return "No valid data available to make a prediction."
        
        prediction, clf, X, y = self.predict(data)
        
        return f"Your total journey will likely be delayed for {str(prediction[1]).zfill(2)} minutes and {str(prediction[2]).zfill(2)} seconds."

# Example usage
#pr = Predictions()
#a = pr.display_results("liver london street ", "norwich", "17:30", "10")
#print(a)
