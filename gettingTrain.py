import spacy
from experta import KnowledgeEngine, Rule, Fact, W
from dotenv import load_dotenv
import psycopg2
import os
import pandas as pd
from factDefinitions import (
    get_initial_fact,
    get_user_details_fact,
    get_search_complete_fact,
    get_present_ticket_fact,
    get_conversation_complete_fact,
    get_confirmation_fact
)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

class TrainTicketBot(KnowledgeEngine):
    @Rule(Fact(action='greet'))
    def greet(self):
        print("Hello! Welcome to FareFinder. I'm here to help you find the most affordable train tickets, train delays and blocked lines . Let's get started!")
        self.declare(Fact(action="get_journey_details"))

    @Rule(Fact(action='user_greet'))
    def respond_to_greeting(self):
        print("Hello! How can I assist you today?")

    

    

    @Rule(Fact(action='get_journey_details'))
    def ask_journey_details(self):
        origin = input("Where are you traveling from? ").lower()
        destination = input("Where are you traveling to? ")
        date = input("What date will you be traveling? (e.g., YYYY-MM-DD) ")
        time = input("What time do you prefer to depart? (24-hour format HH:MM) ")
        self.declare(get_user_details_fact(origin, destination, date, time))
        return_response = input("Will you need a return ticket?  ")
        if return_response.lower() in ['yes','yh', 'yeah', 'sure', 'ok', 'sure', 'okay','absolutely']:
            self.declare(Fact(action="ask_return_details"))
        else:
            self.declare(Fact(action="find_tickets"))

    @Rule(Fact(action='ask_return_details'))
    def ask_return_details(self):
        return_date = input("What date will you be returning? (e.g., YYYY-MM-DD) ")
        return_time = input("What time do you prefer to return? (24-hour format HH:MM) ")
        self.declare(Fact(return_date=return_date, return_time=return_time, action="find_tickets"))

    @Rule(Fact(action='find_tickets'), Fact(return_date=W(), return_time=W()))
    def find_return_ticket(self, origin, destination, date, time, return_date, return_time):
        # Simulate searching for outbound tickets
        cheapest_ticket = self.search_for_tickets(origin, destination, date, time)
        # Simulate searching for return tickets
        cheapest_return_ticket = self.search_for_tickets(destination, origin, return_date, return_time)
        print(f"The cheapest outbound ticket from {origin} to {destination} is {cheapest_ticket['price']} at {cheapest_ticket['time']}.")
        print(f"The cheapest return ticket from {destination} to {origin} is {cheapest_return_ticket['price']} at {cheapest_return_ticket['time']}.")
        print(f"You can book the outbound ticket here: {cheapest_ticket['url']}")
        print(f"You can book the return ticket here: {cheapest_return_ticket['url']}")
        self.declare(Fact(action="complete"))

    def search_for_tickets(self, origin, destination, date, time):
        # Placeholder function to simulate ticket searching
        return {
            "price": "£29.99",
            "time": "08:00",
            "url": "https://bookinglink.com"
        }

    @Rule(Fact(action='complete'))
    def complete(self):
        print("Thank you for using the Train Ticket Bot. Safe travels!")
        self.declare(Fact(action="greet"))  # Reset to greet for a new conversation

# Main function to run the bot
def run_bot():
    bot = TrainTicketBot()
    bot.reset()
    bot.declare(get_initial_fact("greet"))
    bot.run()

if __name__ == "__main__":
    run_bot()
