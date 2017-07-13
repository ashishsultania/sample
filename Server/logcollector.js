var PythonShell 	= require('python-shell');
var WebSocketServer = require('ws').Server;
var ws 				= require('nodejs-websocket');

var fs         	= require('fs');
var common 		= require('./common');
var connMap 	= common.connMap;
var sleep = require('sleep');

    
process.on( "SIGUSR2", function() {
    //sendscript('tryscript.sh')
	process.chdir('../');
    sendcmd('cmdfile.json');
    process.chdir('./Server');
});


var property = {
  secure:	true,
  key: 		fs.readFileSync('../ssl/server.key'),
  cert: 	fs.readFileSync('../ssl/server.crt'),
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

function sendcmd(file) {
    
    console.log(process.cwd())
    var cmddata = JSON.parse(fs.readFileSync(file, 'utf8'));
    fs.unlink(file);
    var count = 0;
    while (cmddata['cmd'][count]) {
    	var content = cmddata['cmd'][count];
        var jsonData = {
            'userID': "1234",
            'type': "cmd",
            'content': content
        }; 
        console.log(content);
        connMap[1].send(JSON.stringify(jsonData));
        sleep.sleep(4);
        count++;
         
    }
    

}


function sendfile(file){

   var content = base64_encode(file);
   var name = file.match(/([^\/]*)\/*$/)[1];
   
   var jsonData = {
       'userID': "1234",
       'type': "save",
       'name':name,
       'content': content
    }; 

    connMap[1].send(JSON.stringify(jsonData));

}


function sendscript(file){

   var content = base64_encode(file);
   var name = file.match(/([^\/]*)\/*$/)[1];   
   var jsonData = {
       'userID': "1234",
       'type': "execute",
       'name':name,
       'content': content
    }; 
    connMap[1].send(JSON.stringify(jsonData));

}


var server = ws.createServer(property, function (conn) {
    console.log("==== WebSocket Connection ====");
    console.log("New connection requested to: " + conn.path);
    

    var connectionID = conn.path.substring(1);
    console.log(connectionID);
    connMap[1] = conn;
    
    fs.writeFile("conn.dat", connMap, function (err){
        if(err) console.log("Error");
        else console.log("Done");

    });
    
    
    

    conn.on('close', function (code, reason) {
        console.log("WebSocket connection closed");

    });

    // parse received text
    conn.on('text', function(str) 
    {
        console.log('WebSocket received text');
        //console.log(str);
        msg = JSON.parse(str);
        
        
        if(msg['type'] == "tar.gz")
        {
            console.log(process.cwd())
            if("uploadserver".indexOf(process.cwd()) == -1) {
                process.chdir('../uploadserver');

            }
            console.log("Received tar.gz file");
            buffer = base64_decode(msg['content']);
            fs.writeFile(msg['filename'], buffer, "binary", function (err){
                if(err) console.log("Error");
                else{
                    
                    process.chdir('../Server');
                    //var str = JSON.stringify(msg['filename']);
                    var str = msg['filename'];
                    var pid = process.pid;
                    console.log(process.pid)
                    var options = {
                              mode: 'text',
                              pythonPath: '/usr/bin/python',
                              args: [str,pid]
                            };
                    
                    PythonShell.run('serverprocess.py', options, function (err,results) 
                    {
                        
                        if (err) console.log("error" + err);
                          // results is an array consisting of messages collected during execution
                        /*
                            console.log("Received Something");
                            console.log(results);
                            var parseJ = JSON.parse(results);
                            var temp = parseJ['cmd']; 
                          
                          console.log(temp);
                          */
                        
                    });
                    
                    
                    
                }
    
            });



        }
    
        if(msg['type'] == "Hello")
        {
            console.log("Hello Message received");
            console.log(process.pid)
        }

        
        
        if(msg['type'] == "out" || msg['type'] == "outreportexe")
        {
       
        	console.log("Script or Command Output received");
        	//console.log(process.cwd())
            process.chdir('../uploadoutput');
        	//console.log(process.cwd())
        	buffer = (msg['content']);
        	
            fs.writeFileSync(msg['filename'], buffer);
            
            process.chdir('../Server');
        }
        

    });

    


}).listen(9000);




var express = require('express');
var multer  = require('multer');
var https   = require('https');
var app     = express();
var port    = 8082;

var storage =   multer.diskStorage(
{
    destination: function (req, file, callback) 
    {
        callback(null, '/home/ashish/sample/uploadserver');
    },
    filename: function (req, file, callback) 
    {
        callback(null, file.originalname);
    }
});
var upload = multer({ storage : storage}).single('logFile');


var options = 
{
    key: fs.readFileSync('../ssl/server.key'),
    cert: fs.readFileSync('../ssl/server.crt'),
    requestCert: true,
    rejectUnauthorized: false
};



var passport 		= require('passport');
var flash    		= require('connect-flash');

var morgan       	= require('morgan');
var cookieParser 	= require('cookie-parser');
var bodyParser   	= require('body-parser');
var session      	= require('express-session');

var sqlite3 		= require('sqlite3').verbose();
var db;

var configDB 		= require('../WebApp/config/database.js');
var conn_str 		= configDB.dbPath;

var busboy = require('connect-busboy'); //middleware for form/file upload

app.use(busboy());
app.use(express.static(__dirname + '/public'));

require('../WebApp/config/passport')(passport); // pass passport for configuration

// set up our express application
app.use(morgan('dev')); // log every request to the console
app.use(cookieParser()); // read cookies (needed for auth)
app.use(bodyParser()); // get information from html forms

app.set('view engine', 'ejs'); // set up ejs for templating

// required for passport
app.use(session({ secret: 'herehereherehrehrerherherherherherherherhe' })); // session secret
app.use(passport.initialize());
app.use(passport.session()); // persistent login sessions
app.use(flash()); // use connect-flash for flash messages stored in session

// routes ======================================================================
require('../WebApp/routes.js')(app, passport); // load our routes and pass in our app and fully configured passport

// launch ======================================================================
  db = new sqlite3.Database(conn_str);
  db.serialize(function() {
        db.run('DROP TABLE IF EXISTS roles');
        db.run('DROP TABLE IF EXISTS roleAccessLevel');
        db.run('DROP TABLE IF EXISTS fqdnACLevel');
        db.run('DROP TABLE IF EXISTS roleBasedAC');
        //db.run('DROP TABLE IF EXISTS logs');
        //db.run('DROP TABLE IF EXISTS users');

	
  	db.run('CREATE TABLE  IF NOT EXISTS logs ( id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, srcMAC TEXT, src TEXT, dst TEXT, UNIQUE(srcMAC,dst));');	

  	db.run('CREATE TABLE  IF NOT EXISTS roles ( role_id INTEGER PRIMARY KEY, roleDesc TEXT);');	
	db.run('INSERT INTO roles VALUES (1,"Student")');
	db.run('INSERT INTO roles VALUES (2, "Professor")');
	db.run('INSERT INTO roles VALUES (3, "Admin")');

  	db.run('CREATE TABLE  IF NOT EXISTS roleAccessLevel ( id INTEGER PRIMARY KEY AUTOINCREMENT, role INTEGER, accessLevel INTEGER, FOREIGN KEY(role) REFERENCES roles(role_id));');
	db.run('INSERT INTO roleAccessLevel(role,accessLevel) VALUES (1, 1)');
	db.run('INSERT INTO roleAccessLevel(role,accessLevel) VALUES (2, 2)');
	db.run('INSERT INTO roleAccessLevel(role,accessLevel) VALUES (3, 4)');

	db.run('CREATE TABLE IF NOT EXISTS fqdnACLevel (id INTEGER PRIMARY KEY AUTOINCREMENT, fqdn TEXT, accessLevel INTEGER, FOREIGN KEY(accessLevel) REFERENCES roleAccessLevel(accessLevel))');
	db.run('INSERT INTO fqdnACLevel(fqdn,accessLevel) VALUES ("iot.aalto.fi", 2)');
	db.run('INSERT INTO fqdnACLevel(fqdn,accessLevel) VALUES ("guest.aalto.fi", 1)');

  	db.run('CREATE TABLE  IF NOT EXISTS roleBasedAC ( id INTEGER PRIMARY KEY AUTOINCREMENT, calledSID TEXT, fqdn TEXT, FOREIGN KEY (fqdn) REFERENCES fqdnACLevel(fqdn));');
	db.run('INSERT INTO roleBasedAC(calledSID,fqdn) VALUES ("6C-19-8F-83-C2-90:Noob2","iot.aalto.fi")');
	db.run('INSERT INTO roleBasedAC(calledSID,fqdn) VALUES ("6C-19-8F-83-C2-80:Noob1","guest.aalto.fi")');
  	
	db.run('CREATE TABLE IF NOT EXISTS radius (called_st_id TEXT, calling_st_id  TEXT, NAS_id TEXT, user_name TEXT PRIMARY KEY);');	


  	db.run('CREATE TABLE  IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role INTEGER DEFAULT 1, isAdmin BOOLEAN DEFAULT FALSE,  FOREIGN KEY(role) REFERENCES roles(role_id) );');
  	db.run('CREATE TABLE  IF NOT EXISTS devices (PeerID TEXT, serv_state INTEGER, PeerInfo TEXT, Noob TEXT, Hoob TEXT, Hint TEXT,errorCode INTEGER ,UserName TEXT, PRIMARY KEY (PeerID, UserName));');




  	db.close();
  });







app.set('port', port); 


app.get('/ls', function(request, response) 
{
    var id  = request.query.cmd;
    

    var jsonData = {
        'userID': "1234",
        'type': "cmd",
        'content': id
    }; 

    connMap[1].send(JSON.stringify(jsonData)); 

    
  
    console.log('Get request received');
    response.end('Cmd received is::   ' + id)
});


//Posting the file upload
app.post('/upload', function(request, response) 
{
	process.chdir('../uploadserver');
	console.log(process.cwd())
    upload(request, response, function(err) 
    {
        if(err) 
        {
            console.log(err);
            return;
        }
        
        //console.log(request);
    	console.log(process.cwd())
    	console.log(request.file.originalname)

        sendscript(request.file.originalname);

        
        /*
        var spawn = require('child_process').spawn,
        py          = spawn('python', ['serverprocess.py']), dataString = request.file.originalname;

        py.stdin.write(JSON.stringify(request.file.originalname));
        py.stdin.end();
        
 
        console.log(request.file.originalname);
        response.end('Your File Uploaded');
        */
        console.log('Script Uploaded');
        response.end('Your File Uploaded');
    })
});

app.post('/sendConf', function(request, response) 
{
    console.log(request);
	path_val = './'
	sendConf(request, response, function(err) 
    {
        if(err) 
        {
        	console.log(err);
        	return;
        }
  		
  
        console.log(request.file.originalname);
        sendfile(request.file.originalname)
        console.log('File Uploaded /save');
        response.end('Your File Uploaded');
    })
});


https.createServer(options, app).listen(8082, function () {
   console.log('Started!');
});
