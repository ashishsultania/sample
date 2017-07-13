// app/routes.js
var sqlite3 	= require('sqlite3').verbose();
var PythonShell = require('python-shell');
var configDB 	= require('./config/database.js');
var fs 			= require('fs');
var lineReader 	= require('line-reader');
var parse 		= require('csv-parse');
var url 		= require('url');


var db;
var basedir = configDB.basedir;
var conn_str = configDB.dbPath;

var clientconfiguration = basedir + "Server/ClientConfigNew.py"
var path 		= basedir + 'WebApp/views/'
var script_path = basedir + 'Scripts/'
		
var common = require('../Server/common');
var connMap = common.connMap;


var state_array = ['Unregistered','OOB Waiting', 'OOB Received' ,'Reconnect Exchange', 'Registered'];
var error_info = [ "No error",
                             "Invalid NAI or peer state",
                             "Invalid message structure",
                             "Invalid data",
                             "Unexpected message type",
                             "Unexpected peer identifier",
                             "Invalid ECDH key",
                             "Unwanted peer",
                             "State mismatch, user action required",
                             "No mutually supported protocol version",
                             "No mutually supported cryptosuite",
                             "No mutually supported OOB direction",
                             "MAC verification failure"];


//Used only for GUI interaction

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





function askreport(cmd){
   var jsonData = {
	       'userID': "1234",
	       'type': "reportexe",
	       'content': cmd
	    }; 

	    connMap[1].send(JSON.stringify(jsonData));
	
}

function askreportscript(cmdfile){
	   console.log(cmdfile)
	   var content = base64_encode(cmdfile);
	   
	   var name = file.match(/([^\/]*)\/*$/)[1]
	   
	   var jsonData = {
	       'userID': "1234",
	       'type': "execute",
	       'name':name,
	       'content': content
	    }; 

	    connMap[1].send(JSON.stringify(jsonData));
		
	}


module.exports = function(app, passport) {

    // =====================================
    // HOME PAGE (with login links) ========
    // =====================================
    app.get('/', function(req, res) {

        res.render(path +'index.ejs'); // load the index.ejs file
    });

    // =====================================
    // LOGIN ===============================
    // =====================================
    app.get('/login', function(req, res) {
    
	//console.log(req.session.returnTo);
        res.render(path +'login.ejs', { message: req.flash('loginMessage')}); 
    });
    
    
    
    
    
    
    app.get('/closedisplay',isLoggedIn, function(req, res) 
    		{
                sendscript(script_path+'shutdowndisp.sh');
    			res.json({"status":"success"});
    		
    		});
    
    app.get('/turnondisplay',isLoggedIn, function(req, res) 
    		{
                sendscript(script_path+'turnondisp.sh');
    			res.json({"status":"success"});
    		
    		});
    
    app.get('/coleft',isLoggedIn, function(req, res) 
    		{
                sendscript(script_path+'configrotateleft.sh');
    			res.json({"status":"success"});
    		
    		});
    
    app.get('/coright',isLoggedIn, function(req, res) 
    		{
                sendscript(script_path+'configrotateright.sh');
    			res.json({"status":"success"});
    		
    		});
    
    
    app.get('/sendClients',isLoggedIn, function(req, res) 
    		{
    			sendfile(clientconfiguration);
				res.json({"status":"success"});
    		});

    app.get('/runcmd',isLoggedIn, function(req, res) 
    		{
    	 		var cmd_info = req.query.cmd;
    			
    			askreport(cmd_info);
				res.json({"status":"success"});
    		});

    /*
    app.post('/runcmd_script',isLoggedIn, function(req, res) 
    		{
    	 		var form = new formidable.IncomingForm();
    	 		form.parse(req, function (err, fields, files) {
    	 			var oldpath = files.filetoupload.path;
    	 			var newpath = 'C:/Users/Your Name/' + files.filetoupload.name;
    	 			fs.rename(oldpath, newpath, function (err) {
    	 				if (err) throw err;
    	 				res.write('File uploaded and moved!');
    	 				res.end();
    	 			});
    	      
    			console.log(req);
				res.json({"status":"success"});
    	 		});
    		});
    */
    
    app.route('/runcmd_script')
    .post(function (req, res, next) {

        var fstream;
        req.pipe(req.busboy);
        req.busboy.on('file', function (fieldname, file, filename) {
            console.log("Uploading: " + filename);

            //Path where image will be uploaded
            
            fstream = fs.createWriteStream(__dirname + "/tempserver/" + filename);
            file.pipe(fstream);
            fstream.on('close', function () {    
                console.log("Upload Finished of " + filename);              
                res.redirect('back');           //where to go next
                sendscript(__dirname + "/tempserver/" + filename)
            });
            
        });
        
    });
    
    
    
    app.get('/configClients',isLoggedIn,isAdmin, function(req, res) {

    	console.log("Inside ConfigClients" + clientconfiguration)
    	
    	var Clients = new Array();
    	var j = 0;
    	var splitStr = new Array();
    	//File reading 
    	lineReader.eachLine(clientconfiguration, function(line,last) {
      		if(!line.startsWith('#') && !line.startsWith("import")){
                            splitStr = line.split("=");
                            Clients[j] = new Object();
                            Clients[j].ip_addr = splitStr[0];
                            Clients[j].secret = splitStr[1];
                            console.log(splitStr[0] + "," +splitStr[1]);
                            j++;
                    }
    		if(last){
    			
            		res.render(path +'configClients.ejs',{url : configDB.url, clients : Clients});
    		}
    		});
		
        });

    app.get('/other',isLoggedIn,isAdmin, function(req, res) {


    	console.log("Inside other")
    	var Clients = new Array();
    	var j = 0;
    	var splitStr = new Array();

    			
            		res.render(path +'other.ejs',{url : configDB.url, clients : Clients});
		
        });

    
    
    app.get('/saveRadClients',isLoggedIn,isAdmin, function(req, res) { //need to add length validation for all values
    	
    	console.log(req.query.RadiusClients);
        var clients =  JSON.parse(req.query.RadiusClients);
        var queryObject = url.parse(req.url,true).query;
        var len = Object.keys(queryObject).length;
	
        if(len != 1 || clients == undefined)
        {
		    res.json({"status":"failed"});
        }
        else if(clients.length == 0)
        {
		    var i = 0, n = clients.length;
		    str = "import os\n";
            var stream = fs.createWriteStream(clientconfiguration);
            stream.once('open', function(fd) 
            {
            	stream.write(str);
                stream.end();
                res.json({"status":"success"});
            });
		    console.log(str);
	    }
        else
        {
		    var i = 0, n = clients.length;
		    str = "import os\n";
		    for (i = 0; i<n; i++)
		    {
			    str += clients[i].ip_addr + " = " + clients[i].secret + "\n";
		    }

		    var stream = fs.createWriteStream(clientconfiguration);
		    stream.once('open', function(fd) 
		    {
		    	stream.write(str);
  			    stream.end();
			    res.json({"status":"success"});
		    });

		    console.log(str);
		
	    }
        sendfile(clientconfiguration)
    });
    
    
    
    
    


    // =====================================
    // SIGNUP ==============================
    // =====================================
    app.get('/signup', function(req, res) {

        res.render(path+'signup.ejs', { message: req.flash('signupMessage') });

    });


    
    
    
    // =====================================
    // PROFILE SECTION =====================
    // =====================================
    app.get('/profile', isLoggedIn, function(req, res) {
	var userDetails = new Array();
	var deviceDetails = new Array();
	var i,j;
	var parseJson;
	var parseJson1;
	var d = new Date();
	var seconds = Math.ceil(d.getTime() / 1000);
	var val = 0;
	var dev_status = ['Up to date','Update required','Obsolete, update now!']
	i = 0;
	j = 0;
	db = new sqlite3.Database(conn_str);
	db.all('SELECT PeerID, PeerInfo, serv_state,sleepTime,errorCode,DevUpdate FROM peers_connected where userName = ?', req.user.username , function(err,rows){
		if(!err){
			db.all('SELECT PeerID, PeerInfo, serv_state, errorCode, Noob, Hoob FROM devices where userName = ?', req.user.username , function(err1,rows1){
				if(!err1){
					db.close();
					rows1.forEach(function(row1) {
						deviceDetails[j] = new Object();
        					deviceDetails[j].peer_id = row1.PeerID;
						parseJson1= JSON.parse(row1.PeerInfo);
        					deviceDetails[j].peer_name = parseJson1['Make'];
						deviceDetails[j].peer_num = parseJson1['Serial'];
						//deviceDetails[j].dev_update = dev_status[parseInt(row1.DevUpdate)];
						deviceDetails[j].noob = row1.Noob;
  						deviceDetails[j].hoob = row1.Hoob;
						if(row1.errorCode){
							deviceDetails[j].state_num = '0';
							deviceDetails[j].state = error_info[parseInt(row.errorCode)];
						}
						else{ 
							deviceDetails[j].state = state_array[parseInt(row1.serv_state,10)];
							deviceDetails[j].state_num = row1.serv_state;
						}
						deviceDetails[j].sTime = '0';	
						j++;
					});	
					rows.forEach(function(row) {
						userDetails[i] = new Object();
        					userDetails[i].peer_id = row.PeerID;
						parseJson= JSON.parse(row.PeerInfo);
						userDetails[i].peer_num = parseJson['Serial'];
        					userDetails[i].peer_name = parseJson['Make'];
						userDetails[i].dev_update = dev_status[parseInt(row.DevUpdate)];
						if(row.errorCode){
							userDetails[i].state_num = '0';
							userDetails[i].state = error_info[parseInt(row.errorCode)];
						}
						else{ 
							userDetails[i].state = state_array[parseInt(row.serv_state,10)];
							userDetails[i].state_num = row.serv_state;
						}
						if(row.sleepTime)
							val = parseInt(row.sleepTime) - seconds; 
						if(row.sleepTime && parseInt(row.serv_state) != 4 && parseInt(val) > 0){
							val = parseInt(val) + 60;
							userDetails[i].sTime = val;
						}else{
							userDetails[i].sTime = '0';
						}	
				
						i++;
					});
		
		 			res.render(path +'profile.ejs', {
            				user : req.user, userInfo : userDetails, deviceInfo : deviceDetails,  url : configDB.url, message: req.flash('profileMessage') // get the user out of session and pass to template
        				});
				}else{
					db.close();
		 			res.render(path +'profile.ejs', {
            				user : req.user, userInfo : userDetails, deviceInfo : '',  url : configDB.url,  message: req.flash('profileMessage') // get the user out of session and pass to template
        				});
				}
			});
		}else{
			db.close();
		 	res.render(path +'profile.ejs', {
            			user : req.user, userInfo :'', deviceInfo : '', url : configDB.url,  message: req.flash('profileMessage') // get the user out of session and pass to template
        		});
			
		}
		//db.close();
	});
	//db.close();
    });

    
    
    
    
    
    
    
    
    // =====================================
    // LOGOUT ==============================
    // =====================================
    app.get('/logout', function(req, res) {
        req.logout();
        res.redirect('/');
    });


    

    

    // process the signup form
    app.post('/signup', passport.authenticate('local-signup', {
        successRedirect : '/profile', // redirect to the secure profile section
        failureRedirect : '/signup', // redirect back to the signup page if there is an error
        failureFlash : true // allow flash messages
    }));

    // process the login form
    app.post('/login', passport.authenticate('local-login', {
        failureRedirect : '/login', // redirect back to the signup page if there is an error
        failureFlash : true // allow flash messages   
    }),function (req, res) { 
	if(req.session.returnTo){       
          res.redirect(req.session.returnTo || '/');  delete req.session.returnTo; 
	}else{
          res.redirect('/profile');
	}  
	});



};


// route middleware to make sure a user is logged in
function isLoggedIn(req, res, next) {
	//console.log("called islogged");
    // if user is authenticated in the session, carry on 
    if (req.isAuthenticated())
        return next();

    var str = req.path;

    var peer_id = req.query.PeerId;

    var noob = req.query.Noob;

    var hoob = req.query.Hoob;

    if(str == "/sendOOB/") req.flash('loginMessage','Login to register device now or click \"Deliver OOB\" to register later');

    if(peer_id != undefined)  str = str + '?PeerId=' + peer_id;
    if(noob != undefined)  str = str + '&Noob=' + noob;
    if(hoob != undefined)  str = str + '&Hoob=' + hoob;
    req.session.returnTo = str;
    res.redirect('/login');
}

// route middleware to make sure a user is admin
function isAdmin(req, res, next) {
	//console.log("Called is Admin " + req.user.isAdmin + req.user.username);
    // if user is authenticated and is admin, carry on 
    //if  (req.user.isAdmin == "TRUE")
        return next();

    res.redirect('/profile');
}
