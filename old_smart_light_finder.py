import json
import os.path
from os import environ
from pprint import pprint
import pywemo

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
  host = environ.get('HUE_HOST', default='192.168.86.62');
  api_key = environ.get('HUE_USER', default='')

  rooms_response = requests.get(f"https://{host}/clip/v2/resource/room", headers={'hue-application-key': api_key}, verify=False)
  rooms = [build_room_object(entry) for entry in rooms_response.json()['data']]
  rooms_by_name = {room['name']: room for room in rooms}

  lights_response = requests.get(f"https://{host}/clip/v2/resource/light", headers={'hue-application-key': api_key}, verify=False)
  body = lights_response.json()
  all_lights = [build_light_object(entry) for entry in body['data']]
  all_lights_by_id = { light['id']: light for light in all_lights}
  questions = [
    {
      'type': 'list',
      'name': 'room',
      'choices': rooms_by_name.keys(),
      'message': 'what room are we configuring?'
    },
    {
      'type': 'checkbox',
      'name': 'lights',
      'choices': lambda answers_so_far: get_light_choices_for_room(answers_so_far, all_lights_by_id, rooms_by_name),
      'message': 'which_lights_are_we_configuring?'
    }
  ]

  answers = prompt(questions)
  pprint(answers)

def get_light_choices_for_room(answers_so_far, lights_by_id, rooms_by_name):
  room_name = answers_so_far['room']
  light_ids_for_room = rooms_by_name[room_name]['lights']
  return [
    {
      'name': lights_by_id[key]['name'],
      'checked':  lights_by_id[key]['on']}
          for key in light_ids_for_room
  ]

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

def get_wemo_outlets():
  path_to_wemo_rooms = environ.get('WEMO_ROOMS_JSON', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                           'wemo_rooms.toml'))
  devices = pywemo.discover_devices()
  print(devices)

if __name__ == '__main__':
    # main()
    get_wemo_outlets()