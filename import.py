import os
import csv
from flask import Flask, session, redirect, url_for, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_mysqldb import MySQL

app = Flask(__name__)

# Set up database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

db = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


def main():
	f = open("students.csv")
	allStudents = csv.reader(f)
	for password, name, email in allStudents:
		db.execute("INSERT INTO students (password, name, email) VALUES (:password, :name, :email)", 
			{"password": password, "name": name, "email": email})
		print(f"Added {name} whos email is {email} passsword is {password}")
	db.commit()


if __name__ == "__main__":
	main()
