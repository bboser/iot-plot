#!/usr/bin/env python3

from mqttclient import MQTTClient
from collections import OrderedDict
from matplotlib import rc
import matplotlib.pyplot as plt
import json, pickle, os, sys

"""
Create malab-like plots from data submitted via MQTT.
"""


class PlotServer:

    def __init__(self, mqtt, dir='.', qos=0):
        # set folder where plots are stored
        os.chdir(os.path.expanduser(dir))
        self.series_ = {}
        mqtt.subscribe("new_series", self.new_series_, qos)
        mqtt.subscribe("data", self.data_, qos)
        mqtt.subscribe("save_series", self.save_series_, qos)
        mqtt.subscribe("plot_series", self.plot_series_, qos)
        self.mqtt = mqtt

    # create new series (stored as dict in self.series_)
    def new_series_(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload)
        series = OrderedDict()
        for c in payload[1:]:
            series[c] = []
        self.series_[payload[0]] = series
        print("new series '{}' with fields {}".format(payload[0], payload[1:]))

    # add data to series defined previously with new_series
    def data_(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload)
            series = self.series_[payload[0]]
            for i, v in enumerate(series.values()):
                v.extend([payload[i+1]])
        except json.decoder.JSONDecodeError:
            print("Received invalid JSON ({}), ignored".format(msg.payload))

    # store series on remote in pickle format
    def save_series_(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload)
        series = self.series_[payload[0]]
        filename = payload[1]
        if not filename: filename = payload[0] + ".pkl"
        dirname = os.path.dirname(filename)
        if len(dirname) > 0: os.makedirs(dirname, exist_ok=True)
        pickle.dump(series, open(filename, "wb"))
        print("saved series '{}' to file '{}'".format(payload[0], filename))

    # plot series on remote
    def plot_series_(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload)
        series = self.series_[payload[0]]
        kwargs = payload[1]
        rc('font', **{'family':'serif','serif':['Palatino']})
        rc('text', usetex=True)
        figsize = kwargs.get("figsize", (5, 3))
        fig = plt.figure(figsize=figsize)
        keys = list(series.keys())
        if len(keys) < 1:
            print("series {} has no data to plot!".format(series_name))
            return
        if "hist" in kwargs:
            v = [0] * len(keys)
            l = [0] * len(keys)
            for i, k in enumerate(keys):
                v[i] = series[k]
                l[i] = k
            plt.hist(v, histtype='bar', stacked=False, rwidth=0.7, label=l)
        else:
            x = series[keys[0]]
            if len(keys) < 2:
                plt.plot(x, label=keys[0])
            else:
                keys.pop(0)
                fmt = kwargs.get("format", [])
                for i, y in enumerate(keys):
                    f = fmt[i] if len(fmt) > i else ''
                    plt.plot(x, series[y], f, label=y)
        if "title"  in kwargs: plt.title(kwargs["title"])
        if "xlabel" in kwargs: plt.xlabel(kwargs["xlabel"])
        if "ylabel" in kwargs: plt.ylabel(kwargs["ylabel"])
        plt.xscale("log" if kwargs.get("xlog", False) else "linear")
        plt.yscale("log" if kwargs.get("ylog", False) else "linear")
        plt.grid(kwargs.get("grid", True))
        if len(keys) > 1: plt.legend()
        filename = kwargs.get("filename", payload[0] + ".pdf")
        dirname = os.path.dirname(filename)
        if len(dirname) > 0: os.makedirs(dirname, exist_ok=True)
        plt.savefig(filename, bbox_inches="tight")
        plt.close(fig)
        print("saved plot of series '{}' to file '{}'".format(payload[0], filename))


def main():
    import argparse

    default_dir = "."
    default_broker = "iot.eclipse.org"
    default_port = 1883
    parser = argparse.ArgumentParser(
        prog="plotserver",
        usage="%(prog)s [options]",
        description="Server for remote plotting via MQTT on resource constrained platforms.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--dir",
        dest="dir",
        help="Path where plots are saved (default: '%s')" % default_dir,
        default=default_dir
    )
    parser.add_argument(
        "-b", "--broker",
        dest="broker",
        help="MQTT broker address (default: '%s')" % default_broker,
        default=default_broker
    )
    parser.add_argument(
        "-p", "--port",
        dest="port",
        type=int,
        help="MQTT broker port (default: '%s')" % default_port,
        default=default_port
    )
    args = parser.parse_args(sys.argv[1:])

    print("Starting plotserver with MQTT broker '{}' on port {}".format(args.broker, args.port))
    print("saving plots to '{}'".format(args.dir))

    # start the server
    mqtt = MQTTClient(args.broker, port=args.port)
    server = PlotServer(mqtt, dir=args.dir)

    print("Server started ... waiting for data!")
    # blocking; see MQTTClient for non-blocking alternatives
    try:
        mqtt.loop_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
