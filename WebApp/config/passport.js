var LocalStrategy   = require('passport-local').Strategy;
var sqlite3 		= require('sqlite3').verbose();
var bcrypt 			= require('bcrypt-nodejs');

// load up the user model
var db;
var configDB = require('./database.js');
var conn_str = configDB.dbPath;


function hashPassword(password) {
	return bcrypt.hashSync(password, bcrypt.genSaltSync(8), null);
}

function validPassword(password,original_password){
	return bcrypt.compareSync(password, original_password);
}

module.exports = function(passport) {

	// =======================================
	// passport session setup ================
	// =======================================
	// required for persistent login sessions	

	passport.serializeUser(function(user, done)
    {
		done(null, user.id);
	});

	// used to deserialize the user
	passport.deserializeUser(function(id, done) 
	{
		db = new sqlite3.Database(conn_str);
		db.get('SELECT id, username, password, isAdmin FROM users WHERE id = ?', id, function(err, row) {

			db.close();
			if (!row) return done(null, false);
			return done(null, row);
		});
	});
	// ========================================
	// LOCAL LOGIN ============================
	// ========================================
	// Using named strategies since we have one for login and one for signup

	passport.use('local-login', new LocalStrategy({
		usernameField : 'email',
		passwordField : 'password',
		passReqToCallback : true // allows to pass back the entire request to the callback
		},
		function(req, email, password, done) { // callback with email and password from our form
		
		// Checking if the user trying to login already exists
		db = new sqlite3.Database(conn_str);
		db.get('SELECT id, username, password, isAdmin FROM users WHERE username = ?', email, function(err, row) {

		db.close();
		if(err) return done(err);
		// if no user is found, return the message
		if (!row){
			return done(null, false, req.flash('loginMessage', 'No user found.')); // req.flash is the way to set flashdata using connect-flash
		}
		// if the user is found but the password is wrong
		if (!validPassword(password,row.password))
		return done(null, false, req.flash('loginMessage', 'Oops! Wrong password.')); // create the loginMessage and save it to session as flashdata
		// all is well, return successful user
		return done(null, row);
		});

}));


	// ======================================
	// LOCAL SIGNUP =========================
	// ======================================

	passport.use('local-signup', new LocalStrategy({
	usernameField : 'email',
	passwordField : 'password',
	passReqToCallback : true // allows us to pass back the entire request to the callback
	},
	function(req, email, password, done) {
	
	// asynchronous
	// User.findOne wont fire unless data is sent back
	process.nextTick(function() 
	{
		// find a user whose email is the same as the forms email
		db = new sqlite3.Database(conn_str);
		db.get('SELECT id FROM users WHERE username = ?', email, function(err, row) 
		{
	
			db.close();
			if(err) return done(err);
			if(row){	
				return done(null, false, req.flash('signupMessage', 'The provided email already used.'));
			}
			if (!row)
			{
				var stmt = db.prepare("INSERT INTO users(username,password) VALUES(?,?)");
				stmt.run(email,hashPassword(password));
				stmt.finalize();
				db.get('SELECT id, username, password, isAdmin FROM users WHERE username = ?', email, function(err, row) 
				{
					if (!row) return done(null, false);
					else return done(null,row);
				});
			}
		});    
	});

}));

};
