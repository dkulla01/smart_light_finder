## smart_light_finder

This is a little project to find the hue lights, nanoleaf devices, and wemo-outlet-controlled lights in a given room,
identify their colors, and spit out some configuration yaml that we can load into
[caseta_listener](https://github.com/dkulla01/caseta_listener).

### Setup
You'll need python 3.9 and [poetry](https://python-poetry.org/docs/#installation). Install the projects deps with

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

### Building scene configurations
Now we're ready to up a lovely ambiance in one of your hue rooms with the hue app, nanoleaf app, and/or wemo app.
Make it extra cozy; _you're worth it!_

Then, with those lights on and dialed in to the colors you want, run the script
to convert your pretty colors to a configuration we'll be able to call up from `caseta_listener`:
```commandline
poetry run build_scene_configuration
```

and follow the prompts.

`caseta_listener` knows how to listen to caseta pico remotes, but it's still learning how to
cue up different lighting scenes. baby steps...

#### things I'd like to add:
- it would be cool if the script could tell you what the colors are in plain english. the xy color space that hue uses
  isn't the most intuitive, so knowing that `"xy": {"x": 0.2988, "y": 0.1419}` is `pink` would make the configuration
  script a little more descriptive. See [this gist](https://gist.github.com/popcorn245/30afa0f98eea1c2fd34d) for some context
- I want to figure out how to build an executable from this. Not a huge deal rn, but this seems simple enough.
  [This tutorial](https://www.brainsorting.com/posts/publish-a-package-on-pypi-using-poetry/) shows how to publish a package on pypi.