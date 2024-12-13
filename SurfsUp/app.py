# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()
    
    result = {data[0]: data[1] for data in precipitation_data}
    
    return jsonify(result)

@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station).all()

    result = [station[0] for station in station_list]

    return jsonify(result)

@app.route("/api/v1.0/tobs")
def tobs():
    active_station_id = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    latest_date = session.query(func.max(Measurement.date)).filter(Measurement.station == active_station_id).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    one_year_ago = latest_date - dt.timedelta(days=365)

    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == active_station_id)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    result = [{"date": data[0], "temperature": data[1]} for data in tobs_data]

    return jsonify(result)

@app.route("/api/v1.0/<start>")
def date_start(start):

    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    temps = (
        session.query(
            func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)
        )
        .filter(Measurement.date >= start_date)
        .all()
    )
    
    result = {
        "Start Date": start_date.strftime('%Y-%m-%d'),
        "TMIN": temps[0][0],
        "TAVG": temps[0][1],
        "TMAX": temps[0][2]
    }
    
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    temps = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        )
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )

    result = {
        "Start Date": start_date.strftime('%Y-%m-%d'),
        "End Date": end_date.strftime('%Y-%m-%d'),
        "TMIN": temps[0][0],
        "TAVG": temps[0][1],
        "TMAX": temps[0][2]
    }

    return jsonify(result)
        

if __name__ == '__main__':
    app.run(debug=True)