import json
import threading

import time

from database import init_database, save_ip
from rmq_queue import RmqChannel, RmqQueueName
from statuses import *

# time to initialize for other services
# time.sleep(30)

chan = RmqChannel()
chan.declare_queue(RmqQueueName.FROM_WORKER)

total = 0
hiks = 0
http = 0


def recv(ch, method, properties, body):
    """
    receiving data from worker_grab_users
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """

    global total
    global http, hiks

    result = json.loads(body.decode())

    save_ip(result['ip'], result['status'])

    if result['status'] == STATUS_HAS_HTTP:
        http += 1
    else:
        hiks += 1


    # acknowledge
    total += 1

    if total % 5 == 0:
        print("total saved: %d, http: %d, hikcams: %d" % (total, http, hiks))

    ch.basic_ack(delivery_tag=method.delivery_tag)


def recv_ips() -> None:
    """
    starts receiving users from the queue
    """

    chan.receive(RmqQueueName.FROM_WORKER, recv)

    # start consumer
    threading.Thread(target=chan.start).start()


init_database()
recv_ips()

