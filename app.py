# Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database 
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


# Flask
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    all_precipitation=[]
    for precip in results:
        precip_dict = {}
        precip_dict["date"] = precip.date
        precip_dict["prcp"] = precip.prcp
        all_precipitation.append(precip_dict)

    return jsonify(all_precipitation)
	
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).all()

    all_stations=[]
    for row in results:
        station_dict = {}
        station_dict["station"] = row[0]
        station_dict["count"] = row[1]
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    last_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    for date in last_date:
        split_last_date=date.split('-')
    
    last_year=int(split_last_date[0])
    last_month=int(split_last_date[1])
    last_day=int(split_last_date[2])
    
    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date>=query_date).\
                order_by(Measurement.date).all()

    last_12months_tobs=[]
    for row in results:
        tobs_dict = {}
        tobs_dict["date"] = row.date
        tobs_dict["station"] = row.tobs
        last_12months_tobs.append(tobs_dict)

    return jsonify(last_12months_tobs)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date): 
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):

    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)