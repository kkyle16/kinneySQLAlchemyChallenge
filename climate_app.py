from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import pandas as pd


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)

##########################################################################################################################
# Functions to be used in the Routes

# Provides a list of available routes.
def route_list():
    routes = ["/", "/api/v1.0/precipitation", "/api/v1.0/stations", "/api/v1.0/tobs", "/api/v1.0/<start>", "/api/v1.0/<start>/<end>"]
    listing = f"Available Routes:<br>"
    for route in routes:
        listing = listing + f"{route}<br>"
    return listing

# Finds the most recent date in db and the date one year prior. 
def one_year_ago():
    session = Session(engine)

    results = session.query(measurement.date).\
        order_by(measurement.date.desc()).all()
    dates = [i for i, in results]
    one_year_ago = dt.datetime.strptime(dates[0], "%Y-%m-%d") - dt.timedelta(days=365)
    one_year_ago = dt.datetime.strftime(one_year_ago, "%Y-%m-%d")
    session.close()

    return dates[0], one_year_ago

# Finds temperature min, max, and avg for given date(s)
def temp_dates(start, end):
    session = Session(engine)
    if end == "no end date":
        results = session.query(measurement.tobs).\
            filter(measurement.date >= start)
    else:
        results = session.query(measurement.tobs).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end)
    session.close()

    df = pd.DataFrame(results, columns = ["tobs"])
    
    temp_summary = []
    temp_dict = {}
    temp_dict["min_temp"] = df["tobs"].min()
    temp_dict["max_temp"] = df["tobs"].max()
    temp_dict["avg_temp"] = df["tobs"].mean()
    temp_summary.append(temp_dict)
    
    return temp_summary

##############################################################################################
# Routes


@app.route("/")
def home():
    print("Home Page")
    return (f"Welcome to the Climate App<br>" 
            f"-----------------------------------<br>"
            f"{route_list()}")


@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    # Query that calls the one_year_ago() function to find the latest date and the date one year prior
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago()[1]).\
        filter(measurement.date <= one_year_ago()[0])
    
    session.close()

    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # results = session.query(measurement.station).distinct().all()
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    station_data = []
    for station, name, latitude, longitude, elevation in results:
        stat_dict = {}
        stat_dict["station"] = station
        stat_dict["name"] = name
        stat_dict["latitude"] = latitude
        stat_dict["longitude"] = longitude
        stat_dict["elevation"] = elevation
        station_data.append(stat_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    # Finds the most active station to use in the next query
    activity_results = session.query(measurement.station, measurement.tobs)
    station_count_df = pd.DataFrame(activity_results, columns = ["station", "tobs"])
    most_active = station_count_df["station"].mode()[0]

    # Finds the temperature data for the most active station during a 1 year span
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year_ago()[1]).\
        filter(measurement.date <= one_year_ago()[0]).\
        filter(measurement.station == most_active)
    session.close()

    temp_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start(start):
    # end is a dummy variable
    end = "no end date"
    return jsonify(temp_dates(start, end))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    return jsonify(temp_dates(start, end))
    
if __name__ == "__main__":
    app.run(debug=True)