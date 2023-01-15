from Downloader import Login
from Spider.SpecialType import *
import asyncio
import nest_asyncio
nest_asyncio.apply()


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
    FuncBuilder('To download similar artworks from artwork', ByArtworkIDCrawler)
    FuncBuilder('To download artworks from one author', ByAuthorIDCrawler)
    FuncBuilder('To download artworks from author(s) you subscribe', BySubCrawler)
    FuncBuilder('To download ranking artworks', ByRankingCrawler)
    FuncBuilder('To trace author(s)', Util.subscribe)
    FuncBuilder('To update the artworks of author(s) you trace', ByTraceCrawler)


def menu():
    while True:
        for num, func in enumerate(Func_list):
            print(f'{num+1}: {func}')
            match str(input(f'>>Yes-1 | >>Next-2 | >Exit-3 >? ')):
                case '1': func.func()
                case '2': continue
                case '3': exit("Exit")
            output(f'[DONE]', form=4, code=32)
            break


if __name__ == '__main__':
    init()
    menu()







