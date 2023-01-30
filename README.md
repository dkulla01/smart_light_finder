## smart_light_finder

This is a little project to find the hue lights, nanoleaf devices, and wemo-outlet-controlled lights in a given room,
identify their colors, and spit out some configuration yaml that we can load into
[caseta_listener](https://github.com/dkulla01/caseta_listener).

### Setup
You'll need python 3.9+ and [poetry](https://python-poetry.org/docs/#installation). Install the projects deps with

```commandline
poetry install
```

You'll need to [generate a hue api key](https://developers.meethue.com/develop/hue-api-v2/getting-started/)
and find the address of your hue bridge (set a dhcp reservation).

Set some environment variables:
```bash
export HUE_HOST=192.168.XXX.XXX
export HUE_USER=your-api-key
```

You'll need some more environment variables if you want to have the script find nanoleaf devices.
[Follow these instructions](https://documenter.getpostman.com/view/1559645/RW1gEcCH#0fe71046-6a4b-46b7-ab05-9ea648b06c89)
for each nanoleaf device to generate auth tokens.
```bash
# colon delimited nanoleaf device names. Note the ROOMNAME prefix for each device
export NANOLEAF_DEVICES=LIVING_ROOM_SHAPES:ROOMNAME_DEVICE
# For each device, you'll need to set an env var for the host
# You made DHCP reservations for these devices too, right?
export NANOLEAF_LIVING_ROOM_SHAPES_HOST=192.168.XXX.XXX
# you'll also need to store the token in an env var
export NANOLEAF_LIVING_ROOM_SHAPES_TOKEN=...
```

_Whoa there, that's a lot of env vars!_ Indeed it is. I use an 
[ohmyzsh dotenv plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/dotenv) and a `.env` file to manage and
automatically load these env vars, but do whatever works for you. 

### Building room configurations
Now we're ready to import your cozy hue scenes and build configuration files with them. We'll find
all the scenes you've made in the hue app, so create any new scenes you
want to import.

If you want to include wemo outlets in your scenes, you need to build a
wemo room configuration that maps wemo outlets to the rooms configured in your
philips hue config. Do that with:

```commandline
poetry run build_wemo_room_configuration --path path/to/configuration_dir
```


Next, to build the scene configurations for a given room, run:
```commandline
poetry run build_room_configuration --path path/to/configuration_dir
```

and follow the prompts. Repeat for each room you want to configure.

Note that you can choose to have Wemo devices and nanoleaf devices included in the scenes
that the script configures. If you include them, the hue scenes will drive those additional devices.
But much of the time, you'll want to control the nanoleaf devices separately. There's a script
for that too:

```commandline
poetry run build_nanoleaf_configuration --path path/to/configuration_dir
```

Finally, stitch together all of your scene configuration files with:

```commandline
poetry run build_home_configuration --path path/to/configuration_dir
```

The file that this script creates is almost ready for `caseta_listener`. All it needs are the
remote IDs of the Caseta Pico remotes that you want to be responsible for each room. You'll
have to add those to the configuration file manually.