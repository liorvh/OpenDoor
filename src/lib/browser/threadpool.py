# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Development Team: Stanislav WEB
"""
import threading
import time
from Queue import Queue

from src.lib.tpl import Tpl as tpl
from .exceptions import ThreadPoolError
from .exceptions import WorkerError
from .worker import Worker


class ThreadPool():
    """ThreadPool class"""

    def __init__(self, num_threads, total_items, delay):
        """
        Initialize thread pool
        :param int num_threads: active workers
        :param int total_items: total items
        :param int delay: delay betwen threads
        :raise ThreadPoolError
        :return None
        """

        self.__queue = Queue(num_threads)
        self.__workers = []
        self.total_items_size = total_items
        self.is_started = True

        try:

            for _ in range(num_threads):

                try:

                    worker = Worker(self.__queue, num_threads, delay)

                    if False is worker.isAlive():
                        worker.setDaemon(True)
                        worker.start()
                        self.__workers.append(worker)

                except Exception as e:
                    raise WorkerError(e)
        except WorkerError as e:
            raise ThreadPoolError(e)

    @property
    def workers_size(self):
        """
        Get pool workers (threads)
        :return: int
        """

        return self.__workers.__len__()

    @property
    def items_size(self):
        """
        Get pool items size
        :return: int
        """

        counter = 0
        for worker in self.__workers:
            counter += worker.counter
        return counter

    def add(self, func, *args, **kargs):
        """
        Add a task to the queue
        :param func func: callback function
        :param dict args: arguments
        :param kargs: key arguments
        :return: None
        """

        try:
            if True is self.is_started:
                if self.items_size < self.total_items_size:
                    self.__queue.put((func, args, kargs))
                else:
                    self.__queue.join()
        except (SystemExit, KeyboardInterrupt):
            time.sleep(2)
            self.pause()

    def pause(self):
        """
        ThreadPool pause
        :raise KeyboardInterrupt
        :return: None
        """

        self.is_started = False
        tpl.info(key='stop_threads', threads=len(self.__workers))

        try:
            while 0 < threading.active_count():
                if False is self.is_started and False:
                    for worker in threading._enumerate():
                        if threading.current_thread().__class__.__name__ != '_MainThread':
                            worker.pause()
                    time.sleep(2)

                char = tpl.prompt(key='option_prompt')
                if char.lower() == 'e':
                    raise KeyboardInterrupt
                elif char.lower() == 'c':
                    self.resume()
                    break
                else:
                    continue

        except (SystemExit, KeyboardInterrupt):
            raise KeyboardInterrupt

    def resume(self):
        """
        Resume threadpool
        :return: None
        """

        if False is self.is_started:
            tpl.info(key='resume_threads')
            for worker in self.__workers:
                worker.resume()
            self.is_started = True
        pass
