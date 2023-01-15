from Process.Component.Parser import *
from Process.Component.Pipeline import *


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


class ProcLauncher:
    Result = []

    def __init__(self, mixin):
        self.MiddleLaunch(mixin, MiddleMixin)
        self.PackageLaunch(mixin, PackageMixin)
        self.WriteLaunch(mixin, CreWriteMixin)

    class Judge(ABC):
        def __init__(self, mixin, _class):
            self.mixin = mixin
            if isinstance(mixin, _class):
                self.process()

        @abstractmethod
        def process(self):
            pass

    class MiddleLaunch(Judge):
        def process(self):
            if self.mixin.id_list is not None:
                output('process ids: ', form=1, code=31, end='')
                ProcLauncher.Result = self.mixin.process_id()
                output(f'[finish]', form=4, code=32)

    class PackageLaunch(Judge):
        def process(self):
            if self.mixin.id_list is not None:
                output(f'expect source: ', form=1, code=31, end='')
                ProcLauncher.Result = self.mixin.package()
                output(f'[finish]', form=4, code=32)

    class WriteLaunch(Judge):
        def process(self):
            if self.mixin.download_infos is not None:
                if not os.path.exists(f'./{self.mixin.file_name}'):
                    os.makedirs(f'./{self.mixin.file_name}')
                output(f'writing in:{self.mixin.file_name}: ', form=1, code=31, end='')
                self.mixin.write_in()
                output(f'[finish]', form=4, code=32)
