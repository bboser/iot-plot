# iot-plot
Remote plotting library for resource constrained devices. Uses MQTT for communication. `plotclient` is compatible with MicroPython, enabling small microcontrollers to create high quality plots of measurement data.

### Installation

```
pip install iot-plot
```

This also installs `matplotlib`, if not installed already. `iot-plot` requires Python 3.

To upgrade to a new version, run

```
pip install iot-plot --upgrade
```


### Usage

Start the server on a host (e.g.\ laptop):

```
$ plotserver
```

then create plots using `iot_plot/plotclient.py`. Run

```
$ plotclient
```

(and check the code) to generate

![Sample plot.](example.png)

In a real application you would use the `PlotClient` object on the microcontroller.

### Error from `plotserver` on OSX:

On OSX, if you get an error similar to this:

```
**RuntimeError**: Python is not installed as a framework. 
The Mac OS X backend will not be able to function correctly if 
Python is not installed as a framework. See the Python 
documentation for more information on installing Python 
as a framework on Mac OS X. Please either reinstall Python 
as a framework, or try one of the other backends.
```

Try the following solution (found on `stackoverflow.com`):

**Problem Cause** In mac os image rendering back end of matplotlib (what-is-a-backend to render using the API of Cocoa by default). There is Qt4Agg and GTKAgg and as a back-end is not the default. Set the back end of macosx that is differ compare with other windows or linux os.

I resolve this issue following ways:

* I assume you have installed the pip matplotlib, there is a directory in you root called `~/.matplotlib`.
* Create a file `~/.matplotlib/matplotlibrc` there and add the following code: `backend: TkAgg`
