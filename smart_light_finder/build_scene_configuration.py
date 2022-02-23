import os
import sys
from pathlib import Path
from collections import defaultdict

import pywemo
import toml
import yaml
from InquirerPy import inquirer
from InquirerPy.base import Choice
from termcolor import colored

from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
from smart_light_finder.hue.topology import get_rooms, get_lights


def main():
  print(colored('looking for hue rooms and devices...', 'green'), file=sys.stderr, end='')
  hue_host = get_hue_host()
  hue_api_key = get_hue_api_key()
  hue_rooms = get_rooms(hue_host, hue_api_key)
  hue_devices_by_id = {
    light['id']: light
    for light in get_lights(hue_host, hue_api_key)
  }
  print(colored('found hue rooms', 'green'), file=sys.stderr)
  hue_rooms_by_name = {room['name']: room for room in hue_rooms}
  wemo_room_configuration = get_wemo_room_configuration()

  room_names = set().union(hue_rooms_by_name.keys(), wemo_room_configuration.keys())
  room_to_configure = inquirer.select(
    message='Which room are we configuring?',
    choices=list(room_names)
  ).execute()
  print(colored(f"great, lets start configuring the {room_to_configure}", 'green'))

  scene_name = inquirer.text(
    message="what should we name this scene?"
  ).execute()

  # see if there's a room configuration file already?
  room_configuration_file_name = f"{room_to_configure.lower()}_scene_configuration.yaml"
  room_configuration_file = Path(room_configuration_file_name)
  room_configuration_file.touch(exist_ok=True)
  with open(room_configuration_file_name, 'r+') as output_file:
    room_configuration = yaml.safe_load(output_file) or {
      'name': room_to_configure,
      'scenes': []
    }

    # see if there's a configuration object that we want to overwrite
    index_of_existing_scene = None
    for index, value in enumerate(room_configuration['scenes']):
      if value['name'] == scene_name:
        index_of_existing_scene = index
        break

    if index_of_existing_scene is not None:
      confirmation = inquirer.confirm(
        message=f"there is already a {scene_name} scene. overwrite it?"
      ).execute()
      if not confirmation:
        exit(0)

    hue_lights_to_configure = [light for light_id, light in hue_devices_by_id.items() if light_id in hue_rooms_by_name[room_to_configure]['lights']]

    hue_device_configuration = build_hue_scene_configuration(hue_lights_to_configure)
    wemo_devices_to_configure = wemo_room_configuration.get(room_to_configure, [])
    wemo_device_configuration = []
    if wemo_devices_to_configure:
      wemo_device_configuration = build_wemo_scene_configuration(wemo_devices_to_configure)

    scene_configuration = {
      "name": scene_name,
      "devices": hue_device_configuration + wemo_device_configuration
    }

    if index_of_existing_scene is not None:
      room_configuration['scenes'][index_of_existing_scene] = scene_configuration
    else:
      room_configuration['scenes'].append(scene_configuration)

    output_file.seek(0)
    output_file.truncate()
    print(colored(f"writing configuration to {room_configuration_file_name}", 'green'))
    yaml.safe_dump(room_configuration, output_file)

def build_hue_scene_configuration(hue_lights_to_configure):
  lights = [
    Choice(light['name'], enabled=light['on'])
    for light in hue_lights_to_configure]
  selected_hue_lights = []
  if not lights:
    print(colored("there are no hue lights in this room", 'red'))
    return []
  else:
    selected_hue_lights = inquirer.checkbox(
      message='Which hue devices do we want to be on? (spacebar to check/uncheck, enter to submit)',
      choices=lights,
    ).execute()

  hue_device_configuration = []
  for light in hue_lights_to_configure:
    light_configuration = {
      'name': light['name'],
      'id': light['id'],
      'type': light['type']
    }
    if light['name'] not in selected_hue_lights:
      light_configuration['on'] = False
    elif light.get('color'):
      light_configuration['color'] = light['color']
    hue_device_configuration.append(light_configuration)
  return hue_device_configuration

def build_wemo_scene_configuration(wemo_devices):
  choices = [
    Choice(device.name, enabled=device.get_state() > 0)
    for device in wemo_devices
  ]

  selected_devices = inquirer.checkbox(
    message='Which wemo devices do we want to be on? (spacebar to check/uncheck, enter to submit)',
    choices=choices
  ).execute()

  return [
    {
      'name': device.name,
      'type': 'wemo_outlet',
      'on': device.name in selected_devices
    }
    for device in wemo_devices
  ]

def get_wemo_room_configuration():
  wemo_room_config_file = os.environ.get('WEMO_ROOM_FILE', 'wemo_rooms.toml')
  print(colored(f"looking for wemo rooms and devices from {wemo_room_config_file}...", 'green'), file=sys.stderr, end='')

  if not os.path.exists(wemo_room_config_file):
    print(colored("it doesn't look like there are any wemo config files", 'red'), file=sys.stderr)
    return {}
  wemo_room_configuration = toml.load(wemo_room_config_file)
  wemo_devices_by_room_name = get_wemo_devices_by_room_name(wemo_room_configuration)
  print(colored('found wemo rooms and devices', 'green'), file=sys.stderr)
  return wemo_devices_by_room_name

def get_wemo_devices_by_room_name(wemo_room_configuration):
  all_devices = pywemo.discover_devices()
  devices_by_room = {}
  devices_by_name = {device.name: device for  device in all_devices}
  for room, device_names in wemo_room_configuration.items():
    devices = [devices_by_name[name] for name in device_names]
    devices_by_room[room] = devices
  return devices_by_room

def get_nanoleaf_configuration(room_name):
  nanoleaf_device_names = os.environ.get('NANOLEAF_DEVICES').split(':')
  nanoleaf_room_prefix = room_name.upper()
  nanoleaf_device = None
  for device_name in nanoleaf_device_names:
    if device_name.startswith(nanoleaf_room_prefix):
      return {
        'name': f"NANOLEAF_{device_name}",
        'host': os.environ.get(f"NANOLEAF_{device_name}_HOST"),
        'token': os.environ.get(f"NANOLEAF_{device_name}_TOKEN")
      }
  return {}


if __name__ == '__main__':
    main()
