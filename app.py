from flask import Flask
import os
import requests
import json

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
            return {
                'name': f'{name}',
                'country': first_result.get('country'),
                'latitude': first_result.get('latitude'),
                'longitude': first_result.get('longitude'),
                'temperature (C)': get_current_temperature(first_result.get('latitude'), first_result.get('longitude'))
            }
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
        
if __name__ == '__main__':
    app.run(debug=True)
