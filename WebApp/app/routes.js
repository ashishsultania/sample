// app/routes.js
var sqlite3 = require('sqlite3').verbose();
var db;

var configDB = require('../config/database.js');
var conn_str = configDB.dbPath;

var rad_cli_path = configDB.radCliPath;

var PythonShell = require('python-shell');


var fs = require('fs');
var lineReader = require('line-reader');

var parse = require('csv-parse');

var multer  =   require('multer');
var storage =   multer.diskStorage({
  destination: function (req, file, callback) {
    callback(null, './uploads');
  },
  filename: function (req, file, callback) {
    callback(null, file.fieldname +'.csv');
  }
});
//var sleep = require('sleep');
var upload = multer({ storage : storage}).single('logFile');

var url = require('url');
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
module.exports = function(app, passport) {

    // =====================================
    // HOME PAGE (with login links) ========
    // =====================================
    app.get('/', function(req, res) {
        res.render('index.ejs'); // load the index.ejs file
    });

    // =====================================
    // LOGIN ===============================
    // =====================================
    app.get('/login', function(req, res) {

        // render the page and pass in any flash data if it exists
	//console.log(req.session.returnTo);
        res.render('login.ejs', { message: req.flash('loginMessage')}); 
    });
    
    
    
    
    
    
    app.get('/closedisplay',isLoggedIn, function(request, response) 
    		{
    			 var spawn = require('child_process').spawn,
    		     py= spawn('python', ['closedisplay.py']);
    			 res.json({"status":"success"});
    		
    		});
    
    app.get('/sendClients',isLoggedIn, function(req, res) 
    		{
    			 var spawn = require('child_process').spawn,
    		     py= spawn('python', ['sendNewConfig.py']);  
    			 res.json({"status":"success"});
    		});
    
    
    app.get('/configClients',isLoggedIn,isAdmin, function(req, res) {


    	
    	var Clients = new Array();
    	var j = 0;
    	var splitStr = new Array();

    	lineReader.eachLine(rad_cli_path, function(line,last) {
      		if(!line.startsWith('#') && !line.startsWith("import")){
                            splitStr = line.split("=");
                            Clients[j] = new Object();
                            Clients[j].ip_addr = splitStr[0];
                            Clients[j].secret = splitStr[1];
                            console.log(splitStr[0] + "," +splitStr[1]);
                            j++;
                    }
    		if(last){
    			
            		res.render('configClients.ejs',{url : configDB.url, clients : Clients});
    		}
    		});

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
            var stream = fs.createWriteStream(rad_cli_path);
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

		    var stream = fs.createWriteStream(rad_cli_path);
		    stream.once('open', function(fd) 
		    {
		    	stream.write(str);
  			    stream.end();
			    res.json({"status":"success"});
		    });

		    console.log(str);
		
	    }

    });
    
    
    
    
    


    app.get('/python',isLoggedIn, function(req, res) {

        // render the page and pass in any flash data if it exists
        //console.log(req.session.returnTo)i;
	var parseJ;
        PythonShell.run('oobmessage.py', options, function (err,results) {
                if (err) console.log (err);
                res.send("Its Successful");
		//parseJ = JSON.parse(results);
                console.log('results:', results);
        });
    });


    // =====================================
    // SIGNUP ==============================
    // =====================================
    app.get('/signup', function(req, res) {

        res.render('signup.ejs', { message: req.flash('signupMessage') });

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
		
		 			res.render('profile.ejs', {
            				user : req.user, userInfo : userDetails, deviceInfo : deviceDetails,  url : configDB.url, message: req.flash('profileMessage') // get the user out of session and pass to template
        				});
				}else{
					db.close();
		 			res.render('profile.ejs', {
            				user : req.user, userInfo : userDetails, deviceInfo : '',  url : configDB.url,  message: req.flash('profileMessage') // get the user out of session and pass to template
        				});
				}
			});
		}else{
			db.close();
		 	res.render('profile.ejs', {
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
