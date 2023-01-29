from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm as td


class API:
    def __init__(self, *param): self.param = param

    @abstractmethod
    def fn_ea(self, *args): pass

    def closer(self, *args): return args


class APISHandler:
    @staticmethod
    def api_launch(api: API):
        def repack(x): return [[e[i] for e in x] for i in range(len(x[0]))]
        desc = f'\033[1;34m{type(api).__name__}\033[0m'
        with ThreadPoolExecutor(max_workers=8) as pool:
            res = [r for r in td(pool.map(api.fn_ea, *api.param), desc=desc, total=len(repack(api.param)), position=0, delay=0.01)]
        return api.closer(*repack(res)) if len(res) > 0 and res[0] is not None else res

    def __new__(cls, *apis: API):
        apis = [api for api in filter(lambda x: isinstance(x, API), apis)]
        with ThreadPoolExecutor(max_workers=len(apis)) as pool:
            res = [res for res in pool.map(cls.api_launch, apis)]
        return res
