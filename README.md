# Bokeh Light Curve Inspector

A simple pure-python browser app using bokeh (bokeh.pydata.org) to visualize, inspect and label astronomical time series. 

## How to run

	bokeh serve path_to_this_folder --args path_to_light_curves path_to_pickled_periods path_to_results

Other options that might be useful

	--allow-websocket-origin=myserveraddress.com:5006


## Requirements

1. Numpy (numpy.org)
2. Bokeh (bokeh.pydata.org)

Note: Tested with Python 3.6 and Bokeh 0.12.8

## TODO

* Add test data
* Improve server security to make this safe for production
* Add user authentication

## License

MIT


