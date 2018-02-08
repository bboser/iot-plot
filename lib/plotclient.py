#!/usr/bin/env python3

from json import dumps

class PlotClient:

    def __init__(self, mqtt_client, session='iot49'):
        self.mqtt_client = mqtt_client
        self.session = session

    def new_series(self, *args):
        """create a new series on remote
        all data of a prior series with the same name will be lost
        arguments:
            series name (first)
            column names
        """
        self.__publish("new_series", args)

        """add data to series on remote, use after 'new_series'
        arguments:
            series name
            column values (same number as column names submitted with new_series)
        """
        self.__publish("data", args)

    def save_series(self, series, filename=None):
        """store series on remote in pickle format"""
        self.__publish("save_series", [ series, filename ])

    def plot_series(self, series, **kwargs):
        """plot series on remote"""
        self.__publish("plot_series", [ series, kwargs ])

    def __publish(self, topic, data):
        """send data to broker, do not call from other modules"""
        topic = '/'.join([self.session, topic])
        self.mqtt_client.publish(topic, dumps(data))


def main():
    """Sample code for producing a plot.

    Typically you'll run this on a small device without access to matplotlib.
    E.g. a microcontroller with MicroPython firmware.

    Start the 'plotserver' on the host computer before running executing this code.
    """
    from lib.mqttclient import MQTTClient
    from math import sin, cos, exp, pi

    mqtt = MQTTClient("iot.eclipse.org")
    mp = PlotClient(mqtt)

    # give the series a unique name (in case you create multiple plots)
    SERIES = "sinusoid"

    # data column names
    mp.new_series(SERIES, 'time', 'cos', 'sin', 'sin*cos')

    # generate the data
    def f1(t): return cos(2 * pi * t) * exp(-t)
    def f2(t): return sin(2 * pi * t) * exp(-t)
    def f3(t): return sin(2 * pi * t) * cos(2 * pi * t) * exp(-t)
    for t in range(200):
        t *= 0.025
        # submit each datapoint to the plot server
        mp.data(SERIES, t, f1(t), f2(t), f3(t))

    # save data as pkl document
    # see plot_load_pkl.py for an example of loading it back into python
    mp.save_series(SERIES)

    # create a plot, default dir is $IoT49
    mp.plot_series(SERIES,
        filename="example.pdf",
        xlabel="Time [s]",
        ylabel="Voltage [mV]",
        title=r"Damped exponential decay $e^{-t} \cos(2\pi t)$")

    # wait until all data is transferred or no plot will be generated ...
    import time
    time.sleep(5)


if __name__ == "__main__":
    main()
