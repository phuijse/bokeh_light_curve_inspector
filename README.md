# Bokeh Light Curve Inspector

A simple pure-python web browser application using Bokeh (bokeh.pydata.org) to visualize, inspect and label periodic astronomical time series. Possible use-cases are novelty detection, collaborative research and crowd-sourcing. *Disclaimer:* This code was written for educative purposes and it is not safe for production (see TODO below).

## How to run

    cd this_folder
    bokeh serve . --args example/light_curves example/periods.pkl example/results/

Then point your favorite web browser to

    http://localhost:5006

### Note about the arguments

The Bokeh server allows to pass arguments to the main code using the --args flag. Three arguments are expected:
1. Path to the folder containing the light curve files
2. Path to a pickle file containing file names and light curve periods
3. Path to a folder to dump results from labeling process

Reading and parsing of the light curve files is done in light\_curve\_handler.py

### What you should see when running the example

![Log-in interface](/example/capture1.png?raw=true "Log-in interface")

![Inspector interface](/example/capture2.png?raw=true "Inspector interface")

### How does it work

* Choose a username and hit enter at the log-in interface
* You should be seeing the inspector interface. Here you can:
    * Move from page to page, each showing a set of 9 light curves
    * Label the currently selected light curve into one of the available categories
    * Each time you move to the next/previous page your labeling results are saved at _resultfolder/username/_

### Remote access to the bokeh server

If you intend to access the bokeh server from another machine in your LAN you will have to add

	--allow-websocket-origin=myserverlanip:5006

before _--args_ in the execution line above

If you intend to access from outside your LAN just change myserverlanip by the desired domain. Bokeh serve also accepts a _--port_ option if you need to use a different port

## Requirements

1. Numpy (numpy.org)
2. Bokeh (bokeh.pydata.org)

Note: Tested with Python 3.6 and Bokeh 0.12.6

## TODO

* ~~Add test data~~
* Improve server security to make this safe for production
* Add user authentication, sessions, etc

## License

MIT


