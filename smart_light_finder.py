import json
from os import environ
from json import dumps
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
  host = environ.get('HUE_HOST', default='192.168.86.62');
  api_key = environ.get('HUE_USER', default='')

  rooms_response = requests.get(f"https://{host}/clip/v2/resource/room", headers={'hue-application-key': api_key}, verify=False)
  rooms = [{'name': entry['metadata']['name'], 'id': entry['id']} for entry in rooms_response.json()['data']]
  print(f"got rooms {json.dumps(rooms)}")

  lights_response = requests.get(f"https://{host}/clip/v2/resource/light", headers={'hue-application-key': api_key}, verify=False)
  body = lights_response.json()
  print(f"got a status of {lights_response.status_code}")
  print(f"this is our json: {json.dumps([ build_light_object(entry) for entry in body['data']])}")

def build_light_object(light_response_entry):
    return {
        'id': light_response_entry['id'],
        'on': light_response_entry['on'],
        'color_capable': 'color' in light_response_entry.keys(),
        'name': light_response_entry['metadata']['name']
    }

if __name__ == '__main__':
    main()