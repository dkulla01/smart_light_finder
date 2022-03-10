import os
import sys
import time
from collections import defaultdict
from termcolor import colored

import toml

from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
from smart_light_finder.hue.topology import get_rooms

from InquirerPy import inquirer
import pywemo

OUTLET_DEVICE_TYPES = {'Switch', 'OutdoorPlug'}
OMIT_FROM_CONFIGURATION = 'Omit from configuration'

def main():
  print(colored("looking up hue room configuration...", 'green'), file=sys.stderr)
  hue_rooms = get_rooms(get_hue_host(), get_hue_api_key())
  room_names = [room['name'] for room in hue_rooms]
  while True:
    newline_separated_room_names = '\n'.join([f"  {room}" for room in room_names])
    additional_rooms_prompt = f"""\
Here are the rooms we know about so far:
{newline_separated_room_names}
Are there any more rooms we should know about? Enter the new room name, or press enter to continue on to configuring."""
    new_room_name = inquirer.text(
      message=additional_rooms_prompt
    ).execute()

    if not new_room_name:
      break
    elif new_room_name in room_names:
      print(colored(f"we already have a `{new_room_name}`", 'red'), file=sys.stderr)
    else:
      room_names.append(new_room_name)

  room_names.append(OMIT_FROM_CONFIGURATION)
  print(colored("looking for wemo devices...", 'green'), file=sys.stderr)
  wemo_devices = pywemo.discover_devices()
  wemo_outlets = [device.name for device in wemo_devices if device.device_type in OUTLET_DEVICE_TYPES]
  outlets_by_room = defaultdict(list)
  for outlet in wemo_outlets:
    room = inquirer.select(
      message=f"What room is the ** {outlet} ** outlet in?",
      choices=room_names
    ).execute()
    if room == OMIT_FROM_CONFIGURATION:
      continue
    outlets_by_room[room].append(outlet)

  timestamp = int(time.time() * 1000)
  filename = f"wemo_rooms_{timestamp}.toml"
  print(f"printing the following configuration to {colored(filename, 'green')}:", file=sys.stderr)
  toml_output = toml.dumps(outlets_by_room)
  print(toml_output)

  with open(filename, "w+") as output_file:
    print(toml_output, file=output_file)

def load_wemo_room_configuration():
  wemo_room_config_file = os.environ.get('WEMO_ROOM_FILE', 'wemo_rooms.toml')
  print(colored(f"Looking for wemo rooms and devices from {wemo_room_config_file}...", 'green'), file=sys.stderr, end='')

  if not os.path.exists(wemo_room_config_file):
    print(colored("It doesn't look like there are any wemo config files", 'red'), file=sys.stderr)
    return {}
  wemo_room_configuration = toml.load(wemo_room_config_file)
  wemo_devices_by_room_name = _get_wemo_devices_by_room_name(wemo_room_configuration)
  print(colored('Found wemo rooms and devices', 'green'), file=sys.stderr)
  return wemo_devices_by_room_name

def _get_wemo_devices_by_room_name(wemo_room_configuration):
  all_devices = pywemo.discover_devices()
  devices_by_room = {}
  devices_by_name = {device.name: device for device in all_devices}
  for room, device_names in wemo_room_configuration.items():
    devices = [devices_by_name[name] for name in device_names]
    devices_by_room[room] = devices
  return devices_by_room

if __name__ == '__main__':
    main()
