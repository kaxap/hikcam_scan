import requests
import os

PROXY_SERVICE_HOST = os.environ.get('PROXY_SERVICE_HOST', '192.168.0.10')
PROXY_SERVICE_PORT = os.environ.get('PROXY_SERVICE_PORT', '12001')


def get_proxy() -> dict:
    r = requests.get("http://{}:{}/proxy/random".format(PROXY_SERVICE_HOST, PROXY_SERVICE_PORT))
    try:
        if r.ok:
            proxy = r.json()

            if proxy.get('login'):
                return {
                    "http": "http://{}:{}@{}:{}".format(proxy.get('login'), proxy.get('password'), proxy.get('addr'),
                                                        proxy.get('port')),
                    "https": "https://{}:{}@{}:{}".format(proxy.get('login'), proxy.get('password'), proxy.get('addr'),
                                                          proxy.get('port')),
                }
            else:

                return {
                    "http": "http://{}:{}".format(proxy.get('addr'), proxy.get('port')),
                    "https": "https://{}:{}".format(proxy.get('addr'), proxy.get('port'))
                }

        else:
            raise Exception("Proxy address retrieval error. Is proxy service up and running?")
    finally:
        r.close()


if __name__ == "__main__":
    print(get_proxy())
