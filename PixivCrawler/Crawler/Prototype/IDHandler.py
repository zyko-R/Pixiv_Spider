from PixivCrawler.Crawler.Prototype.Lib.MethodLauncher import *
from PixivCrawler.Crawler.Prototype.Lib.Method import *


class ICrawler(ABC):
    @abstractmethod
    def crawl(self, file_name: str, id_list: list): pass


class IDHandler(ICrawler):
    class HandleS:
        def __new__(cls, *p_m: PendingMethod): return [ExecuteMethod(EnableMethod(d)) for d in p_m]

    def crawl(self, file_name: str, id_list: list):
        ids = {'IMG': {'NOR': [], 'R18': []}, 'GIF': {'NOR': [], 'R18': []}}
        result = self.HandleS(*[FFilterType(ids)for ids in self.HandleS(FFilterForm(id_list))[0]])
        ids['IMG']['NOR'], ids['IMG']['R18'] = result[0] if len(result[0]) > 0 else (None, None)
        ids['GIF']['NOR'], ids['GIF']['R18'] = result[1] if len(result[1]) > 0 else (None, None)

        nor_img, r18_img = self.HandleS(FParseIMG(ids['IMG']['NOR']), FParseIMG(ids['IMG']['R18']))
        self.HandleS(FStoreIMG(f'[NOR]{file_name}', *nor_img), FStoreIMG(f'[R18]{file_name}', *r18_img))

        nor_gif, r18_gif = self.HandleS(FParseGIF(ids['GIF']['NOR']), FParseGIF(ids['GIF']['R18']))
        self.HandleS(FStoreGIF(f'[NOR]{file_name}', *nor_gif), FStoreGIF(f'[R18]{file_name}', *r18_gif))
