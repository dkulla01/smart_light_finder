import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

HOST = get_hue_host()
KEY = get_hue_api_key()

def get_rooms(host=HOST, api_key=KEY):
  rooms_response = requests.get(f"https://{host}/clip/v2/resource/room", headers={'hue-application-key': api_key}, verify=False)
  nonempty_rooms = filter(has_all_valid_room_fields, rooms_response.json()['data'])
  return [build_room_object(entry) for entry in nonempty_rooms]

def get_scenes(host=HOST, api_key=KEY):
  scenes_response = requests.get(f"https://{host}/clip/v2/resource/scene", headers={'hue-application-key': api_key}, verify=False)
  body = scenes_response.json()

  return[build_scenes_object(entry) for entry in body['data']]

def has_all_valid_room_fields(room_response_entry):
  return room_response_entry['services'] and room_response_entry['children']

def build_room_object(room_response_entry):
  grouped_light_room_id = [
    service['rid']
    for service in room_response_entry['services']
    if service['rtype'] == 'grouped_light'
  ][0]
  return {
    'id': room_response_entry['id'],
    'name': room_response_entry['metadata']['name'],
    'grouped_light_room_id': grouped_light_room_id
  }

def build_scenes_object(scene_response_entry):
  if scene_response_entry['group']['rtype'] != 'room':
    raise AssertionError('scenes should belong to rooms')

  return {
    'id': scene_response_entry['id'],
    'room_id': scene_response_entry['group']['rid'],
    'name': scene_response_entry['metadata']['name'],
  }