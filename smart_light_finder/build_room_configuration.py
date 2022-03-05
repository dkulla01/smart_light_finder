import sys

from InquirerPy import inquirer
from termcolor import colored

from hue.topology import get_rooms, get_scenes
from smart_light_finder.wemo_topology import load_wemo_room_configuration


def main():
  print(colored('Looking for hue rooms, scenes, and devices...', 'green'), file=sys.stderr, end='')
  hue_rooms = get_rooms()
  hue_rooms_by_name = {room['name']: room for room in hue_rooms }
  hue_scenes = get_scenes()
  print(colored('found hue rooms and scenes', 'green'), file=sys.stderr)
  wemo_room_configuration = load_wemo_room_configuration()

  room_to_configure = inquirer.select(
    message='Which room are we configuring?',
    choices=sorted(list(hue_rooms_by_name.keys()))
  ).execute()
  selected_room_id = hue_rooms_by_name[room_to_configure]['id']
  scenes_in_this_room = filter(lambda scene: scene['room_id'] == selected_room_id, hue_scenes)



if __name__ == '__main__':
    main()
