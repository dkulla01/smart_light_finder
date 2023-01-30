import argparse
import os
import sys

import yaml
from InquirerPy import inquirer
from termcolor import cprint

from smart_light_finder.inquirepy_util import YES_OR_NO_CHOICES
from smart_light_finder.termcolor_util import Color

# force pyyaml to always write out configuration objects instead of using
# references when a configuration object appears in multiple places
yaml.SafeDumper.ignore_aliases = lambda *args: True

HOME_CONFIGURATION_FILE_NAME = "total_home_configuration.yaml"

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--path', help="path to individual room configuration files")
  arguments = parser.parse_args()
  configuration_path = arguments.path or os.path.dirname(os.path.abspath(__file__))

  config_file_destination = os.path.join(configuration_path, HOME_CONFIGURATION_FILE_NAME)
  if os.path.exists(config_file_destination):
    overwrite_existing_config = inquirer.select(
      message=f"there is already a home configuration file at {config_file_destination}. Overwrite it?",
      choices=YES_OR_NO_CHOICES
    ).execute()
    if not overwrite_existing_config:
      cprint(f"Not overwriting the existing config file {config_file_destination}", color=Color.RED.value, file=sys.stderr)
      sys.exit(0)

  cprint(f"looking for existing room configurations in {configuration_path}...", color=Color.GREEN.value, file=sys.stderr)
  file_names = [
    file
    for file in os.listdir(configuration_path)
    if os.path.isfile(file) and file.endswith('scene_configuration.yaml')
  ]

  if not file_names:
    cprint(f"No configuration files within {configuration_path}. exiting", color=Color.RED.value, file=sys.stderr)
    sys.exit(1)

  cprint(f"found {len(file_names)} configuration files:", color=Color.GREEN.value, file=sys.stderr)
  cprint("    - " + "\n    - ".join(file_names), color=Color.GREEN.value, file=sys.stderr)

  configurations_by_room_name = {}
  for file_name in file_names:
    with open(file_name, "r") as open_file:
      contents = yaml.safe_load(open_file)
      configurations_by_room_name[contents['name']] = contents

  rooms_to_add = inquirer.checkbox(
    message="which rooms are we adding to the configuration?",
    choices=sorted(configurations_by_room_name.keys())
  ).execute()

  configuration_to_save = {
    'rooms': [
      room_configuration
      for room_name, room_configuration in configurations_by_room_name.items()
      if room_name in rooms_to_add
    ]
  }

  cprint(f"saving configuration with {len(configuration_to_save['rooms'])} rooms to {config_file_destination}", color=Color.GREEN.value, file=sys.stderr)
  with open(config_file_destination, "w") as configuration_file:
    yaml.safe_dump(configuration_to_save, configuration_file)


if __name__ == '__main__':
    main()