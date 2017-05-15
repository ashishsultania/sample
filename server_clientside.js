
var express = require('express');
var multer  = require('multer');
var https   = require('https');
var fs      = require('fs');
var app 	= express();
var port 	= 8081;

var options = {
				key: fs.readFileSync('./server.key'),
				cert: fs.readFileSync('./server.crt'),
				requestCert: true,
				rejectUnauthorized: false
};
var path_val;
app.set('port', port); 
var storage =   multer.diskStorage({
	destination: function (req, file, callback) 
	{
		callback(null, path_val);
	},
    filename: function (req, file, callback) 
    {
    	callback(null, file.originalname);
    }
});
var upload = multer({ storage : storage}).single('logFile');

var save = multer({ storage : storage}).single('logFile');



app.get('/', function(request, response) 
{
    var id  	= request.query.cmd;
    var spawn 	= require('child_process').spawn,
    py    		= spawn('python', ['parser.py']), dataString = id;

    py.stdin.write(JSON.stringify(id));
    py.stdin.end();

    console.log('Get request received');
    response.end('Cmd received is::   ' + id)
});


app.post('/upload', function(request, response) 
{
	path_val = './uploadclient'
    upload(request, response, function(err) 
    {
        if(err) 
        {
        	console.log(err);
        	return;
        }
  
        var spawn 	= require('child_process').spawn,
        py    		= spawn('python', ['parser.py']), dataString = request.file.originalname;

        py.stdin.write(JSON.stringify("2:"+request.file.originalname));
        py.stdin.end();

  
        console.log(request.file.originalname);
        response.end('Your File Uploaded /upload');
        console.log('File Uploaded /upload');
    })
});

app.post('/save', function(request, response) 
{
	path_val = './'
	save(request, response, function(err) 
    {
        if(err) 
        {
        	console.log(err);
        	return;
        }
  		     
  
        console.log(request.file.originalname);
        response.end('Your File Uploaded /save');
        console.log('File Uploaded /save');
    })
});


https.createServer(options, app).listen(8081, function () 
{
    console.log('Started!');
});
