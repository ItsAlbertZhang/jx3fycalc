# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Union
import asyncio
import hashlib
import json
import multiprocessing
# import time
import websockets.legacy.server as websockets


class Program():
    def __init__(self, pipe=None) -> None:
        scripts_dir = Path('./src/scripts')
        process_init_filename = './src/worker_calc/__init__.py'
        if scripts_dir.exists() and scripts_dir.is_dir():
            with open(process_init_filename, 'w+', encoding='utf-8') as f:
                f.write(f'# -*- coding: utf-8 -*-\n')
                for path in scripts_dir.iterdir():
                    if path.is_file() and path.suffix == '.py':
                        module_name = path.stem
                        f.write(f'import src.scripts.{module_name}\n')
            # print('Init completely.')
        self.pipe = pipe
        self.stop_event = asyncio.Event()

    def main(self):
        # init
        self.child_arg = self.arg_init()
        multiprocessing.freeze_support()
        self.process_calc = ProgramChildCalc(self)
        self.process_attrbenefit = ProgramChildAttrBenefit(self)

        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.server()),
            loop.create_task(self.task_pipe())
        ]
        loop.run_until_complete(asyncio.wait(tasks))

        self.cleanup()

    def cleanup(self):
        self.process_calc.cleanup()
        self.process_attrbenefit.cleanup()

    async def task_pipe(self):
        while True:
            if self.pipe is not None:
                if self.pipe.poll():
                    self.stop_event.set()
                    break
                await asyncio.sleep(1)
            else:
                await asyncio.Future()

    async def server(self):
        async with websockets.serve(self.server_handle, "localhost", 8765):
            await self.stop_event.wait()

    async def server_handle(self, websocket: websockets.WebSocketServerProtocol):
        self.websocket = websocket
        # 接收数据
        async for message in websocket:
            try:
                self.child_arg = json.loads(message)
            except:
                print('json.loads error.')
                return
            if not self.arg_check():
                print('arg_check error.')
                return

            await self.send_message(category='data_begin')

            cachename = hashlib.md5(json.dumps(self.child_arg['fight']).encode('utf-8')).hexdigest()
            random_event_work = self.child_arg['fight']['random_event_work']
            if not Path(f'data/cache/{cachename}').exists() or random_event_work:
                # await websocket.send('模型不存在, 或是开启了随机事件, 正在重新建立模型.')
                # start_time = time.time()
                await self.worker_calc_handle()
                # end_time = time.time()
                # run_time = int((end_time - start_time) * 1000)
                # await self.send_message(category='time_spent', data=run_time)
            if Path(f'data/cache/{cachename}').exists():  # 如果还是不存在, 说明 worker_calc 运行出错, 此时不再运行 worker_attrbenefit
                # start_time = time.time()
                await self.worker_attrbenefit_handle()
                # end_time = time.time()
                # run_time = int((end_time - start_time) * 1000)
                # await self.send_message(category='time_spent', data=run_time)

            await self.send_message(category='data_end')

    async def worker_calc_handle(self):
        await self.process_calc.handle(self.child_arg)
        self.process_calc.reset()

    async def worker_attrbenefit_handle(self):
        await self.process_attrbenefit.handle(self.child_arg)
        self.process_attrbenefit.reset()

    async def send_message(self, category: str, data: Union[None, dict] = None):
        message = {
            'category': category,
        }
        if data is not None:
            message['data'] = data
        await self.websocket.send(json.dumps(message, ensure_ascii=False))

    def arg_init(self) -> dict:
        ret = {
            'attr_self': '{}',
            'attr_target': '{}',
            'env': '{}',
            'fight': '{}',
        }
        # try:
        #     with open('data/defaultattr.json', 'r', encoding='utf-8') as f:
        #         ret['attr_self'] = json.dumps(json.loads(f.read()), ensure_ascii=False)
        # except FileNotFoundError:
        #     pass
        # try:
        #     with open('data/targetattr.json', 'r', encoding='utf-8') as f:
        #         ret['attr_target'] = json.dumps(json.loads(f.read()), ensure_ascii=False)
        # except FileNotFoundError:
        #     pass
        # try:
        #     with open('data/fight.json', 'r', encoding='utf-8') as f:
        #         ret['fight'] = json.dumps(json.loads(f.read()), ensure_ascii=False)
        # except FileNotFoundError:
        #     pass
        return ret

    def arg_check(self) -> bool:
        standard = {
            'attr_self': {
                "attr": '',
                "recipe_skill": '',
                "talent_list": ''
            },
            'attr_target': {
                "attr": ''
            },
            'env': '',
            'fight': {
                "ping": '',
                "skill_list": '',
                "options": {},
                "random_event_work": '',
                "random_events": {},
                "include": {
                    "normal_skill": '',
                    "special_skill": '',
                    "lists": ''
                }
            },
        }

        def check_dict(standard, obj) -> bool:
            ret = True
            for key in standard:
                if key not in obj:
                    return False
                else:
                    if type(standard[key] == dict):
                        ret = ret and check_dict(standard[key], obj[key])
            return ret

        ret = check_dict(standard, self.child_arg)

        # fight skill_list 额外检查
        for i in self.child_arg['fight']['skill_list']:
            if i not in self.child_arg['fight']['include']['lists']:
                return False

        return ret


def child_calc_entry(queue_put, queue_get):
    '''子进程的入口函数. 不能放在子进程类中, 以避免子进程递归实例化子进程.'''
    import src.worker_calc.handle as child
    child.handle(queue_put, queue_get)


class ProgramChildCalc():
    '''用于计算的子进程.'''

    def __init__(self, parent) -> None:
        self.parent: Program = parent
        self.queue_put = multiprocessing.Queue()
        self.queue_get = multiprocessing.Queue()
        self.process_worker = multiprocessing.Process(target=child_calc_entry, args=(self.queue_put, self.queue_get))
        self.process_worker.start()

    def cleanup(self):
        '''清理子进程.'''
        self.process_worker.terminate()

    def reset(self):
        '''重置子进程.'''
        self.process_worker.join()
        self.process_worker = multiprocessing.Process(target=child_calc_entry, args=(self.queue_put, self.queue_get))
        self.process_worker.start()

    async def handle(self, arg):
        '''子进程业务函数.'''
        self.queue_put.put(arg)
        await self.parent.send_message(category='damage_begin')
        while True:
            try:
                message = self.queue_get.get_nowait()
            except:
                await asyncio.sleep(0.1)
                continue
            if type(message) == dict:
                data = None
                if 'data' in message:
                    data = message['data']
                await self.parent.send_message(category=message['category'], data=data)
            else:
                await self.parent.send_message(category='damage_end')
                message: list
                for i in message:
                    data = None
                    if 'data' in i:
                        data = i['data']
                    await self.parent.send_message(category=i['category'], data=data)
                break


def child_attrbenefit_entry(index: int, pub_arg: dict):
    '''子进程的入口函数. 不能放在子进程类中, 以避免子进程递归实例化子进程.'''
    import src.worker_attrbenefit.handle as child
    return child.handle(index, pub_arg)


def child_fastcalc_entry(queue_put, queue_get):
    '''子进程的入口函数. 不能放在子进程类中, 以避免子进程递归实例化子进程.'''
    import src.worker_attrbenefit.handle as child
    child.handle(0, None, queue_put, queue_get)


class ProgramChildAttrBenefit():
    def __init__(self, parent) -> None:
        self.parent: Program = parent
        self.queue_put = multiprocessing.Queue()
        self.queue_get = multiprocessing.Queue()
        self.arg_list = ['元气收益', '攻击收益', '会心收益', '会效收益', '破防收益', '无双收益', '破招收益']
        self.process_pool = multiprocessing.Pool(processes=len(self.arg_list), maxtasksperchild=1)
        self.process_worker = multiprocessing.Process(target=child_fastcalc_entry, args=(self.queue_put, self.queue_get))
        self.process_worker.start()

    def cleanup(self):
        '''清理子进程.'''
        self.process_worker.terminate()

    def arg_init(self, arg):
        ret = []
        for i in range(len(self.arg_list)):
            ret.append((i+1, arg))
        return ret

    def reset(self):
        self.process_pool.close()
        self.process_pool.join()
        self.process_pool = multiprocessing.Pool(processes=len(self.arg_list), maxtasksperchild=1)
        self.process_worker.join()
        self.process_worker = multiprocessing.Process(target=child_fastcalc_entry, args=(self.queue_put, self.queue_get))
        self.process_worker.start()

    async def handle(self, arg):
        self.queue_put.put(arg)
        await self.parent.send_message(category='damage_begin')
        arg_iterable = self.arg_init(arg)
        results = self.process_pool.starmap_async(child_attrbenefit_entry, arg_iterable)
        while True:
            try:
                message = self.queue_get.get_nowait()
            except:
                await asyncio.sleep(0.05)
                continue
            if type(message) == dict:
                data = None
                if 'data' in message:
                    data = message['data']
                await self.parent.send_message(category=message['category'], data=data)
            else:
                await self.parent.send_message(category='damage_end')
                message: list
                for i in message:
                    data = None
                    if 'data' in i:
                        data = i['data']
                    await self.parent.send_message(category=i['category'], data=data)
                    if i['category'] == 'fight_stat' and data and 'dps' in data:
                        dps = i['data']['dps']
                break
        while not results.ready():
            await asyncio.sleep(0.05)
        results = results.get()
        attr_benefit = {}
        for i in range(len(self.arg_list)):
            attr_benefit[self.arg_list[i]] = (results[i] - dps) / (results[1] - dps)
        await self.parent.send_message(category='attr_benefit', data=attr_benefit)
