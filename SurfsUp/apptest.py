# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

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
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> YYYY-MM-DD (Start date)<br/>"
        f"/api/v1.0/<start>/<end> YYYY-MM-DD/YYYY-MM-DD (Start/End date) <br/>"
        
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    # Query code from prc analysis in climate_starter.ipynb file
    most_recent_date = dt.date(2017, 8,23)
    prev_year = most_recent_date - dt.timedelta(days=365)
    data_prcp = session.query(Measurement.date, Measurement.prcp)\
            .filter(Measurement.date >= prev_year).all()
    session.close()
 # Convert to a dictionary using Date as the key and PRCP as the value
    prcp_dict = {}
    for date, prcp in data_prcp:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)

# Stations
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
# Return a JSON list of stations from the dataset
    results = session.query(Station.station).all()
    session.close()

    station_list = list(np.ravel(results))

    return jsonify(station_list)


# Tobs
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
# Query dates & temperatures observations of the most active station
#   for the previous year of data
    
    last12_months = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station=='USC00519281')\
                        .filter(Measurement.date >='2016-08-23').all()
    session.close()

    tobs_list = []
    for date, tobs in last12_months:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        tobs_dict["date"] = date
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


# Start
@app.route("/api/v1.0/<start>")
def temp_start(start):

    session = Session(engine)
    # Query min, avg, max temp for all dates greater than or equal to start date
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                              func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in temp_data:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min_temp
        temp_dict["Average Temperature"] = avg_temp
        temp_dict["Maximum Temperature"] = max_temp
        temps.append(temp_dict)

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):
    
    session = Session(engine)
    # Query min, avg, max temp for dates from the start date to the end date,inclusive.
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                              func.max(Measurement.tobs)).filter(Measurement.date >= start)\
                              .filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in temp_data:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min_temp
        temp_dict["Average Temperature"] = avg_temp
        temp_dict["Maximum Temperature"] = max_temp
        temps.append(temp_dict)
    
    return jsonify(temps)




if __name__ == '__main__':
    app.run(debug=True)



