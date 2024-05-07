import spacy
from experta import KnowledgeEngine, Rule, Fact

import pandas as pd

from patterns import get_entities

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

class TrainTicketBot(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.user_responses = {
    'singlejourney': {'service': None,'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None},
    'returnJourney': {'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None}
}
  

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
        modifiedTime =  entities['singleJourney'].get('timeModifier')
        while True and not singleJourneyFromCity:
            singleJourneyFromCity = input("Please enter the valid city you are departing from ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message': 'from ' + singleJourneyFromCity})
            #print(f"Entities: {entities}")
            extractedCity = entities['singleJourney'].get('fromCity')

            # If get_entities returns an empty result, ask the user to try again
            if not extractedCity:
                print("Invalid city. Please try again.")
                continue

            # Strip 'from ' from the start of extractedCity
            if extractedCity.startswith('from '):
                singleJourneyFromCity = extractedCity[5:]
                self.user_responses['singlejourney']['toCity'] = singleJourneyFromCity
                #print(f"Valid city entered: {singleJourneyFromCity}")
                break # Break the loop

            print("Invalid city. Please try again.")



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
            self.user_responses['singlejourney']['date'] = date
            break

        while True and not time:
            time = input(f"Please enter the time you are leaving  { (self.user_responses['singlejourney']['fromCity'] or '').replace('from ', '', 1)} ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message':   time})
            time = entities['singleJourney'].get('time')

            # If get_entities returns an empty result, ask the user to try again
            if not time:
                print("Invalid time. Please try again.")
                continue

            # Save the city and exit the loop
            self.user_responses['singlejourney']['time'] = time
           
            break
        while True and not returnJourneyFromCity:
            returnJourneyFromCity = input("Please enter the valid city you are returning from ")
            # Update the entities dictionary with the new input
            entities = get_entities({'message': 'from ' + returnJourneyFromCity})
            extractedCity = entities['returnJourney'].get('fromCity')

            # If get_entities returns an empty result, ask the user to try again
            if not extractedCity:
                print("Invalid city. Please try again.")
                continue

            # Strip 'from ' from the start of extractedCity
            if extractedCity.startswith('from '):
                returnJourneyFromCity = extractedCity[5:]
                self.user_responses['returnJourney']['fromCity'] = returnJourneyFromCity
                break # Break the loop

            print("Invalid city. Please try again.")

        



       
       
        
    
# Main function to run the bot
def run_bot():
    bot = TrainTicketBot()
    bot.reset()
    bot.declare(Fact(action='greet'))  # Fixed the missing function call
    bot.run()

if __name__ == "__main__":
    run_bot()
