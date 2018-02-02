import paho.mqtt.client as paho

class MQTTClient:

    def __init__(self, broker, port=1883):
        mqtt = paho.Client()
        mqtt.connect(broker, 1883)
        mqtt.reconnect_delay_set(min_delay=1, max_delay=120)
        self.mqtt = mqtt

    # subscribe to topic(s), supports wildcards (+, #)
    # optionally register callback (or rely on default)
    # callback signature: cb(client, userdata, message)
    #    message has fields topic and payload
    def subscribe(self, topic, callback=None, qos=0):
        self.mqtt.subscribe(topic, qos)
        if callback: self.mqtt.message_callback_add(topic, callback)

    # default callback for topics subscribed to for which no dedicated
    # callback handler has been defined
    def default_subscribe_callback(self, callback):
        self.mqtt.on_message = callback

    def unsubscribe(self, topic):
        self.mqtt.unsubscribe(topic)

    # non-blocking check for incoming messages, call periodically
    # (or use another "loop" solution)
    def loop(self):
        self.mqtt.loop()

    # non-blocking thread to check for incoming messages
    def loop_start(self):
        self.mqtt.loop_start()

    # blocking loop checking for incoming messages
    def loop_forever(self):
        self.mqtt.loop_forever()

    def publish(self, topic, payload=None, qos=0, retain=False):
        return self.mqtt.publish(topic, payload, qos, retain)

    def disconnect(self):
        self.mqtt.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
