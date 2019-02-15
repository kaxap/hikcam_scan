import json

import requests

from proxy_utils import get_proxy
from rmq_queue import RmqChannel, RmqQueueName
from app_logger import get_logger
from statuses import *

logger = get_logger("hik_scan_worker")


def is_generic_http_server(text: str) -> bool:
    text = text.lower()
    if "<html" in text:
        return True
    if "<body" in text:
        return True
    if "<!doctype" in text:
        return True

    return False


def is_hikcam(url: str) -> int:
    try:
        proxy = get_proxy()
        r = requests.get(url, allow_redirects=False, timeout=10, proxies=proxy)
        try:
            if r.ok:
                if 'window.location.href = "doc/page/login.asp?_"+nowDate.getTime();' in r.text:
                    return STATUS_HAS_HIKCAM

                def_status = STATUS_HAS_HTTP

                if 'jsCore/rpcCore.js?version=' in r.text:
                    if 'jsCore/rpcLogin.js?version=' in r.text:
                        if 'jsCore/qrcode.js?version=' in r.text:
                            def_status = STATUS_HAS_UNK_DAHUA


                # dahua gen 2
                r2 = requests.get(url + "current_config/passwd", allow_redirects=False, timeout=10, proxies=proxy)
                try:
                    if r2.ok:
                        if is_generic_http_server(r2.text):
                            return def_status
                        return STATUS_HAS_DAHUA_GEN2
                finally:
                    r2.close()

                # dahua gen 3
                r3 = requests.get(url + "current_config/Account1", allow_redirects=False, timeout=10, proxies=proxy)
                try:
                    if r3.ok:
                        if is_generic_http_server(r3.text):
                            return def_status

                        return STATUS_HAS_DAHUA_GEN3

                    return STATUS_HAS_HTTP
                finally:
                    r3.close()
        finally:
            r.close()

        return r.status_code
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return STATUS_NONE


# create Rabbit channel and queues
channel = RmqChannel()
channel.declare_queue(RmqQueueName.TO_WORKER)
channel.declare_queue(RmqQueueName.FROM_WORKER)


def recv(ch, method, properties, body):
    """
    receiving data from worker_group_discovery
    :param ch: pika parameter [channel]
    :param method:  pika parameter
    :param properties: pika parameter
    :param body: byte encoded json
    :return: nothing
    """

    ip = json.loads(body.decode())['ip']

    status = is_hikcam("http://" + ip + "/")

    if status != STATUS_NONE:
        channel.send(RmqQueueName.FROM_WORKER, {'ip': ip, 'status': status})
        logger.info("sent to saver")

    # acknowledge
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.receive(RmqQueueName.TO_WORKER, recv)
channel.start()


if __name__ == "__main__":
    print(is_hikcam("http://10.10.5.239:80"))




