import sys

from InquirerPy import inquirer
from InquirerPy.base import Choice
from termcolor import colored

from hue.topology import get_rooms, get_scenes
from smart_light_finder.nanoleaf import get_device_status, list_scene_names
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
  scenes_in_this_room = list(filter(lambda scene: scene['room_id'] == selected_room_id, hue_scenes))

  scenes_by_name = {scene['name']: scene for scene in scenes_in_this_room}
  scene_choices = sorted(scenes_by_name.keys())

  selected_scenes = inquirer.checkbox(
    message="Which scenes should we add to this room?",
    choices=scene_choices
  ).execute()

def build_scene_configuration(hue_scene, wemo_devices, nanoleaf_devices):
  done_configuring = False
  while not done_configuring:
    any_wemo_devices = inquirer.select(
      message="Should any wemo devices be on in this scene?",
      choices=["Yes", "No"]
    ).execute()
    if any_wemo_devices:
      # figure out which wemo devices should be on
      pass
    else:
      # mark all of the wemo devices as off
      pass

def build_wemo_device_configuration_for_scene(wemo_devices):
  if not wemo_devices:
    return []
  wemo_device_names = sorted([device.name for device in wemo_devices])
  any_wemo_devices = inquirer.select(
    message="Should any WeMo devices be on in this scene?",
    choices=["Yes", "No"]
  ).execute()
  if not any_wemo_devices:
    return [
      {
        'name': device.name,
        'type': 'wemo_outlet',
        'on': False
      }
      for device in wemo_devices
    ]
  selected_wemo_devices = set(
    inquirer.checkbox(
      message="Which WeMo devices should be on?",
      choices=sorted(wemo_device_names)
    ).execute()
  )
  return [
    {
      'name': device.name,
      'type': 'wemo_outlet',
      'on': device.name in selected_wemo_devices
    }
    for device in wemo_devices
  ]



def build_nanoleaf_device_configuration_for_scene(nanoleaf_devices):
  if not nanoleaf_devices:
    return []
  any_nanoleaf_devices = inquirer.select(
    message='Should any Nanoleaf devices be on in this scene?',
    choices=['Yes', 'No']
  ).execute()
  if not any_nanoleaf_devices:
    return [
      {
        'name': device.name,
        'on': False,
        'type': 'nanoleaf_light_panels'
      }
      for device in nanoleaf_devices
    ]
  nanoleaf_configuration = []
  nanoleaf_device_names = sorted(device['name'] for device in nanoleaf_devices)
  selected_nanoleaf_devices = set(
    inquirer.checkbox(
      message='Which Nanoleaf devices should be on?',
      choices=nanoleaf_device_names
    ).execute()
  )
  for device_name in nanoleaf_device_names:
    if device_name not in selected_nanoleaf_devices:
      nanoleaf_configuration.append({
        'name': device_name,
        'on': False
      })
      break
    current_device_status = get_device_status(device_name)
    current_scene = current_device_status['color']['effect']
    choices = [
      Choice(scene, enabled=scene == current_scene)
      for scene in list_scene_names(device_name)
    ]
    effect = inquirer.select(
      message='Which Nanoleaf scene should be on?',
      choices=choices
    ).execute()

    nanoleaf_configuration.append({
      'name': device_name,
      'on': True,
      'effect': effect
    })
  return nanoleaf_configuration





if __name__ == '__main__':
    main()
