import json
import requests
from bs4 import BeautifulSoup


class Ticket(object):
    url = ""
   

    @staticmethod
    def custom_to_date(date_string, date_format):
        # Implement the custom_to_date function here
        pass

    @staticmethod
    def get_page_contents(url):
        Ticket.url = url
        r = requests.get(url)
        print(f"Response status code: {r.status_code}") 
        
        return BeautifulSoup(r.text, 'html.parser')

    @staticmethod
    def get_ticket_single(from_location, to_location, depart_date, depart_time):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + from_location + '/' + to_location
               + '/' + depart_date + '/' + depart_time + '/dep')
        html = Ticket.get_page_contents(url)
        print(url)
        return Ticket.get_cheapest_ticket(html, False, depart_date, None)

    @staticmethod
    def get_ticket_return(from_location, to_location, depart_date, depart_time, return_date, return_time):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + from_location + '/' + to_location
               + '/' + depart_date + '/' + depart_time + '/dep/' + return_date + '/' + return_time + '/dep')
        html = Ticket.get_page_contents(url)
        return Ticket.get_cheapest_ticket(html, True, depart_date, return_date)

    @staticmethod
    def get_cheapest_ticket(page_contents, is_return, depart_date, return_date):

        if not page_contents:
            return None
        try:

            for x in page_contents.find('script', {'type': 'application/json'}):
                info = json.loads(str(x).strip())
                if not info:
                    return None

            ticket = {'url': Ticket.url, 'isReturn': is_return, 'departDate': Ticket.custom_to_date(depart_date, '%d-%b-%Y'),
                      'departureStationName': str(info['jsonJourneyBreakdown']['departureStationName']),
                      'arrivalStationName': str(info['jsonJourneyBreakdown']['arrivalStationName']),
                      'departureTime': str(info['jsonJourneyBreakdown']['departureTime']),
                      'arrivalTime': str(info['jsonJourneyBreakdown']['arrivalTime'])}
            print(f"Ticket: {ticket['url']}")

            duration_hours = str(info['jsonJourneyBreakdown']['durationHours'])
            duration_minutes = str(info['jsonJourneyBreakdown']['durationMinutes'])
            ticket['duration'] = (duration_hours + 'h ' + duration_minutes + 'm')
            ticket['changes'] = str(info['jsonJourneyBreakdown']['changes'])

            if is_return:
                ticket['returnDate'] = Ticket.custom_to_date(return_date, '%d-%b-%Y')
                ticket['fareProvider'] = info['returnJsonFareBreakdowns'][0]['fareProvider']
                ticket['returnTicketType'] = info['returnJsonFareBreakdowns'][0]['ticketType']
                ticket['ticketPrice'] = info['returnJsonFareBreakdowns'][0]['ticketPrice']
            else:
                ticket['fareProvider'] = info['singleJsonFareBreakdowns'][0]['fareProvider']
                ticket['ticketPrice'] = info['singleJsonFareBreakdowns'][0]['ticketPrice']

            print (ticket)
        
            

        except:
            return False
if __name__ == "__main__":
    Ticket.get_ticket_single('LON', 'BHM', '2022-12-25', '09:00')