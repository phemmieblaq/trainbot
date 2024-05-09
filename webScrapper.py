import json
import requests
from bs4 import BeautifulSoup
#https://www.nationalrail.co.uk/journey-planner/?type=single&origin=182&destination=NRW&leavingType=departing&leavingDate=080524&leavingHour=07&leavingMin=00&adults=1&extraTime=0#O

class Ticket(object):
    url = ""
   

    @staticmethod
    def custom_to_date(date_string, date_format):
        # Implement the custom_to_date function here
        pass

    @staticmethod
    def get_page_contents(url):
        Ticket.url = url
        r = requests.get('https://www.nationalrail.co.uk/journey-planner/?type=single&origin=NRW&destination=182&leavingType=departing&leavingDate=080524&leavingHour=09&leavingMin=30&adults=1&extraTime=0#O'
)
        #print(f"Response status code: {r.status_code}")
        s= BeautifulSoup(r.text, 'html.parser')
        with open('output.html', 'w') as f:
            f.write(s.prettify())

        
      


    @staticmethod
    def get_ticket_single(from_location, to_location, depart_date, depart_time_hour, depart_min):
        url='https://www.nationalrail.co.uk/journey-planner/?type=single&origin='+ from_location+'&destination=' + to_location + '&leavingType=departing&leavingDate='+ depart_date + '&leavingHour='+depart_time_hour+'&leavingMin=' +depart_min+'&adults=1&extraTime=0#O'

        # url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + from_location + '/' + to_location
        #        + '/' + depart_date + '/' + depart_time + '/dep')
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
                #print(info)
                if not info:
                    return None

            ticket = {'url': Ticket.url, 'isReturn': is_return, 'departDate': Ticket.custom_to_date(depart_date, '%d-%b-%Y'),
                      'departureStationName': str(info['jsonJourneyBreakdown']['departureStationName']),
                      'arrivalStationName': str(info['jsonJourneyBreakdown']['arrivalStationName']),
                      'departureTime': str(info['jsonJourneyBreakdown']['departureTime']),
                      'arrivalTime': str(info['jsonJourneyBreakdown']['arrivalTime'])}
            #print(f"Ticket: {ticket['url']}")

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

    page_url = 'https://www.nationalrail.co.uk/journey-planner/?type=single&origin=NRW&destination=182&leavingType=departing&leavingDate=080524&leavingHour=10&leavingMin=00&adults=1&extraTime=0#O'
    page_contents = Ticket.get_page_contents(page_url)
    #print (page_contents)
    Ticket.get_cheapest_ticket(page_contents, False, '080524', None)
    #Ticket.get_ticket_single('NRW', '182', '080524', '09','30')