import shutil
import zipfile
import aiofiles
import os
import aiofiles.os
import imageio
from abc import ABC, abstractmethod
from Main import output, asy_launch


class WriteMixin(ABC):
    pass


class CreWriteMixin(WriteMixin):
    @abstractmethod
    def write_in(self, download_infos, file_name):
        pass


class WriteIMG(CreWriteMixin):
    def write_in(self, download_infos, file_name):
        if not os.path.exists(f'./{file_name}'):
            os.makedirs(f'./{file_name}')

        async def write_in(params):
            img_bina, suffix, _id, page = params[0]
            async with aiofiles.open(f'./{file_name}/{_id}_p{page}.{suffix}', 'wb+') as f:
                await f.write(img_bina)
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (download_infos,))


class WriteGIF(CreWriteMixin):
    def write_in(self, download_infos, file_name):
        if not os.path.exists(file_name):
            os.makedirs(file_name)

        async def write_in(params):
            gif_bina, _id, delay = params[0]
            img_path = f'./{file_name}/{_id}'
            zip_path = f'./{file_name}/{_id}.zip'
            async with aiofiles.open(zip_path, "wb+") as fp:
                await fp.write(gif_bina)
            await aiofiles.os.mkdir(img_path)
            Zip(img_path, Zip.unzip)
            flames = [imageio.v3.imread(f'{img_path}/{img}') for img in Zip.Name_list]
            imageio.v2.mimsave(f'{img_path}.gif', flames, "GIF", duration=delay)
            shutil.rmtree(img_path)
            os.unlink(f'{zip_path}')
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (download_infos,))


class WriteCaller:
    def __init__(self, download_infos, file_name, write_in_mixin):
        if len(download_infos) > 0:
            output(f'writing in:{file_name}: ', form=1, code=31, end='')
            write_in_mixin.write_in(download_infos, file_name)
            output(f'[finish]', form=4, code=32)
        else:
            pass


class Zip:
    zip = 0
    unzip = 1
    Name_list = []

    def __init__(self, file_name, form):
        self.form = form
        self.zip_path = f'./{file_name}.zip'
        self.unzip_path = f'./{file_name}'
        self.run()

    def run(self):
        if self.form == Zip.zip:
            self._zip()
        else:
            if self.form == Zip.unzip:
                self._unzip()

    def _unzip(self):
        with zipfile.ZipFile(self.zip_path, "r") as unzip:
            unzip.extractall(self.unzip_path)
            Zip.Name_list = unzip.namelist()

    def _zip(self):
        with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            Zip.Name_list = z.namelist()
            for item in os.listdir(self.unzip_path):
                z.write(self.unzip_path + os.sep + item)

