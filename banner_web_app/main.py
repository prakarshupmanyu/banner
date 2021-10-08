from flask import Flask, render_template, request, url_for, redirect
import mysql.connector


db_connection = mysql.connector.connect(host="mysql", user="user", password="password", database="banner")
db_cursor = db_connection.cursor()

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/campaigns', methods=['POST'])
def get_campaign():
    return redirect(url_for('get_specific_campaign', campaign_id=request.form['campaign_id']))


@app.route('/campaigns/<campaign_id>')
def get_specific_campaign(campaign_id):
    if not campaign_id.isnumeric() or int(campaign_id) <= 0:
        error = "Campaign ID is supposed to be a single positive integer value. Please enter again."
        return render_template('home.html', error=error)

    table = "q1_campaign_banners"
    sql = "SELECT X FROM " + table + " where campaign_id = " + campaign_id
    print(sql)
    db_cursor.execute(sql)
    result = db_cursor.fetchall()
    num_converted_banners = result[0][0]

    return str(result[0][0])
