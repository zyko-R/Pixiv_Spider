from concurrent.futures import ThreadPoolExecutor
from itertools import chain

from tqdm import tqdm

from PixivCrawler.Crawler.Prototype.Lib.Method import *


class EnableMethod:
    def __new__(cls, self: PendingMethod) -> PendingMethod.Method:
        if not isinstance(self, PendingMethod):
            return PendingMethod.VoidMethod()

        def is_param_safe(*ps):
            def different_len(): return len([x for x in filter(lambda p: len(p) != len(ps[0]), ps)]) > 0
            def contain_none(): return len([x for x in filter(lambda p: p is None, list(chain(*ps)))]) > 0
            return not contain_none() and not different_len()
        try:
            method = self.Method(*self.MethodParam)
            return method if is_param_safe(*method.params) else PendingMethod.VoidMethod()
        except TypeError:
            return PendingMethod.VoidMethod()


class ExecuteMethod:
    def __new__(cls, self: PendingMethod.Method) -> []:
        if not isinstance(self, PendingMethod.Method) or type(self).__name__ == 'VoidMethod':
            return [None]

        def reshape(x): return [[e[i] for e in x] for i in range(len(x[0]))]
        desc = f'\033[1;34m{type(self).__name__}\033'
        with ThreadPoolExecutor(max_workers=8) as pool:
            res = [r for r in tqdm(pool.map(self.fn_ea, *self.params), desc=desc, total=len(self.params[0]))]
        return self.close(*reshape(res)) if len(res) > 0 and res[0] is not None else res
