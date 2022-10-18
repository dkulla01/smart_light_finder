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
  return [build_room_object(entry) for entry in rooms_response.json()['data']]

def get_lights(host=HOST, api_key=KEY):
  lights_response = requests.get(f"https://{host}/clip/v2/resource/light", headers={'hue-application-key': api_key}, verify=False)
  body = lights_response.json()
  devices_by_device_id = {device['id']: device for device in get_devices(host, api_key)}
  light_objects = []
  for entry in body['data']:
    owner = entry['owner']
    if owner['rtype'] != 'device':
      raise AssertionError('lights must be owned by devices')
    parent_device = devices_by_device_id[owner['rid']]
    if not parent_device:
      raise AssertionError(f"unable to find the parent device for {entry}")
    light_objects.append(build_light_object(entry, parent_device))
  return light_objects

def get_scenes(host=HOST, api_key=KEY):
  scenes_response = requests.get(f"https://{host}/clip/v2/resource/scene", headers={'hue-application-key': api_key}, verify=False)
  body = scenes_response.json()
  # decorate the lights in the scenes with the HueDeviceKind
  lights = get_lights(host, api_key)
  light_ids_to_light_kind = {light['id']: light['kind'] for light in lights}
  return[build_scenes_object(entry, light_ids_to_light_kind) for entry in body['data']]

def get_devices(host=HOST, api_key=KEY):
  devices_response = requests.get(f"https://{host}/clip/v2/resource/device", headers={'hue-application-key': api_key}, verify=False)
  body = devices_response.json()
  return [build_hue_device_object(entry) for entry in body['data']]

def build_light_object(light_response_entry, parent_device):
  hue_device_kind = parent_device['kind']
  light_object = {
    'id': light_response_entry['id'],
    'on': light_response_entry['on']['on'],
    'kind': hue_device_kind.value,
    'name': light_response_entry['metadata']['name']
  }

  if hue_device_kind == HueDeviceKind.COLOR_AND_WHITE_AMBIANCE_LAMP:
    light_object['color'] = {
      'xy': light_response_entry['color']['xy']
    }
  return light_object

def build_light_object_from_action_object(action_object_entry, light_ids_to_light_kind):

  light_id = action_object_entry['target']['rid']
  hue_device_kind = light_ids_to_light_kind[light_id]
  light_object = {
    'id': light_id,
    'on': action_object_entry['action']['on']['on'],
    'kind': hue_device_kind
  }

  if not light_object['on']:
    return light_object

  has_xy_color = action_object_entry['action'].get('color') and \
                 action_object_entry['action']['color'].get('xy')
  has_mirek_color_temperature = action_object_entry['action'].get('color_temperature') and \
                                action_object_entry['action']['color_temperature'].get('mirek')
  if hue_device_kind == HueDeviceKind.COLOR_AND_WHITE_AMBIANCE_LAMP.value:
    if has_xy_color:
      light_object['color'] = {
        'xy': action_object_entry['action']['color']['xy']
      }
    elif has_mirek_color_temperature:
      light_object['color'] = {
        'mirek': action_object_entry['action']['color_temperature']['mirek']
      }
    else:
      raise AssertionError(f"COLOR_AND_WHITE_AMBIANCE bulb must have either an XY color or a mirek color temperature")

  return light_object

def build_room_object(room_response_entry):
  lights = [service['rid'] for service in room_response_entry['services'] if service['rtype'] == 'light']
  return {
    'id': room_response_entry['id'],
    'name': room_response_entry['metadata']['name'],
    'lights': lights
  }

def build_scenes_object(scene_response_entry, light_ids_to_light_kind):
  if scene_response_entry['group']['rtype'] != 'room':
    raise AssertionError('scenes should belong to rooms')

  return {
    'id': scene_response_entry['id'],
    'room_id': scene_response_entry['group']['rid'],
    'name': scene_response_entry['metadata']['name'],
    'devices': get_devices_in_scene(scene_response_entry, light_ids_to_light_kind)
  }

def build_hue_device_object(device_response_entry):
  """hue devices include lights, switches, and even the hub itself. We
  really only care about lights when building this configuration, but we
  should get some data for the lights' parent device objects to know
  more about whether this device is color capable or not"""

  return {
    'id': device_response_entry['id'],
    'name': device_response_entry['metadata']['name'],
    'kind': HueDeviceKind.from_hue_device_product_name(device_response_entry['product_data']['product_name'])
  }

def get_devices_in_scene(scene_response_entry, light_ids_to_light_kind):
  return [
    build_light_object_from_action_object(action_object, light_ids_to_light_kind)
    for action_object
    in scene_response_entry['actions']
  ]