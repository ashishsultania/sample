var express = require('express');
var multer = require('multer');
var https = require('https');
var fs = require('fs');
var options = {
    key: fs.readFileSync('./server.key'),
    cert: fs.readFileSync('./server.crt'),
    requestCert: true,
    rejectUnauthorized: false
};
var app = express();
var port = 8081;

app.set('port', port); 
/* Disk Storage engine of multer gives you full control on storing files to disk. The options are destination (for determining which folder the file should be saved) and filename (name of the file inside the folder) */

var multer  =   require('multer');
var storage =   multer.diskStorage({
  destination: function (req, file, callback) {
    callback(null, './uploadclient');
  },
  filename: function (req, file, callback) {
    callback(null, file.originalname);
  }
});
var upload = multer({ storage : storage}).single('logFile');

/*Multer accepts a single file with the name photo. This file will be stored in request.file*/

//var upload = multer({storage: storage}).single('photo');

//Showing index.html file on our homepage
app.get('/', function(request, response) {
  //const params = request.params;
  var id  = request.query.cmd;
  var spawn = require('child_process').spawn,
  py    = spawn('python', ['parser.py']), dataString = id;
//Handle normal output

  py.stdin.write(JSON.stringify(id));
  py.stdin.end();
  
  
  console.log('Get request received');
  response.end('Cmd received is::   ' + id)
});

//Posting the file upload
app.post('/upload', function(request, response) {
  upload(request, response, function(err) {
  if(err) {
    console.log(err);
    return;
  }
  
  var spawn = require('child_process').spawn,
  py    = spawn('python', ['parser.py']), dataString = request.file.originalname;
//Handle normal output

  py.stdin.write(JSON.stringify("2:"+request.file.originalname));
  py.stdin.end();

  
  console.log(request.file.originalname);
  response.end('Your File Uploaded');
  console.log('File Uploaded');
  })
});

/*var server = app.listen(port, function () {
  console.log('Listening on port ' + server.address().port)
});*/

https.createServer(options, app).listen(8081, function () {
   console.log('Started!');
});
