"""
RabbitMQ wrapper

Example:

    channel = RmqChannel()
    channel.declare_queue(RmqQueueName.FROM_WORKER)
    channel.receive(RmqQueueName.GROUP, recv)
    channel.start()

recv function:

    def recv(ch, method, properties, body):
        "(your data in the body)"
        data = json.loads(body.decode());

send:
    channel.send(RmqQueueName.FROM_WORKER, {"some_data": "value"})

"""

from enum import Enum
import pika
import os
import json

DEBUG = False


class RmqQueueName(Enum):
    TO_WORKER = 'KZ_HIKCAM_SCAN_TO_WORKER'
    FROM_WORKER = 'KZ_HIKCAM_SCAN_FROM_WORKER'


class RmqChannel:
    def __init__(self, prefetch_count=1):
        """ create rabbitmq connection """

        if not DEBUG:
            user = os.environ.get('RABBITMQ_DEFAULT_USER', 'rabbit')
            password = os.environ.get('RABBITMQ_DEFAULT_PASS', 'carrotinuranus')
            host = os.environ.get('RABBITMQ_HOST', '192.168.0.10')
            port = os.environ.get('RABBITMQ_PORT', '5772')
            heartbeat = os.environ.get('RABBITMQ_HEARTBEAT', '0')

            print("connecting to {}:{}".format(host, port))

            params = pika.ConnectionParameters(
                host=host,
                port=int(port),
                credentials=pika.credentials.PlainCredentials(user,
                                                              password),
                heartbeat_interval=int(heartbeat),
            )

            self.connection = pika.BlockingConnection(parameters=params)
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=prefetch_count)
        else:
            user = 'rabbit'
            password = 'carrotinuranus'
            host = '192.168.0.10'
            port = '5772'
            heartbeat = '0'

            print("connecting to {}:{}".format(host, port))

            params = pika.ConnectionParameters(
                host=host,
                port=int(port),
                credentials=pika.credentials.PlainCredentials(user,
                                                              password),
                heartbeat_interval=int(heartbeat),
            )

            self.connection = pika.BlockingConnection(parameters=params)
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=prefetch_count)

        print("connected")

    def declare_queue(self, name: RmqQueueName, durable=True):
        """ declare queue before using """
        self.channel.queue_declare(name.value, durable=durable)

    def delete_queue(self, name: RmqQueueName):
        self.channel.queue_delete(name.value)

    def redeclare_queue(self, name: RmqQueueName, durable=True):
        self.delete_queue(name)
        self.declare_queue(name, durable)

    def queue_length(self, name: RmqQueueName):
        q = self.channel.queue_declare(queue=name.value, durable=False, passive=True, exclusive=False,
                                       auto_delete=False)
        return q.method.message_count

    def send(self, queue_name: RmqQueueName, data: dict):
        """ send object to the queue """
        self.channel.basic_publish(exchange='', routing_key=queue_name.value,
                                   body=json.dumps(data, ensure_ascii=False),
                                   properties=pika.BasicProperties(
                                       delivery_mode=2, ))

    def receive(self, queue_name: RmqQueueName, callback, no_ack=False):
        """callback = func(ch, method, properties, body) """
        self.channel.basic_consume(callback,
                                   queue=queue_name.value,
                                   no_ack=no_ack)

    def start(self):
        self.channel.start_consuming()

    def close(self):
        return self.channel.close()
