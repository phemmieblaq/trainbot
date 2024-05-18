import spacy

from experta import KnowledgeEngine, Rule, Fact
import re
import asyncio
from playwright.async_api import Playwright
from scrape import TrainScrapeTicketBot
from returnScraper import TrainReturnScrapeTicketBot
from utils import convert_date_format,determine_time_format
from db import get_tiploc_by_name
 

import pandas as pd
from playwright.async_api import async_playwright

from patterns import get_entities,yes_pattern


# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


class TrainTicketBot(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.leavingHour = None
        self.leavingMinute = None
        self.arrivalHour = None
        self.arrivalMinute = None
        self.user_responses = {
    'singlejourney': {'service': None,'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None},
    'returnJourney': {'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None}
}   
        self.delay_responses = {}
    async def run_scrape_bot(self, origin: str, originCode: str, destination: str, destinationCode: str, date: str, hour: str, minute: str):
        scrape_bot = TrainScrapeTicketBot()
        async with async_playwright() as playwright:
            await scrape_bot.run(playwright, origin, originCode, destination, destinationCode, date, hour, minute)

     
    async def run_return_scrape_bot(self, origin: str, originCode: str, destination: str, destinationCode: str, leavingDate: str, leavingHour: str, leavingMinute: str,arrivalDate: str, arrivalHour: str, arrivalMinute: str):
        scrape_bot = TrainReturnScrapeTicketBot()
        async with async_playwright() as playwright:
            await scrape_bot.run(playwright, origin, originCode, destination, destinationCode, leavingDate, leavingHour, leavingMinute, arrivalDate, arrivalMinute, arrivalHour)

    

    @Rule(Fact(action='greet'))
    def greet(self):
        service_input = input("Hello! Welcome to FareFinder. I'm here to help you find the most affordable train tickets, train delays and blocked lines.  What service would you like? Let's get started!")
        service_entities = get_entities({'message': service_input})
        service = service_entities['singleJourney'].get('service')
        self.user_responses['singlejourney']['service'] = service
        if service in ['travel', 'book', 'booking']:
            self.declare(Fact(action='ask_service'))
        elif service in ['delay', 'predictions', 'delays']:
            self.declare(Fact(action='query_delay'))

        else:
            print("Sorry, I didn't get that. Please try again.")
            self.declare(Fact(action='greet'))
            run_bot()
            

    @Rule(Fact(action='ask_service'))
    def ask_service(self):
        journey_details = input("Please provide your journey details:")
        entities = get_entities({'message': journey_details})
        #print(entities)
        if 'singleJourney' in entities:
            self.user_responses['singlejourney'].update(entities['singleJourney'])
        if 'returnJourney' in entities:
            self.user_responses['returnJourney'].update(entities['returnJourney'])
        
        singleJourneyFromCity = entities['singleJourney'].get('fromCity')
        arrivingAtCity = entities['singleJourney'].get('toCity')
        date = entities['singleJourney'].get('fullDate')
        time =  entities['singleJourney'].get('time')

       
        print (date)
        print (time)
        

        #modifiedTime =  entities['singleJourney'].get('timeModifier')
       
        while True and not singleJourneyFromCity:
            singleJourneyFromCity = input("Please enter the valid city you departing from  ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message': 'to ' + singleJourneyFromCity})
            singleJourneyFromCity = entities['singleJourney'].get('toCity')

            # If get_entities returns an empty result, ask the user to try again
            if not singleJourneyFromCity:
                print("Invalid city. Please try again.")
                continue

            # Save the city and exit the loop
            self.user_responses['singlejourney']['fromCity'] = singleJourneyFromCity
            break




        while True and not arrivingAtCity:
            arrivingAtCity = input("Please enter the valid city you are arriving at ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message': 'to ' + arrivingAtCity})
            arrivingAtCity = entities['singleJourney'].get('toCity')

            # If get_entities returns an empty result, ask the user to try again
            if not arrivingAtCity:
                print("Invalid city. Please try again.")
                continue

            # Save the city and exit the loop
            self.user_responses['singlejourney']['toCity'] = arrivingAtCity
            break



        while True and not date:
            date = input(f"Please enter the date you will be departing  { (self.user_responses['singlejourney']['fromCity'] or '').replace('from ', '', 1)}")
            # Update the entities dictionary with the new input
            entities = get_entities({'message':   date})
            date = entities['singleJourney'].get('fullDate')

            # If get_entities returns an empty result, ask the user to try again
            if not date:
                print("Invalid date. Please try again.")
                continue

            # Save the city and exit the loop
            self.user_responses['singlejourney']['fullDate'] = date
            break

        while True and not time:
            time = input(f"Please enter the time you are leaving  { (self.user_responses['singlejourney']['fromCity'] or '').replace('from ', '', 1)} ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message':   time})
            time = entities['singleJourney'].get('time')

            # If get_entities returns an empty result, ask the user to try again
            if not time:
                print("Invalid time. Please enter time in 12hours format(1am or 1pm) or 24 hours format(23:00 or 1:00).")
                continue

            # Determine the time format and parse the time
            result = determine_time_format(time)
            if result[0] == 'Invalid format':
                print("Invalid time format. Please enter time in 12-hour (e.g., '1:00 PM') or 24-hour (e.g., '13:00') format.")
                continue

            # Save the city and exit the loop
            self.user_responses['singlejourney']['time'] = time

            break

        
        # Declaring variable to 
        # Remove 'from ' from 'fromCity' and 'to ' from 'toCity'
        from_city = None
        to_city = None

        if self.user_responses['singlejourney']['fromCity']:
            from_city = self.user_responses['singlejourney']['fromCity'].replace('from ', '', 1)
            self.user_responses['singlejourney']['fromCity'] = from_city

        if self.user_responses['singlejourney']['toCity']:
            to_city = self.user_responses['singlejourney']['toCity'].replace('to ', '', 1)
            self.user_responses['singlejourney']['toCity'] = to_city

        if self.user_responses['singlejourney']['fullDate']:
            fullDate = self.user_responses['singlejourney']['fullDate']
            leavingDate = convert_date_format(fullDate)
            self.user_responses['singlejourney']['fullDate'] = leavingDate

            print(leavingDate)

        if self.user_responses['singlejourney']['time']:
            time_string = self.user_responses['singlejourney']['time']
            result = determine_time_format(time_string)
            if result[0] == 'Invalid format':
                print("Invalid time format. Please enter time in 12-hour (e.g., '1:00 PM') or 24-hour (e.g., '13:00') format.")
            else:
                self.leavingHour, self.leavingMinute = str(result[1]), str(result[2])
            if int(self.leavingMinute) < 15:
                self.leavingMinute = '00'
            elif int(self.leavingMinute) < 30:
                self.leavingMinute = '15'
            elif int(self.leavingMinute) < 45:
                self.leavingMinute = '30'
            else:
                self.leavingMinute = '45'
                    

                

        print(f"{self.user_responses['singlejourney']['fullDate']}, i will getting your single cheapest ticket from {from_city} to {to_city} around {self.user_responses['singlejourney']['time']}")
        #getting code from db 
        originCode = get_tiploc_by_name(from_city) 
        destinationCode = get_tiploc_by_name(to_city)

      
    
                
        #asyncio.run(self.run_scrape_bot())
        #After collecting all details, run the scrape bot
                #asyncio.run(self.run_scrape_bot())
                # Your code for return journey details here

        

           

        if all(value is None for value in self.user_responses['returnJourney'].values()):

        
            return_ticket = input("Do you want a return ticket?")

            # Get the regex pattern from yes_pattern
            yes_regex = yes_pattern[0]['LOWER']['REGEX']
            if not re.match(yes_regex, return_ticket, re.IGNORECASE):
                   asyncio.run(self.run_scrape_bot(from_city, originCode, to_city,destinationCode, leavingDate, self.leavingHour, self.leavingMinute))

            # If the user wants a return ticket, proceed with the return journey details
            if re.match(yes_regex, return_ticket, re.IGNORECASE):
                self.user_responses['returnJourney']['fromCity'] = self.user_responses['singlejourney']['toCity']
                self.user_responses['returnJourney']['toCity'] = self.user_responses['singlejourney']['fromCity']

                print(f"Great! You are returning from {self.user_responses['returnJourney']['fromCity']} to {self.user_responses['returnJourney']['toCity']}")
                returnDate = self.user_responses['returnJourney'].get('fullDate')


                while True and not returnDate:
                    returnDate = input(f"Please enter the date you will be returning  { (self.user_responses['returnJourney']['fromCity'] or '').replace('from ', '', 1)}")
                    # Update the entities dictionary with the new input
                    entities = get_entities({'message':   returnDate})
                    print(entities)
                    returnDate = entities['singleJourney'].get('fullDate')

                    # If get_entities returns an empty result, ask the user to try again
                    if not returnDate:
                        print("Invalid date. Please try again.")
                        continue

                    # Save the date and exit the loop
                    self.user_responses['returnJourney']['fullDate'] = returnDate
                    break

                returnTime = self.user_responses['returnJourney'].get('time')

                while True and not returnTime:
                    returnTime = input(f"Please enter the time you are returning  { (self.user_responses['returnJourney']['fromCity'] or '').replace('from ', '', 1)} ")
                    # Update the entities dictionary with the new input
                    entities = get_entities({'message':   returnTime})
                    returnTime = entities['singleJourney'].get('time')

                    # If get_entities returns an empty result, ask the user to try again
                    if not returnTime:
                        print("Invalid time. Please try again.")
                        continue

                    # Save the time and exit the loop
                    self.user_responses['returnJourney']['time'] = returnTime
                    break

                print(self.user_responses)

                if self.user_responses['returnJourney']['fullDate']:
                    fullDate = self.user_responses['returnJourney']['fullDate']
                    arrivalDate = convert_date_format(fullDate)
                    self.user_responses['returnJourney']['fullDate'] = arrivalDate

                    print(arrivalDate)

                if self.user_responses['returnJourney']['time']:
                    time_string = self.user_responses['returnJourney']['time']
                    result = determine_time_format(time_string)
                    if result[0] == 'Invalid format':
                        print("Invalid time format. Please enter time in 12-hour (e.g., '1:00 PM') or 24-hour (e.g., '13:00') format.")
                    else:
                        self.arrivalHour, self.arrivalMinute = str(result[1]), str(result[2])
                        print("arrivalHour", self.arrivalHour)
                        print("arrivalMinute", self.arrivalMinute)
                    if int(self.arrivalMinute) < 15:
                        self.arrivalMinute = '00'
                    elif int(self.arrivalMinute) < 30:
                        self.arrivalMinute = '15'
                    elif int(self.arrivalMinute) < 45:
                        self.arrivalMinute = '30'
                    else:
                        self.arrivalMinute = '45'
                            


                

                asyncio.run(self.run_return_scrape_bot(from_city, originCode, to_city,destinationCode, leavingDate, self.leavingHour, self.leavingMinute,arrivalDate,  self.arrivalHour, self.arrivalMinute))

                # After collecting all details, run the scrape bot
                #asyncio.run(self.run_scrape_bot())
                # Your code for return journey details here

    @Rule(Fact(action='query_delay'))
    def delay_service(self):
        current_location = input("Where is the train now? ")
        delay_time = input("How much time has the train been delayed? ")
        destination = input("Where is your destination? ")

        # Use the gathered information to predict the arrival time
        # This is a placeholder, replace it with your actual prediction logic
        #predicted_arrival_time = predict_arrival_time(train, current_location, delay_time, destination)

        #print(f"The predicted arrival time at {destination} is {predicted_arrival_time}.")



        



       
       
        
    
# Main function to run the bot
def run_bot():
    bot = TrainTicketBot()
    bot.reset()
    bot.declare(Fact(action='greet'))  # Fixed the missing function call
    bot.run()
    #asyncio.run(bot.run_scrape_bot())

if __name__ == "__main__":
    run_bot()
