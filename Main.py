import asyncio

import Process


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


def asy_launch(asy_method, params_list, call_back=None):
    p_list = [[] for i in range(len(params_list[0]))]
    for param_list in params_list:
        for i in range(len(param_list)):
            p_list[i].append(param_list[i])

    task_list = []
    loop = asyncio.get_event_loop()
    for params in p_list:
        task = loop.create_task(asy_method(tuple(params)))
        if call_back is not None:
            task.add_done_callback(call_back)
        task_list.append(task)
    try:
        loop.run_until_complete(asyncio.wait(task_list))
    except ValueError:
        pass


if __name__ == '__main__':
    runner = Process.Run()
    runner.start()
    runner.run()
    runner.end()
