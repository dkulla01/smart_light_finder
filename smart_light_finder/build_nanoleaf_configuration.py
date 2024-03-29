import argparse
import sys
from os import path

import yaml
from InquirerPy import inquirer
from termcolor import cprint

from smart_light_finder.inquirepy_util import YES_OR_NO_CHOICES
from smart_light_finder.nanoleaf import get_all_nanoleaf_device_names, list_scene_names, get_device_status
from smart_light_finder.termcolor_util import Color


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--path', help="path to directory to place wemo room configuration file")
  arguments = parser.parse_args()
  configuration_dir = arguments.path or path.dirname(path.abspath(__file__))

  device_names = get_all_nanoleaf_device_names()
  device_to_configure = inquirer.select(
    message='Which nanoleaf device are we configuring?',
    choices=device_names
  ).execute()

  device_configuration_file_name = f"{device_to_configure.replace(' ', '_').lower()}_scene_configuration.yaml"
  device_configuration_destination_file = path.join(configuration_dir, device_configuration_file_name)
  if path.exists(device_configuration_destination_file):
    overwrite_existing_config = inquirer.select(
      message=f"A configuration for {device_to_configure} already exists. Overwrite it?",
      choices=YES_OR_NO_CHOICES
    ).execute()
    if not overwrite_existing_config:
      cprint(f"Not overwriting the existing config for {device_to_configure}", color=Color.RED.value, file=sys.stderr)
      exit(0)
  device_status = get_device_status(device_to_configure)
  scenes = list_scene_names(device_to_configure)
  scenes_to_include = inquirer.checkbox(
    message=f"Which scenes for the {device_to_configure} should we include?",
    choices=scenes
  ).execute()
  scene_configurations = [
    build_scene_configuration(device_status, scene)
    for scene in scenes_to_include
  ]
  device_configuration = {
    'name': f"{device_to_configure.lower()}_configuration",
    'remotes': [],
    'scenes': scene_configurations
  }

  with open(device_configuration_destination_file, 'w') as configuration_file:
    yaml.safe_dump(device_configuration, configuration_file)

  cprint(f"finished writing configuration to {device_configuration_destination_file}.", Color.GREEN.value, file=sys.stderr)

def build_scene_configuration(device_status, scene_name):
   return {
     'name': scene_name.replace(' ', '_').lower(),
     'devices': [
       {
         'name': device_status['name'],
         'internal_name': device_status['internal_name'],
         'effect': scene_name,
         'on': True,
         'type': 'nanoleaf_light_panels'
       }
     ]
   }


if __name__ == '__main__':
    main()
