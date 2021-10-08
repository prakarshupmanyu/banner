from flask import Flask, render_template, request, url_for, redirect

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

    return campaign_id
