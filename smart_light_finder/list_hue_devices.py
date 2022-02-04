from os import environ
from pprint import pprint

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
  host = environ.get('HUE_HOST', default='192.168.86.62');
  api_key = environ.get('HUE_USER', default='')

  rooms = get_rooms(host, api_key)
  lights_by_id = {light['id']: light for light in get_lights(host, api_key)}

  for room in rooms:
    print(f"room: {room['name']}")
    print("  lights:")
    for light_id in room['lights']:
      light = lights_by_id[light_id]

      print(f"    name: {light['name']}, id: {light['id']}")

def get_rooms(host, api_key):
  rooms_response = requests.get(f"https://{host}/clip/v2/resource/room", headers={'hue-application-key': api_key}, verify=False)
  return [build_room_object(entry) for entry in rooms_response.json()['data']]

def get_lights(host, api_key):
  lights_response = requests.get(f"https://{host}/clip/v2/resource/light", headers={'hue-application-key': api_key}, verify=False)
  body = lights_response.json()
  return [build_light_object(entry) for entry in body['data']]

def build_light_object(light_response_entry):
  return {
    'id': light_response_entry['id'],
    'on': light_response_entry['on'],
    'color_capable': 'color' in light_response_entry.keys(),
    'name': light_response_entry['metadata']['name']
  }

def build_room_object(room_response_entry):
  lights = [service['rid'] for service in room_response_entry['services'] if service['rtype'] == 'light']
  return {
    'id': room_response_entry['id'],
    'name': room_response_entry['metadata']['name'],
    'lights': lights
  }