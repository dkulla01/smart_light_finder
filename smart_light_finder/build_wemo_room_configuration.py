from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
from smart_light_finder.hue.topology import get_rooms

import pywemo

def main():
  hue_rooms = get_rooms(get_hue_host(), get_hue_api_key())
  room_names = [room['name'] for room in hue_rooms]

  pywemo.discover_devices()

  print(f"rooms: {room_names}")
