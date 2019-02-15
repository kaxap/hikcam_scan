"""
runs and supervises vk workers

Example:
    spawn_and_supervise("worker.py")
"""

from subprocess import Popen
import time
import app_logger
from typing import List

logger = app_logger.get_logger("supervisor")

def spawn_single_worker(worker_name: str) -> Popen:
    """ spawns process for account """
    return Popen(['python', worker_name])


def spawn_workers(worker_name: str, n_workers: int) -> List[dict]:
    """
    spawns multiple processes
    :param worker_name: py filename, e.g. worker.py
    :param accounts: accounts to spawn
    :return: list of {account:, process:} dictionary
    """
    logger.info("running processes...")
    processes = []
    for i in range(n_workers):
        processes.append({'process': spawn_single_worker(worker_name)})

        """ pause for 2 secs, so vk won't et flooded with auth requests """
        time.sleep(0.2)

    return processes


def kill_processes(processes: List[dict]):
    """
    kill all processes from processes list
    :param processes: list of processes spawned by spawn_workers
    :return:
    """
    for process in processes:
        try:
            process['process'].kill()
        except:
            # sometimes kill() throws an exception
            pass


def spawn_and_supervise(worker_name: str) -> None:
    """ spawns and supervises processes """
    processes = spawn_workers(worker_name, 1000)

    while True:
        try:
            for process in processes:
                return_code = process['process'].poll()
                if return_code is not None:

                    logger.warning("Worker  has died, restarting...")

                    """pause for 2 seconds, to prevent instant relogging"""
                    time.sleep(2)
                    process['process'] = spawn_single_worker(worker_name)

            time.sleep(5)

        except KeyboardInterrupt:
            kill_processes(processes)
            quit()


logger.info("initializing...")

