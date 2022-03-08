from os import environ

from nanoleafapi import Nanoleaf


def get_all_nanoleaf_device_names():
  return environ.get('NANOLEAF_DEVICES').split(':')

def get_nanoleaf_device_names(room_name):
  all_devices = get_all_nanoleaf_device_names()
  formatted_room_name = room_name.upper().replace(' ', '_')
  return sorted([device for device in all_devices if device.startswith(formatted_room_name)])

def get_nanoleaf_host(device_name):
  return environ.get(f"NANOLEAF_{device_name}_HOST")

def get_nanoleaf_token(device_name):
  return environ.get(f"NANOLEAF_{device_name}_TOKEN")

def get_device_status(device_name):
  host = get_nanoleaf_host(device_name)
  token = get_nanoleaf_token(device_name)
  if not host or not token:
    raise AssertionError(f"Incomplete configuration for the {device_name} nanoleaf device")
  device = Nanoleaf(host, token)
  device_info = device.get_info()
  status = {
    'name': device_name,
    'internal_name': device_info['name'],
    'on': device_info['state']['on']['value'],
    'type': 'nanoleaf_light_panels',
    'color': {'effect': device_info['effects']['select']}
  }
  return status

def list_scene_names(device_name):
  host = get_nanoleaf_host(device_name)
  token = get_nanoleaf_token(device_name)
  device = Nanoleaf(host, token)
  return device.list_effects()
