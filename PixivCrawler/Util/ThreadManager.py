import asyncio
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import nest_asyncio
nest_asyncio.apply()


class ThreadLauncher:
    def __new__(cls, compositor):
        return compositor.launch()


class ThreadCompositor(ABC):
    @abstractmethod
    def launch(self):
        pass

    @staticmethod
    def unpacking(params_list):
        task_params = [[] for i in range(len(params_list[0]))]
        for param_list in params_list:
            for i, param in enumerate(param_list):
                task_params[i].append(param)
        return task_params


class Thread(ThreadCompositor):
    def __init__(self, method, params_list):
        self.method, self.params_list = method, params_list

    def launch(self):
        task_params = self.unpacking(self.params_list)
        with ThreadPoolExecutor(max_workers=8) as pool:
            task_list = [pool.submit(self.method, *params) for params in task_params]
            result = [task.result() for task in as_completed(task_list)]
        return result


class Async(ThreadCompositor):
    def __init__(self, method, params_list, call_back=None):
        self.method, self.params_list = method, params_list
        self.call_back = call_back

    def launch(self):
        task_params = self.unpacking(self.params_list)
        loop = asyncio.get_event_loop()
        task_list = [loop.create_task(self.method(*params)) for params in task_params]
        if self.call_back is not None:
            for task in task_list:
                task.add_done_callback(self.call_back)
        try:
            loop.run_until_complete(asyncio.wait(task_list))
        except ValueError:
            pass


class Wait(ThreadCompositor):
    def __init__(self, task_list):
        self.task_list = task_list

    def launch(self):
        for task in self.task_list:
            if isinstance(task, threading.Thread):
                task.start()
        result = []
        for task in self.task_list:
            if isinstance(task, threading.Thread):
                task.join()
                result.append(task.result if hasattr(task, 'result')else None)
        return result



