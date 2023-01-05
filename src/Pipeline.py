import shutil
import zipfile
import aiofiles
import os
import aiofiles.os
import imageio
import urllib3
import nest_asyncio
from Main import *

urllib3.disable_warnings()
nest_asyncio.apply()
class Pipeline:
    @staticmethod
    def process_gif(download_infos, file_name):
        output(f'writing in:GIF {file_name}: ', form=1, code=31, end='')
        if not os.path.exists(file_name):
            os.makedirs(file_name)

        async def write_in(params):
            gif_bina, _id, delay = params[0]
            img_path = f'./{file_name}/{_id}'
            zip_path = f'./{file_name}/{_id}.zip'
            async with aiofiles.open(zip_path, "wb+") as fp:
                await fp.write(gif_bina)
            await aiofiles.os.mkdir(img_path)
            with zipfile.ZipFile(zip_path, "r") as unzip:
                unzip.extractall(img_path)
            flames = [imageio.v3.imread(f'{img_path}/{img}') for img in unzip.namelist()]
            imageio.v2.mimsave(f'{img_path}.gif', flames, "GIF", duration=delay)
            shutil.rmtree(img_path)
            os.unlink(f'{zip_path}')
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (download_infos,))
        output(f'[finish]', form=4, code=32)

    @staticmethod
    def process_img(download_infos, file_name):
        output(f'writing in:IMG {file_name}: ', form=1, code=31, end='')
        if not os.path.exists(f'./{file_name}'):
            os.makedirs(f'./{file_name}')

        async def write_in(params):
            img_bina, suffix, _id, page = params[0]
            async with aiofiles.open(f'./{file_name}/{_id}_p{page}.{suffix}', 'wb') as f:
                await f.write(img_bina)
            output('#', code=33, form=4, end='')

        asy_launch(write_in, (download_infos,))
        output(f'[finish]', form=4, code=32)

    @staticmethod
    def zip(file_name):
        output(f'zipping {file_name}: ', form=1, code=31, end='')
        zip_file = f'./{file_name}.zip'
        z = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        for item in os.listdir(f'./{file_name}'):
            z.write(f'./{file_name}' + os.sep + item)
            output('#', code=33, form=4, end='')
        z.close()
        output(f'[finish]', form=4, code=32)