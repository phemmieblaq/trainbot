// Required Libraries
const express = require('express');
const puppeteer = require('puppeteer');

// Function to Convert Ticket Information to String
const convertTicketInfoToString = (ticketDetails, travelDate, ticketType) => {
 return `${ticketType === 'single' ? 'Single' : 'Return'} Ticket
Departure Date: ${travelDate}
Departure Station: ${ticketDetails['jsonJourneyBreakdown']['departureStationName']}
Arrival Station: ${ticketDetails['jsonJourneyBreakdown']['arrivalStationName']}
Departure Time: ${ticketDetails['jsonJourneyBreakdown']['departureTime']}
Arrival Time: ${ticketDetails['jsonJourneyBreakdown']['arrivalTime']}
Price: £${ticketDetails['singleJsonFareBreakdowns'][0]['fullFarePrice'].toFixed(2)}`;
};

// Function to Convert Ticket Information to HTML String
const convertTicketInfoToHTMLString = (ticketDetails, travelDate, ticketType) => {
 return `${ticketType === 'single' ? 'Single' : 'Return'} Ticket<br>
Departure Date: ${travelDate}<br>
Departure Station: ${ticketDetails['jsonJourneyBreakdown']['departureStationName']}<br>
Arrival Station: ${ticketDetails['jsonJourneyBreakdown']['arrivalStationName']}<br>
Departure Time: ${ticketDetails['jsonJourneyBreakdown']['departureTime']}<br>
Arrival Time: ${ticketDetails['jsonJourneyBreakdown']['arrivalTime']}<br>
Price: £${ticketDetails['singleJsonFareBreakdowns'][0]['fullFarePrice'].toFixed(2)}`;
};

// Function to Convert Month Number to String
const monthNumberToString = month => {
 switch(parseInt(month)) {
    case 1: return 'Jan';
    case 2: return 'Feb';
    case 3: return 'Mar';
    case 4: return 'Apr';
    case 5: return 'May';
    case 6: return 'Jun';
    case 7: return 'Jul';
    case 8: return 'Aug';
    case 9: return 'Sep';
    case 10: return 'Oct';
    case 11: return 'Nov';
    case 12: return 'Dec';
 }
 return null;
};



// Async Function to Fetch Train Tickets
async function fetchTrainTicketDetails(journeyDetails) {
 try {
    console.log('Initiating browser for ticket fetching...');
    const browserInstance = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--headless', 'ignoreHTTPSErrors=true']
    });
    console.log('Browser successfully launched.');
    const page = await browserInstance.newPage();

    await page.goto('https://ojp.nationalrail.co.uk/service/planjourney/search', { waitUntil: 'networkidle0' });
    console.log('Navigated to the National Rail website.');

    await page.screenshot({path: './puppeteerFeed/initial_scrape.png'});
    
    await page.waitForSelector('#onetrust-accept-btn-handler', { visible: true });
    await page.click('#onetrust-accept-btn-handler');
    console.log('Cookie consent managed.');

    await page.screenshot({path: './images/scrape.png'});

    await page.type('#txtFrom', journeyDetails.single.depStation);
    await page.type('#txtTo', journeyDetails.single.arrStation);
    await page.type('#txtDate', journeyDetails.single.depDate);
    console.log('Journey details populated.');

    const submitButton = await page.evaluateHandle(() => document.querySelector('button[type="submit"]'));
    await submitButton.click();
    console.log('Search initiated.');

    await page.waitForNavigation();
    await page.screenshot({path: './puppeteerFeed/post_search.png'});

    // Implement logic to handle tickets as previously described

    await browserInstance.close();
    console.log('Browser closed after fetching tickets.');
    return true;
 } catch (error) {
    console.log(`An error occurred while fetching tickets: ${error}`);
    return false;
 }
}

// Example usage:
const journeyDetails = {
 single: {
    depStation: "Norwich",
    arrStation: "Romford",
    depDate: "25/07/2023"
 }
};

fetchTrainTicketDetails(journeyDetails);