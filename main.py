import json
import requests
import folium
import os
from flask import Flask
from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_min_coordinates(data):
    return data['distance']


def my_map():
    with open('index.html', encoding='utf-8') as file:
        return file.read()


if __name__ == '__main__':
    load_dotenv()
    apikey = os.getenv('APIKEY')
    user_coordinates_input = input('Где вы находитесь? ')
    user_coordinates = fetch_coordinates(apikey, user_coordinates_input)

    with open('coffee.json', 'r', encoding='CP1251') as my_file:
        coffee_json = my_file.read()

    coffees = json.loads(coffee_json)

    new_coffees = []
    for i in range(len(coffees)):
        temp_coffees = dict()
        temp_coffees['title'] = coffees[i]['Name']
        temp_coffees['distance'] = distance.distance(user_coordinates[::-1], (coffees[i]['geoData']['coordinates'])[::-1]).km
        temp_coffees['latitude'] = coffees[i]['geoData']['coordinates'][1]
        temp_coffees['longitude'] = coffees[i]['geoData']['coordinates'][0]
        new_coffees.append(temp_coffees)

    coffees_map = folium.Map(location=user_coordinates[::-1], tiles="cartodb positron")

    coffees_min = (sorted(new_coffees, key=get_min_coordinates))[0:5]

    for i in range(len(coffees_min)):
        location_coordinates = []
        location_coordinates.append(coffees_min[i]['latitude'])
        location_coordinates.append(coffees_min[i]['longitude'])

        folium.Marker(
            location=location_coordinates,
            tooltip="Click me!",
            popup=coffees_min[i]['title'],
            icon=folium.Icon(),
        ).add_to(coffees_map)

    coffees_map.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'map', my_map)
    app.run('0.0.0.0')