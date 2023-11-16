from flask import Flask, request
import os
import requests
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import pymongo
import urllib.parse
from urllib.parse import quote_plus

app = Flask(__name__)

@app.route('/')
def get_env():

    return list_env_vars()

@app.route('/env')
def list_env_vars():
    env_vars = os.environ
    return '\n'.join([f'{key}: {value}' for key, value in env_vars.items()])

@app.route('/env-file')
def list_properties_file():
    properties_file_path = '/etc/app/application.properties'
    try:
        with open(properties_file_path, 'r') as file:
            content = file.read()
        # return content.replace('\n', '<br>')
        return content
    except FileNotFoundError:
        return "Properties file not found."
    except Exception as e:
        return f"An error occurred: {e}"
@app.route('/place/<name>')
def get_location_details(name):
    API_URL_GEOCODING = os.environ.get('API_URL_GEOCODING')
    url = f'{API_URL_GEOCODING}/search?name={name}&count=1&language=en&format=json'
    # url = f'{url_params}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])

        if results:
            first_result = results[0]
            local_timezone = ZoneInfo("Asia/Kolkata")
            current_time_with_timezone = datetime.now(local_timezone)
            formatted_timestamp_with_timezone = current_time_with_timezone.strftime("%Y-%m-%d %H:%M:%S %Z%z")

            success_result = {
                'place': f'{name}',
                'country': first_result.get('country'),
                'latitude': first_result.get('latitude'),
                'longitude': first_result.get('longitude'),
                'temperature (C)': get_current_temperature(first_result.get('latitude'), first_result.get('longitude')),
                'time': formatted_timestamp_with_timezone
            }
            store_json_in_mongodb(success_result)
            return success_result
        else:
            return None
    except requests.RequestException as e:
        print(f"An error occurred while fetching location details: {e}")
        return None

@app.route('/temperature/<latitude>/<longitude>')
def get_current_temperature(latitude, longitude):
    API_URL_WEATHER = os.environ.get('API_URL_WEATHER')
    url = f'{API_URL_WEATHER}/forecast?latitude={latitude}&longitude={longitude}&current=temperature'
    # url = f'{url_params}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_weather = data.get('current', {})
        return current_weather.get('temperature')
    except requests.RequestException as e:
        print(f"An error occurred while fetching temperature: {e}")
        return None

def store_json_in_mongodb(json_data):
    try:
        db_host = os.environ['DB_HOST']
        db_username = os.environ['DB_USERNAME']
        db_password = os.environ['DB_PASSWORD']

        client = pymongo.MongoClient(db_host,username=db_username,password=db_password,authSource='weatherdb',authMechanism='SCRAM-SHA-256')
        db = client.weatherdb  # replace with your database name
        collection = db.temperature  # replace with your collection name
        if isinstance(json_data, str):
            json_data = json.loads(json_data)  # convert string to json if necessary
        json_data = {k: serialize_datetime(v) for k, v in json_data.items()}
        collection.insert_one(json_data)
        print(collection)
        return "JSON data stored successfully"
    except KeyError as e:
        return f"Environment variable not set: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

@app.route('/history/temperature', methods=['GET'])
def get_temperature_data():
    try:
        # Retrieve database connection details from environment variables
        db_host = os.environ['DB_HOST']
        db_name = os.environ['DB_NAME']
        db_username = os.environ['DB_USERNAME']
        db_password = os.environ['DB_PASSWORD']

        client = pymongo.MongoClient(db_host,username=db_username,password=db_password,authSource='weatherdb',authMechanism='SCRAM-SHA-256')

        # Connect to the 'weather' database and 'temperature' collection
        db = client['weatherdb']
        col_temperature = db['temperature']
        # Pagination parameters from URL query
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit

        # Query the collection with pagination
        records = list(col_temperature.find().skip(skip).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for record in records:
            record['_id'] = str(record['_id'])

        return {"data": records}
    
    except KeyError as e:
        return {"error": f"Missing environment variable: {e}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500

def serialize_datetime(value):
    """Convert datetime objects to string."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return value

if __name__ == '__main__':
    app.run(debug=True)
