# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create date variables
date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
most_recent_date = date[0]
year = int(date[0][:4])
month = int(date[0][5:7])
day = int(date[0][8:10])

# Calculate the date one year from the last date in data set.
year_ago = dt.date(year,month,day) - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Basic Home Page
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; (use format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (use format: YYYY-MM-DD/YYYY-MM-DD)"
    )

# Json Data for precipitation for last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    last_year_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date.between(year_ago,most_recent_date)).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = list(np.ravel(last_year_precipitation))

    return jsonify(all_precipitation)

# Json data for stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations2 = list(np.ravel(stations))

    return jsonify(stations2)

# Json list of temperatures for last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    mvp_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    temp_active_station = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == mvp_station).filter(Measurement.date.between(year_ago,most_recent_date)).all()

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(temp_active_station))

    return jsonify(tobs)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def search_start_date(start):
    session = Session(engine)
    start_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= str(start)).all()
    session.close()

    # Convert list of tuples into normal list
    start_temp2 = list(np.ravel(start_temp))

    return jsonify(start_temp2)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def search_start_end_date(start, end):
    session = Session(engine)
    start_end_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date.between(start,end)).all()
    session.close()

    # Convert list of tuples into normal list
    start_end_temp2 = list(np.ravel(start_end_temp))

    return jsonify(start_end_temp2)

if __name__ == "__main__":
    app.run(debug=True)