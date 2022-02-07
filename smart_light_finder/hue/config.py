from os import environ

def get_hue_host():
  return environ.get('HUE_HOST', default='192.168.86.62')

def get_hue_api_key():
  return environ.get('HUE_USER', default='')