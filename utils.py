from datetime import datetime

def convert_date_format(date_string):
    # Add the current year to the date string
    current_year = datetime.now().year
    date_string_with_year = f"{date_string} {current_year}"

    # Parse the date string into a datetime object
    date = datetime.strptime(date_string_with_year, '%dth %B %Y')

    # Check if the date is in the future
    if date < datetime.now():
        print("Invalid date. Please enter a date in the future.")
        return None

    # Convert the datetime object into the desired format
    formatted_date = date.strftime('%A, %-d %B')

    return formatted_date

def convert_time_format(time_string):
    # Parse the time string into a datetime object
    time = datetime.strptime(time_string, '%I%p')

    # Extract the hours and minutes
    hours = time.hour
    minutes = time.minute

    return hours, minutes



def convert_military_time(time_string):
    # Parse the time string into a datetime object
    time = datetime.strptime(time_string, '%H:%M')

    # Extract the hours and minutes
    hours = time.hour
    minutes = time.minute

    return hours, minutes


def determine_time_format(time_string):
    try:
        # Try to parse the time string as 12-hour format
        hours, minutes = convert_time_format(time_string)
        # Convert the time to 24-hour format
        if hours < 12 and 'pm' in time_string.lower():
            hours += 12
        return '24-hour format', hours, minutes
    except ValueError:
        try:
            # Try to parse the time string as 24-hour format
            hours, minutes = convert_military_time(time_string)
            return '24-hour format', hours, minutes
        except ValueError:
            return 'Invalid format', None, None


if __name__ == '__main__':
    date_string = '12th May'
    formatted_date = convert_date_format(date_string)
    print(formatted_date)  

    # time_string = '1pm'
    # hours, minutes = convert_time_format(time_string)
    # print(hours, minutes)  

    # time_string = '23:00'
    # hours, minutes = convert_military_time(time_string)
    # print(hours, minutes)  # Outputs: 23 0