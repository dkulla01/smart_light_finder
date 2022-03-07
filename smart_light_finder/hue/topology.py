import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from config import get_hue_host, get_hue_api_key
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

HOST = get_hue_host()
KEY = get_hue_api_key()

def get_rooms(host=HOST, api_key=KEY):
  rooms_response = requests.get(f"https://{host}/clip/v2/resource/room", headers={'hue-application-key': api_key}, verify=False)
  return [build_room_object(entry) for entry in rooms_response.json()['data']]

def get_lights(host=HOST, api_key=KEY):
  lights_response = requests.get(f"https://{host}/clip/v2/resource/light", headers={'hue-application-key': api_key}, verify=False)
  body = lights_response.json()
  return [build_light_object(entry) for entry in body['data']]

def get_scenes(host=HOST, api_key=KEY):
  scenes_response = requests.get(f"https://{host}/clip/v2/resource/scene", headers={'hue-application-key': api_key}, verify=False)
  body = scenes_response.json()

def build_light_object(light_response_entry):
  light_object = {
    'id': light_response_entry['id'],
    'on': light_response_entry['on']['on'],
    'color_capable': 'color' in light_response_entry.keys(),
    'name': light_response_entry['metadata']['name']
  }

  if light_object['color_capable']:
    light_object['type'] = 'hue_white_and_color_ambiance'
    light_object['color'] = {
      'xy': light_response_entry['color']['xy']
    }
  else:
    light_object['type'] = 'hue_white_bulb'
  return light_object

def build_room_object(room_response_entry):
  lights = [service['rid'] for service in room_response_entry['services'] if service['rtype'] == 'light']
  return {
    'id': room_response_entry['id'],
    'name': room_response_entry['metadata']['name'],
    'lights': lights
  }

def build_scenes_object(scene_response_entry):
  if scene_response_entry['group']['rtype'] != 'room':
    raise AssertionError('scenes should belong to rooms')

  return {
    'id': scene_response_entry['id'],
    'room_id': scene_response_entry['group']['rid'],
    'name': scene_response_entry['metadata']['name']
  }