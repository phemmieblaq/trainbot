from experta import Fact

# Returns a simple fact based on the action name
def get_initial_fact(action_name):
    return Fact(action=action_name)

# Fact for user journey details
def get_user_details_fact(origin, destination, date, time):
    return Fact(action="find_tickets", origin=origin, destination=destination, date=date, time=time)

# Fact for ticket search completion
def get_search_complete_fact():
    return Fact(action="search_complete")

# Fact for presenting the cheapest ticket found
def get_present_ticket_fact(url):
    return Fact(action="present_ticket", url=url)

# Fact for completion of the conversation
def get_conversation_complete_fact():
    return Fact(action="complete_conversation")

# Fact for handling user confirmations
def get_confirmation_fact(user_response):
    if user_response.lower() in ['yes', 'y', 'sure', 'ok']:
        return Fact(action="confirm_yes")
    else:
        return Fact(action="confirm_no")

# Fact for handling user queries about travel conditions or delays
def get_query_delay_fact():
    return Fact(action="query_delay")

# Fact for asking return journey details
def get_return_journey_fact():
    return Fact(action="ask_return_details")

# Fact for return journey details
def get_return_details_fact(return_date, return_time):
    return Fact(action="find_return_tickets", return_date=return_date, return_time=return_time)

# Fact for handling alternative travel options if the user requests it
def get_alternative_travel_options_fact():
    return Fact(action="offer_alternatives")

# Fact for handling emergencies or special notices
def get_emergency_notice_fact(emergency_details):
    return Fact(action="emergency_notice", details=emergency_details)

# Fact for initiating a new search based on user's request to modify search parameters
def get_modify_search_fact():
    return Fact(action="modify_search")

# Fact for requesting additional user details when needed
def get_request_additional_details_fact(missing_details):
    return Fact(action="request_additional_details", details=missing_details)
