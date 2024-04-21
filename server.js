// Save this as app.js
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { spawn } = require('child_process'); //to run python scripts
const {pool} = require('./dbConnection.js');
const bodyParser = require('body-parser');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);


//middleware
app.use(bodyParser.json());   // Using body parser to handle form data
app.use(bodyParser.urlencoded({extended: false}))    

app.use(express.static('assets'))    // Sets default file directory to 'assets'

app.set('view engine', 'ejs'); // Sets view engine to ejs




// route to render index file 
app.get('/', (req, res) =>
{
  try
  {
    res.render('index');
  }
  catch (err)
  {
    console.log(err.message);
  }
});


app.get('/chatbot', (req, res) =>
{
  try
  {
    res.render('mainChatbot');
  }
  catch (err)
  {
    console.log(err.message);
  }
});

// Socket connection handler
io.on('connection', (socket) => {
    console.log("A user connected");

    // Listen for a 'request train info' event from client
    socket.on('request train info', (fromStation, toStation, date) => {
        console.log(`Received train info request: ${fromStation} to ${toStation} on ${date}`);

        // Start the Python scraper with arguments
        const pythonProcess = spawn('python', ['railwayScrapper.py', fromStation, toStation, date]);

        pythonProcess.stdout.on('data', (data) => {
            // Parse the output from the Python script
            const response = JSON.parse(data.toString());
            console.log("Sending train ticket data back to client");

            // Emit the response back to the client
            socket.emit('train info response', response);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data.toString()}`);
            socket.emit('error', 'Failed to fetch ticket information');
        });

        pythonProcess.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });
    });
});
server.listen(3000, () => {
    console.log('listening on *:3000');
});
