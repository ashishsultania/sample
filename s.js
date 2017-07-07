
var express = require('express');
var multer 	= require('multer');
var https	= require('https');
var fs 		= require('fs');
var app 	= express();
var port 	= 8082;
var connMap = {};
var options = 
{
    key: fs.readFileSync('./server.key'),
    cert: fs.readFileSync('./server.crt'),
    requestCert: true,
    rejectUnauthorized: false
};


var WebSocketServer = require('ws').Server;
var ws = require('nodejs-websocket');

var property = {
  secure:true,
  key: fs.readFileSync('./server.key'),
  cert: fs.readFileSync('./server.crt'),
  requestCert: true,
  rejectUnauthorized: false
};


function base64_encode(file) {
    // read binary data
    var bitmap = fs.readFileSync(file);
    // convert binary data to base64 encoded string
    return new Buffer(bitmap).toString('base64');
}

function base64_decode(str_cont) {
    // read binary data
    var buf = new Buffer(str_cont,'base64');
    return buf;
}

var server = ws.createServer(property, function (conn) {
    console.log("==== WebSocket Connection ====");
    console.log("New connection requested to: " + conn.path);
    console.log(conn.path);

    var connectionID = conn.path.substring(1);
    console.log(connectionID);
    connMap[1] = conn;

    conn.on('close', function (code, reason) {
        console.log("WebSocket connection closed");

    });

    // parse received text
    conn.on('text', function(str) {
        console.log('WebSocket received text');
        console.log(str);
        msg = JSON.parse(str);
	if(msg['type'] == "tar.gz"){
		console.log("Received file");
		buffer = base64_decode(msg['content']);
		fs.writeFile("asish1.tar.gz", buffer, "binary", function (err){
			if(err) console.log("Error");
			else console.log("Done");

		});



	}
        if(msg['type'] == "softwareUpdated"){
                console.log("Updated received");
        }
    });

    

    // Sending data
    connMap[1] = conn;

   var content = base64_encode('asish.tar.gz');

       var jsonData = {
        'userID': "1234",
        'type': "txt",
        'content': content
    }; 

    connMap[1].send(JSON.stringify(jsonData));

}).listen(9000);







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

app.set('port', port); 
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

app.post('/sendConf', function(request, response) 
		{
			 var spawn = require('child_process').spawn,
		     py    	  = spawn('python', ['send.py']), dataString = request.file.originalname;
		
		     py.stdin.write(JSON.stringify(request.file.originalname));
		     py.stdin.end();
		
		     console.log(request.file.originalname);
		     response.end('Your File Uploaded');
		     console.log('File Uploaded');
		});


https.createServer(options, app).listen(8082, function () {
   console.log('Started!');
});
