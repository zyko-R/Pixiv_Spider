import asyncio
import nest_asyncio

from ExceptID.Secondary import subscribe
from Spider.SpecialType import *
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


Func_list = []


class FuncBuilder:
    def __init__(self, display, func):
        self.display = display
        self.func = func
        Func_list.append(self)

    def __str__(self):
        return self.display


def init():
    Login()
    FuncBuilder('To trace author(s)', subscribe)
    FuncBuilder('To update the artworks of author(s) you trace', ByTraceCrawler)
    FuncBuilder('To download similar artworks from artwork', ByArtworkIDCrawler)
    FuncBuilder('To download artworks from one author', ByAuthorIDCrawler)
    FuncBuilder('To download artworks from author(s) you subscribe', BySubCrawler)
    FuncBuilder('To download ranking artworks', ByRankingCrawler)


def menu():
    while True:
        for num, func in enumerate(Func_list):
            print(f'{num+1}: {func}')
            match str(input(f'>>Yes-1 | >>Next-2 | >Exit-3 >? ')):
                case '1': func.func()
                case '2': continue
                case '3': exit("Exit")
            print('DONE')
            break


if __name__ == '__main__':
    init()
    menu()




