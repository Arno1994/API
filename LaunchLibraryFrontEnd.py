# This code is made to create a frontend to display the data retrieved from the Launch Library 2 API
# Import required packages
from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# Function to execute SQL query and fetch data from postgres data container
def execute_query(sql):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port='5432'
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    # SQL query to fetch all the data from the database
    sql_query = "SELECT * FROM launch_table;"
    # Execute the SQL query
    results = execute_query(sql_query)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)