import redis, random, datetime, math, mysql.connector
from flask import Flask, render_template, request, url_for, redirect


db_connection = mysql.connector.connect(host="mysql", user="user", password="password", database="banner")
db_cursor = db_connection.cursor()

app = Flask(__name__)
redis = redis.Redis(host='redis', port=6379, db=0)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/campaigns', methods=['POST'])
def get_campaign():
    return redirect(url_for('show_campaign_banners', campaign_id=request.form['campaign_id']))


@app.route('/campaigns/<campaign_id>')
def show_campaign_banners(campaign_id):
    # Validate the Campaign ID
    if not campaign_id.isnumeric() or int(campaign_id) <= 0:
        error = "Campaign ID is supposed to be a single positive integer value. Please enter again."
        return render_template('home.html', error=error)

    # generate and execute the SQL according to time
    data = get_campaign_data(campaign_id)

    # if campaign not found
    if len(data) == 0:
        error = "Campaign ID not found. Please enter a different ID."
        return render_template('home.html', error=error)

    banners = compute_banners_to_show(data)
    return render_template('banners.html', banners=banners)


def get_data_from_redis(campaign_id, hour_quarter):
    redis_key = str(hour_quarter) + "_" + str(campaign_id)
    return redis.get(redis_key)


def set_data_in_redis(campaign_id, hour_quarter, data):
    redis_key = str(hour_quarter) + "_" + str(campaign_id)
    redis.set(redis_key, bytes(str(data), 'utf-8'))


def get_campaign_data(campaign_id):
    now = datetime.datetime.now()
    hour_quarter = math.floor(now.minute / 15) + 1
    data = get_data_from_redis(campaign_id, hour_quarter)
    if data is not None:
        return list(eval(data.decode('utf-8')))

    table = "q" + str(hour_quarter) + "_campaign_banners"
    sql = "SELECT `X`, `banner_id`, `total_revenue`, `total_clicks`, `order` FROM " + table + " where campaign_id = " \
          + campaign_id + " order by total_revenue desc, total_clicks desc"
    db_cursor.execute(sql)
    data = db_cursor.fetchall()
    set_data_in_redis(campaign_id, hour_quarter, data)
    return data


def get_banners_for_high_conversion_campaigns(data):
    banners = []
    for row in data:
        # Show banner only if revenue exists
        if row[2] > 0:
            banners.append(row[1])

    return banners


def get_banners_for_low_conversion_campaigns(data, X):
    banners = []
    idx = 0
    max_banners_to_show = 5
    while idx < X:
        banners.append(data[idx][1])
        idx += 1

    num_banners_to_add = max_banners_to_show - len(banners)
    while num_banners_to_add > 0 and idx < len(data):
        if data[idx][3] > 0:
            banners.append(data[idx][1])
            num_banners_to_add -= 1
            idx += 1
        else:
            break

    # You can uncomment the following if you want to fill up the banner count to 5 by adding no rev no click banners
    # from within the campaign
    ''' 
    data_no_rev_no_clicks = data[idx:]
    random.shuffle(data_no_rev_no_clicks)
    idx = 0
    while num_banners_to_add > 0 and idx < len(data_no_rev_no_clicks):
        banners.append(data_no_rev_no_clicks[idx][1])
        num_banners_to_add -= 1
        idx += 1
    '''
    return banners


def get_banners_for_no_conversion_campaigns(data):
    banners = []
    idx = 0
    num_banners_to_add = 5
    while num_banners_to_add > 0 and idx < len(data):
        if data[idx][3] > 0:
            banners.append(data[idx][1])
            num_banners_to_add -= 1
            idx += 1
        else:
            break

    # Fill up banners from within the campaign when we run out of banners with clicks
    data_no_rev_no_clicks = data[idx:]
    random.shuffle(data_no_rev_no_clicks)
    idx = 0
    num_banners_to_add = 5 - len(banners)
    while num_banners_to_add > 0 and idx < len(data_no_rev_no_clicks):
        banners.append(data_no_rev_no_clicks[idx][1])
        num_banners_to_add -= 1
        idx += 1

    # Fill up random banners
    while num_banners_to_add > 0:
        banner = str(random.randint(100, 500))
        if banner not in banners:
            banners.append(banner)
            num_banners_to_add -= 1
    return banners


def compute_banners_to_show(data):
    banners = []
    X = data[0][0]

    # if X >= 10, only the top 10 banners based on revenue would be fetched as only those were pushed to MySql from
    # the spark job. Hence, for X >= 5 we only need to pick those banners which have a valid revenue > 0, ignore clicks
    if X >= 5:
        banners = get_banners_for_high_conversion_campaigns(data)

    # for X = 1,2,3,4 we need to show 5 banners based on revenue first, then clicks. If the total banners even after
    # that is < 5, then we don't do anything else. I will leave some code commented which would fill up the banner count
    # to 5 by including random banners from within that campaign
    elif X > 0:
        banners = get_banners_for_low_conversion_campaigns(data, X)

    else:  # X == 0
        banners = get_banners_for_no_conversion_campaigns(data)

    random.shuffle(banners)
    return banners
