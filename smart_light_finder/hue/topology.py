import enum

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

HOST = get_hue_host()
KEY = get_hue_api_key()

_COLOR_AND_WHITE_AMBIANCE_NAMES = {
  item.lower() for item in (
    "Extended color light",
    "Hue color Lamp",
    "Hue color candle",
    "Hue color lamp",
    "Hue lightstrip outdoor",
    "Hue lightstrip plus",
    "Hue play"
  )
}

_NON_LAMP_DEVICE_NAMES = {
  item.lower() for item in (
    "Hue dimmer switch",
    "Lutron Aurora",
    "Philips hue"
  )
}

_WHITE_LAMP_NAMES = {"hue white lamp"}

_WHITE_AMBIANCE_LAMP_NAMES = set()

class HueDeviceKind(enum.Enum):
  WHITE_LAMP = 'white_lamp'
  WHITE_AMBIANCE_LAMP = 'white_ambiance_lamp'
  COLOR_AND_WHITE_AMBIANCE_LAMP = 'color_and_white_ambiance_lamp'
  NON_LAMP_DEVICE = 'non_lamp_device'

  def is_color_capable(self):
    return self == HueDeviceKind.COLOR_AND_WHITE_AMBIANCE_LAMP

  @staticmethod
  def from_hue_device_product_name(product_name: str) -> 'HueDeviceKind':
    lowercase_name = product_name.lower()
    if lowercase_name in _COLOR_AND_WHITE_AMBIANCE_NAMES:
      return HueDeviceKind.COLOR_AND_WHITE_AMBIANCE_LAMP
    elif lowercase_name in _WHITE_AMBIANCE_LAMP_NAMES:
      return HueDeviceKind.WHITE_AMBIANCE_LAMP
    elif lowercase_name in _WHITE_LAMP_NAMES:
      return HueDeviceKind.WHITE_LAMP
    elif lowercase_name in _NON_LAMP_DEVICE_NAMES:
      return HueDeviceKind.NON_LAMP_DEVICE
    raise AssertionError(f"{product_name} is not a supported hue product")

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