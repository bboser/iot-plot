# iot-plot
Remote plotting library for resource constrained devices. Uses MQTT for communication. `plotclient` is compatible with MicroPython, enabling small microcontrollers to create high quality plots of measurement data.

Start the server on a host (e.g.\ laptop):

```
$ plotserver
```

then create plots using `iot_plot/plotclient.py`. Run

```
$ plotclient
```

(and check the code) to generate

![Sample plot.](example.pdf)

In a real application you would use the PlotClient object on the microcontroller.