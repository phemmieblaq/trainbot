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
io.on('connection', (socket) => {
  const python = spawn('python3', ['gettingTrain.py']);
  
  python.stdout.on('data', (data) => {
    const botMessage = data.toString();
    socket.emit('botMessage', botMessage); // Emit 'botMessage' event
  });

  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  python.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });

  socket.on('userMessage', (message) => {
    python.stdin.write(message + '\n');
  });
});

server.listen(3000, () => {
    console.log('listening on *:3000');
});
