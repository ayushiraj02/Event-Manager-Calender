    # im working on a calendar app with Flask and MySQL, it has features like adding, deleting, and updating events.now i want to connect events list to db by making tables and inserting data into them.  i want to use mysql.connector to connect to the database and create tables. from flask import Flask, render_template, request, redirect, url_for




import mysql.connector
from mysql.connector import Error
from flask import Flask, g
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date
import calendar
import os
from flask import jsonify

load_dotenv()

app = Flask(__name__)

CATEGORY_COLORS = {
        'work': '#ffc107',
        'personal': '#28a745',
        'holiday': '#17a2b8',
        'birthday': '#dc3545'
    }

events = []
print(events,"events[]")
# Function to group dates into ranges
def group_dates(dates):
        dates = sorted(dates)
        grouped = []
        start = end = dates[0]
        for current in dates[1:]:
            if (current - end).days == 1:
                end = current
            else:
                grouped.append((start, end))
                start = end = current
        grouped.append((start, end))
        print(grouped,"grouped")
        # Convert to list of dictionaries
        return grouped



print(os.getenv('MYSQL_USER')) 
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE')
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    return g.db


def fetch_events(year):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, event_title, category, event_date
        FROM events
        WHERE YEAR(event_date) = %s
        ORDER BY event_date
    """, (year,))
    rows = cursor.fetchall()
    cursor.close()

    # Convert to list of event dicts with 'dates' as a list containing single date
    events_list = []
    for row in rows:
        events_list.append({
            'event_title': row['event_title'],
            'category': row['category'],
            'dates': [row['event_date']]
        })
    return events_list



@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()



@app.route('/', methods=['GET'])
def index():
    year = request.args.get('year', default=datetime.now().year, type=int)
    months = []
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        cal = calendar.Calendar(firstweekday=6)  
        weeks = list(cal.itermonthdays(year, month))
        weeks_grouped = [weeks[i:i+7] for i in range(0, len(weeks), 7)]
        months.append({'name': month_name, 'month': month, 'weeks': weeks_grouped})

    events = fetch_events(year)

    event_map = {}
    for event in events:
        for d in event['dates']:
            event_map[d] = event

    return render_template(
        'index.html',
        year=year,
        months=months,
        event_map=event_map,
        category_colors=CATEGORY_COLORS,
        grouped_events=events,
        date=date,
        events=events,
        
    )


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    dates_str = request.args.get('dates')
    if not dates_str:
        return redirect(url_for('index'))
    
    selected_dates = []
    for dt in dates_str.split(','):
        dt = dt.strip()
        try:
            parsed_date = datetime.strptime(dt, '%Y-%m-%d').date()
            selected_dates.append(parsed_date)
        except ValueError:
            continue
    
    if not selected_dates:
        return "No valid dates provided", 400

    if request.method == 'POST':
        event_title = request.form.get('event_title')
        if not event_title:
            return "Event title is required", 400
        
        category = request.form.get('category')
        
        # Use the first date from selected_dates for event_date
        event_date = selected_dates

        db = get_db()
        cursor = db.cursor()
        
        for event_date in selected_dates:
            cursor.execute(
        "INSERT INTO events (event_title, event_date, category) VALUES (%s, %s, %s)",
        (event_title, event_date, category)
    )

        
        db.commit()
        cursor.close()

        return redirect(url_for('index', year=event_date.year))

    # GET request: show form with selected dates and categories
    return render_template('add_event.html', dates=selected_dates, categories=CATEGORY_COLORS)




# @app.route('/delete_event/<int:event_id>', methods=['POST'])
# def delete_event(event_id):
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
#     db.commit()
#     cursor.close()
#     return ('', 204)


@app.route('/delete_event/', methods=['POST'])
def delete_event():
    data = request.get_json()
    print("Raw data:", request.data)
    print("JSON data:", request.get_json())
    if not data or 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    event_id = data['id']
    global events
    events = [event for event in events if event.get('id') != event_id]
    print(f"Deleted event with id: {event_id}")
    return jsonify({'status': 'success'})




@app.route('/update_event', methods=['POST'])
def update_event():
    print(request.form)
    event_id = int(request.form.get('event_id'))
    event_title = request.form.get('event_title')
    category = request.form.get('category')
    print(event_id,"id", "titlt", event_title, category,"-------------------")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE events SET event_title=%s, category=%s WHERE id=%s",
        (event_title, category, event_id)
    )
    print("Event updated:", event_title, category)
    db.commit()
    cursor.close()
    return redirect(url_for('index', year=datetime.now().year))


if __name__ == '__main__':
    app.run(debug=True)



