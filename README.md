## smart_light_finder

This is a little script to find the hue lights in a given room,
identify their colors, and spit out some configuration JSON
to let us load into [caseta_listener](https://github.com/dkulla01/caseta_listener).

You'll need python 3.9 and [poetry](https://python-poetry.org/docs/#installation). Install the projects deps with

```commandline
poetry install
```

You'll need to [generate a hue api key](https://developers.meethue.com/develop/hue-api-v2/getting-started/)
and find the address of your hue bridge (set a dhcp reservation).

set some environment variables:
```commandline
export HUE_HOST=<address of your hue bridge>
export HUE_USER=<a hue api key>
```

Then set up a lovely ambiance in one of your hue rooms with the hue app.
Make it extra cozy; _you're worth it!_

Then, with those lights on and dialed in to the colors you want, run the script
to convert your pretty colors to a configuration we'll be able to call up from `caseta_listener`:
```commandline
python smart_light_finder.py
```

and follow the prompts.

`caseta_listener` knows how to listen to caseta pico remotes, but it's still learning how to
cue up different lighting scenes. baby steps...

#### things I'd like to add:
- it would be cool if the script could tell you what the colors are in plain english. the xy color space that hue uses
  isn't the most intuitive, so knowing that `"xy": {"x": 0.2988, "y": 0.1419}` is `pink` would make the configuration
  script a little more descriptive. See [this gist](https://gist.github.com/popcorn245/30afa0f98eea1c2fd34d) for some context
- I want to figure out how to build an executable from this. Not a huge deal rn, but this seems simple enough.