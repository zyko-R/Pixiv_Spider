from PixivCrawler.Crawler.Prototype.Lib.APIHandler import *
from PixivCrawler.Crawler.Prototype.Lib.HandlerAPI import *


class ICrawler(ABC):
    @abstractmethod
    def crawl(self, file_name: str, id_list: list): pass


class IDHandler(ICrawler):
    def crawl(self, file_name: str, id_list: list):
        ids = {'IMG': {'NOR': [], 'R18': []}, 'GIF': {'NOR': [], 'R18': []}}
        result = APISHandler(*(FilterType(ids) for ids in [*APISHandler(FilterForm(id_list))[0]]))
        ids['IMG']['NOR'], ids['IMG']['R18'] = result[0] if len(result[0]) > 0 else (None, None)
        ids['GIF']['NOR'], ids['GIF']['R18'] = result[1] if len(result[1]) > 0 else (None, None)

        nor_img, r18_img = APISHandler(ParseIMG(ids['IMG']['NOR']), ParseIMG(ids['IMG']['R18']))
        store_nor = StoreIMG(f'[NOR]{file_name}', *nor_img) if len(nor_img) > 0 else None
        store_r18 = StoreIMG(f'[R18]{file_name}', *r18_img) if len(r18_img) > 0 else None
        APISHandler(store_nor, store_r18)

        nor_gif, r18_gif = APISHandler(ParseGIF(ids['GIF']['NOR']), ParseGIF(ids['GIF']['R18']))
        store_nor = StoreGIF(f'[NOR]{file_name}', *nor_gif) if len(nor_gif) > 0 else None
        store_r18 = StoreGIF(f'[R18]{file_name}', *r18_gif) if len(r18_gif) > 0 else None
        APISHandler(store_nor, store_r18)
