
var express = require('express');
var multer 	= require('multer');
var https	= require('https');
var fs 		= require('fs');
var app 	= express();
var port 	= 8082;

var options = 
{
    key: fs.readFileSync('./server.key'),
    cert: fs.readFileSync('./server.crt'),
    requestCert: true,
    rejectUnauthorized: false
};

app.set('port', port); 

var multer  =   require('multer');
var storage =   multer.diskStorage(
{
    destination: function (req, file, callback) 
    {
        callback(null, './uploadserver');
    },
    filename: function (req, file, callback) 
    {
        callback(null, file.originalname);
    }
});
var upload = multer({ storage : storage}).single('logFile');

app.get('/', function(request, response) 
{
    var id  = request.query.cmd;
  
    console.log('Get request received');
    response.end('Cmd received is::   ' + id)
});


//Posting the file upload
app.post('/upload', function(request, response) 
{
    upload(request, response, function(err) 
    {
        if(err) 
        {
            console.log(err);
            return;
        }
        var spawn = require('child_process').spawn,
        py    	  = spawn('python', ['serverprocess.py']), dataString = request.file.originalname;

        py.stdin.write(JSON.stringify(request.file.originalname));
        py.stdin.end();

        console.log(request.file.originalname);
        response.end('Your File Uploaded');
        console.log('File Uploaded');
    })
});

https.createServer(options, app).listen(8082, function () {
   console.log('Started!');
});