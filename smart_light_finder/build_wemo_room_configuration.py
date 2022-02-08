from collections import defaultdict

import toml

from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
from smart_light_finder.hue.topology import get_rooms

from InquirerPy import inquirer
import pywemo

OUTLET_DEVICE_TYPES = {'Switch', 'OutdoorPlug'}

def main():
  hue_rooms = get_rooms(get_hue_host(), get_hue_api_key())
  room_names = [room['name'] for room in hue_rooms]

  wemo_devices = pywemo.discover_devices()
  wemo_outlets = [device.name for device in wemo_devices if device.device_type in OUTLET_DEVICE_TYPES]
  outlets_by_room = defaultdict(list)
  for outlet in wemo_outlets:
    room = inquirer.select(
      message=f"what room is the ** {outlet} ** outlet in?",
      choices=room_names
    ).execute()

    outlets_by_room[room].append(outlet)

  print("here is the output...")
  print(toml.dumps(outlets_by_room))


if __name__ == '__main__':
    main()