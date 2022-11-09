import toml

from smart_light_finder.hue.config import get_hue_host, get_hue_api_key
from smart_light_finder.hue.topology import get_rooms


def main():
  host = get_hue_host()
  api_key = get_hue_api_key()

  rooms = get_rooms(host, api_key)
  lights_by_id = {light['id']: light for light in get_lights(host, api_key)}

  rooms_and_their_lights = {}

  for room in rooms:
    # print(f"room: {room['name']}")
    # print("  lights:")
    rooms_and_their_lights[room['name']] = [lights_by_id[light_id] for light_id in room['lights']]
    # for light_id in room['lights']:
    #   light = lights_by_id[light_id]

      # print(f"    name: {light['name']}, id: {light['id']}")

    print(toml.dumps(rooms_and_their_lights))

if __name__ == '__main__':
    main()
