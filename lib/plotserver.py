#!/usr/bin/env python3

from lib.mqttclient import MQTTClient
from collections import OrderedDict
from matplotlib import rc
import matplotlib.pyplot as plt
import json, pickle, os, sys

"""
Create malab-like plots from data submitted via MQTT.
"""

DEBUG = False

def dprint(*args, **kw):
    global DEBUG
    if DEBUG:
        print(*args, **kw)


class PlotServer:

    def __init__(self, mqtt, *, session='iot49', dir='.', qos=0):
        # set folder where plots are stored
        os.chdir(os.path.expanduser(dir))
        self.mqtt = mqtt
        self.session = session
        self.series = {}
        self.subscribe("new_series", self.new_series, qos)
        self.subscribe("data", self.data, qos)
        self.subscribe("save_series", self.save_series, qos)
        self.subscribe("plot_series", self.plot_series, qos)

    def subscribe(self, topic, cb, qos):
        topic = '/'.join([self.session, topic])
        self.mqtt.subscribe(topic, cb, qos)

    def new_series(self, client, userdata, msg):
        """MQTT callback: create new series (stored as dict in self.series)"""
        payload = json.loads(msg.payload)
        dprint("new series, {}".format(payload))
        series = OrderedDict()
        for c in payload[1:]:
            series[c] = []
        self.series[payload[0]] = series
        print("new series '{}' with fields {}".format(payload[0], payload[1:]))

    def data(self, client, userdata, msg):
        """MQTT callback: add data to series defined previously with new_series"""
        try:
            payload = json.loads(msg.payload)
            dprint("data, {}".format(payload))
            series = self.series[payload[0]]
            for i, v in enumerate(series.values()):
                v.extend([payload[i+1]])
        except json.decoder.JSONDecodeError:
            print("Received invalid JSON ({}), ignored".format(msg.payload))

    def save_series(self, client, userdata, msg):
        """MQTT callback: store series on remote in pickle format"""
        payload = json.loads(msg.payload)
        dprint("save_series, {}".format(payload))
        series = self.series[payload[0]]
        filename = payload[1]
        if not filename: filename = payload[0] + ".pkl"
        dirname = os.path.dirname(filename)
        if len(dirname) > 0: os.makedirs(dirname, exist_ok=True)
        pickle.dump(series, open(filename, "wb"))
        print("saved series '{}' to file '{}'".format(payload[0], filename))

    def plot_series(self, client, userdata, msg):
        """MQTT callback: do the actual plotting.
        Understands "matlab-like" parameters: title, xlabel, xlog, grid, ...
        """
        payload = json.loads(msg.payload)
        dprint("plot_series, {}".format(payload))
        try:
            series = self.series[payload[0]]
        except KeyError:
            print("*** plot_series: series {} not in {}".format(payload[0], self._series.keys()))
            return
        kwargs = payload[1]
        rc('font', **{'family':'serif','serif':['Palatino']})
        rc('text', usetex=True)
        figsize = kwargs.get("figsize", (5, 3))
        fig = plt.figure(figsize=figsize)
        keys = list(series.keys())
        if len(keys) < 1:
            print("series {} has no data to plot!".format(payload[0]))
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
    default_qos = 0
    default_session = 'iot49'
    parser = argparse.ArgumentParser(
        prog="plotserver",
        usage="%(prog)s [options]",
        description="Server for remote plotting via MQTT on resource constrained platforms.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-s", "--session",
        dest="session",
        help="Session - topic prefix (default: '{}')".format(default_session),
        default=default_session
    )
    parser.add_argument(
        "-d", "--dir",
        dest="dir",
        help="Path where plots are saved (default: '{}')".format(default_dir),
        default=default_dir
    )
    parser.add_argument(
        "-b", "--broker",
        dest="broker",
        help="MQTT broker address (default: '()')".format(default_broker),
        default=default_broker
    )
    parser.add_argument(
        "-p", "--port",
        dest="port",
        type=int,
        help="MQTT broker port (default: '{}')".format(default_port),
        default=default_port
    )
    parser.add_argument(
        "-q", "--qos",
        dest="qos",
        type=int,
        help="MQTT quality of service(default: '{}')".format(default_qos),
        default=default_qos
    )
    args = parser.parse_args(sys.argv[1:])

    print("Starting plotserver with MQTT broker '{}' on port {} with id".format(args.broker, args.port))
    print("saving plots to '{}'".format(args.dir))

    # start the server
    mqtt = MQTTClient(args.broker, port=args.port)
    PlotServer(mqtt, session=args.session, dir=args.dir, qos=args.qos)

    print("Server started ... waiting for data!")
    # blocking; see MQTTClient for non-blocking alternatives
    try:
        mqtt.loop_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
