from flask import Flask, render_template, request, redirect, url_for
import calendar
from datetime import datetime, date
app = Flask(__name__)
CATEGORY_COLORS = {
    'work': '#ffc107',
    'personal': '#28a745',
    'holiday': '#17a2b8',
    'birthday': '#dc3545'
}
events = []
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
    return grouped
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
    event_map = {}
    grouped_events = []
    for event in events:
            if any(d.year == year for d in event['dates']):
                for d in event['dates']:
                    if d.year == year:
                        event_map[d] = event 
                grouped_events.append(event)
    grouped_events = [event for event in events if any(d.year == year for d in event['dates'])]
    return render_template(
    'index.html',
    year=year,
    months=months,
    event_map=event_map,
    category_colors=CATEGORY_COLORS,
    grouped_events=grouped_events,
    date=date,
    events=events
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
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        events.append({'dates': selected_dates, 'title': title, 'category': category})
        return redirect(url_for('index', year=selected_dates[0].year))
    print("Events after adding:", events)
    return render_template('add_event.html', dates=selected_dates, categories=CATEGORY_COLORS)
@app.route('/update_event', methods=['POST'])
def update_event():
    idx = int(request.form.get('event_index'))
    title = request.form.get('title')
    category = request.form.get('category')
    if 0 <= idx < len(events):
        events[idx]['title'] = title
        events[idx]['category'] = category
    return redirect(url_for('index', year=datetime.now().year))
@app.route('/delete_event/<int:idx>', methods=['POST'])
def delete_event(idx):
    if 0 <= idx < len(events):
        events.pop(idx)
    return ('', 204) 
if __name__ == '__main__':
    app.run(debug=True)























    
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

    def get_db():
        if 'db' not in g:
            try:
                g.db = mysql.connector.connect(
                    host=app.config['MYSQL_HOST'],
                    user=app.config['MYSQL_USER'],
                    password=app.config['MYSQL_PASSWORD'],
                    database=app.config['MYSQL_DB']
                )
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                raise
        return g.db

    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)