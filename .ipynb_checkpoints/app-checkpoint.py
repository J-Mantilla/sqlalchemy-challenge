# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate API<br>"
        f"Available API Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt; (enter as YYYY-MM-DD)<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (enter as YYYY-MM-DD/YYYY-MM-DD)<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Calculate the date one year ago from today
    prev_year = dt.date.today() - dt.timedelta(days=365)
    
    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation_dict = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Query stations
    station_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    # Create a dictionary for each station and append to a list
    stations_list = []
    for station, name, latitude, longitude, elevation in station_results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_dict['Latitude'] = latitude
        station_dict['Longitude'] = longitude
        station_dict['Elevation'] = elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Query temperature observations for the most active station from the last year
    prev_year = dt.date.today() - dt.timedelta(days=365)
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all()
    session.close()

    # Create a dictionary for temperature observations and append to a list
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Tobs'] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    # Query temperature statistics from the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    # Create a dictionary to hold the results
    stats_dict = {
        "Start Date": start,
        "Lowest Temperature": results[0][0],
        "Maximum Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    # Query temperature statistics between start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Create a list of dictionaries for temperature statistics
    temp_stats = []
    for min_temp, avg_temp, max_temp in results:
        temp_dict = {}
        temp_dict['Min Temperature'] = min_temp
        temp_dict['Avg Temperature'] = avg_temp
        temp_dict['Max Temperature'] = max_temp
        temp_stats.append(temp_dict)

    return jsonify(temp_stats)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
