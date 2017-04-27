import sqlite3

# Open database connection
connection_string = "slackbotdb.cnobenweteje.us-west-1.rds.amazonaws.com:3306"
#db = mysqldb.connect("slackbotdb.cnobenweteje.us-west-1.rds.amazonaws.com:3306","master","master123","slackbotdb" )
db = sqlite3.connect(connection_string)

# disconnect from server
db.close()