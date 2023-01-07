import asyncio
import nest_asyncio
from Spider.Factory import *
nest_asyncio.apply()


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
    Login()
    Menu = """
    If you want to subscribe a author(ID): type 1
    If you want to download all artwork from one author: type 2
    If you want to update your subscribe_list: type 3
    """
    match str(input(Menu)):
        case '1': ExceptAuthorSub.subscribe(str(input('Enter author(ID)')))
        case '2': FocusedAuthorCrawler(str(input('Author(ID/Name)>? ')), int(input("How many sources do you want>? ")))
        case '3': IncrementalAuthorCrawler(int(input("How many sources do you want to update>? ")))


