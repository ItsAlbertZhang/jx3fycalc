# -*- coding: utf-8 -*-
import bisect


class Event():
    '''
        Event 类为事件列表, 用于处理时间线上的事件. 注意, 该类不应被实例化.
    '''
    tick = 0  # 时间线. 每 1024 tick 为 1 秒.
    tick_list = []  # 待处理事件列表对应的 tick. 应当始终按时间升序排列.
    event_list = []  # 待处理事件列表. 应当始终按时间升序排列.

    @classmethod
    def add(cls, tick: int, func, *args, **kwargs) -> int:
        '''
            添加事件. 注意传入的参数:
            - `tick` : 离处理事件的 tick 数.
            - `func` : 事件处理函数.
            - `*args`, `**kwargs` : 事件处理函数的参数.

            返回值为事件处理瞬间的 tick.
        '''
        if type(tick) != int:
            raise RuntimeError('Tick must be of type int.')
        handle_tick = cls.tick + tick  # 获取处理事件的 tick
        index = bisect.bisect_left(cls.tick_list, handle_tick)
        cls.tick_list.insert(index, handle_tick)  # 插入待处理事件列表
        cls.event_list.insert(index, (func, args, kwargs))  # 插入待处理事件列表对应的 tick
        return handle_tick

    @classmethod
    def handle(cls):  # 处理一次事件
        if 0 == len(cls.tick_list):
            # 若事件列表为空, 则直接返回.
            return
        # print('\n开始处理下一次事件...', end='')
        cls.tick = cls.tick_list.pop(0)  # 取出第一个事件的处理 tick, 并将其赋给 cls.tick (步进时间).
        func, args, kwargs = cls.event_list.pop(0)  # 取出第一个事件的处理函数和参数
        # print(cls.tick, func, args, kwargs)
        func(*args, **kwargs)  # 执行处理事件函数
        if 0 == len(cls.tick_list):
            # 如果此时事件列表为空, 则计算 dps 并记录
            cls._dps = cls.dps  # 语法糖, 实际上是通过 getter 拿到当前的 dps 并通过 setter 赋给 cls._dps
            # cls.damage_list.clear()  # 将伤害列表置空
            # cls.tick = 0  # 重置时间
        # print('处理完毕!')

    # @classmethod
    # def clear(cls):
    #     if len(cls.tick_list) > 0:
    #         raise RuntimeError('Event list is not empty, cannot clear.')
    #     else:
    #         # cls.damage_list.clear()  # 将伤害列表置空
    #         cls.tick = 0  # 重置时间

    @classmethod
    def delete(cls, tick: int, func, *args, **kwargs) -> bool:
        '''提前移除事件.'''
        index = bisect.bisect_left(cls.tick_list, tick)
        while cls.tick_list[index] == tick:
            if func == cls.event_list[index][0] and args == cls.event_list[index][1] and kwargs == cls.event_list[index][2]:
                cls.tick_list.pop(index)  # 取出事件处理 tick
                cls.event_list.pop(index)  # 取出事件的处理函数
                return True
            else:
                index += 1
        return False
