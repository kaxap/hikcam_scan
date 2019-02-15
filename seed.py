import random
import threading

import time

from rmq_queue import RmqChannel, RmqQueueName
from supervisor import spawn_and_supervise

# time to initialize for other services
# time.sleep(30)

chan = RmqChannel()
chan.declare_queue(RmqQueueName.TO_WORKER)


def ips(ip_range: str):
    s = ip_range.strip().split("-")
    start, end = s[0], s[1]
    import socket, struct
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0]
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]


def send_user_ids(filename: str) -> None:
    """
    sends user ids(to be multiplied by thousands) to the TO_WORKER queue
    :return:
    """

    result = []
    with open(filename, 'r', encoding='utf-8') as f:
        l = f.readlines()
        random.shuffle(l)
        for i in l:
            print("generating ips for range", i)
            result.extend(ips(i))

    print("sending...")
    for ip in result:
        chan.send(RmqQueueName.TO_WORKER, {"ip": ip})


def start_workers() -> None:
    """
    spawn worker processes
    """
    # start workers
    threading.Thread(target=spawn_and_supervise, args=("hik_scan.py",)).start()
    pass


if chan.queue_length(RmqQueueName.TO_WORKER) == 0:
    send_user_ids("ip_ranges.kz.txt")

print("spawning processes...")
start_workers()

# wait for queue to be emptied
while chan.queue_length(RmqQueueName.TO_WORKER) > 0:
    time.sleep(60)
