# -*- coding: utf-8 -*-
from src.frame.event import Event
from src.frame.fetchdata import TabAttr


class Buff():
    '''
        Buff 类用于存放某个对象的 buff 并实现相关功能, 可以通俗地理解为 buff 列表.
    '''
    tabattr = TabAttr('settings/skill/buff.tab')

    def __init__(self) -> None:
        self.atHaste = 0
        self.table = {}  # 初始化哈希表, 用于存放当前对象的所有 buff

    def init_add(self, ID, Level, stacknum):
        # 获取 buff 属性
        buff_attr = self.__class__.tabattr.fetch(['ID', 'Level'], [ID, Level])
        buff_interval = buff_attr['Interval']
        buff_count = buff_attr['Count']
        key = f'{ID}_{Level}'
        if key not in self.table:  # 如果当前没有该 buff
            buff_dict = {
                'buff_attr': buff_attr,
                'ID': ID,
                'Level': Level,
                'buff_interval': buff_interval,
                'buff_count': buff_count,
                'buff_stacknum': stacknum,
            }
        else:
            buff_dict = self.table[key]
        return buff_dict

    def add(self, buff_dict, time_tick):
        buff_attr = buff_dict['buff_attr']
        ID = buff_dict['ID']
        Level = buff_dict['Level']
        buff_interval = buff_dict['buff_interval']
        buff_count = buff_dict['buff_count']
        key = f'{ID}_{Level}'
        if time_tick is None:
            timeset = int(buff_interval * 1024 / 16)
        else:
            timeset = int(time_tick)

        if key not in self.table:  # 如果当前没有该 buff
            self.table[key] = buff_dict  # 将 buff 添加至哈希表
            if timeset > 0:
                buff_tick = Event.add(timeset, self.active, ID, Level)
                self.table[key]['buff_tick'] = buff_tick  # 将 buff_tick 添加至哈希表
        else:  # 如果当前已有该 buff
            if not 'Damage' == buff_attr['FunctionType'] and not 'Hot' == buff_attr['FunctionType']:  # 如果 buff 类型不是 DOT 和 HOT
                self.delete(ID, Level, pop_table=False, all=True)  # 移除 buff, 但不移出哈希表, 仅移出事件列表
                if timeset > 0:
                    buff_tick = Event.add(timeset, self.active, ID, Level)  # 再次添加至事件列表
                    self.table[key]['buff_tick'] = buff_tick  # 将 buff_tick 添加至哈希表
            else:  # 是 DOT 或 HOT, 则刷新跳数
                self.table[key]['buff_count'] = buff_attr['Count']
            if 1 == buff_attr['IsStackable']:  # 如果 buff 允许叠层
                self.table[key]['buff_stacknum'] = min(buff_attr['MaxStackNum'], self.table[key]['buff_stacknum'] + 1)
            self.delete(ID, Level, False, False, True)  # 删除 buff 属性以重新初始化
        # 实现 buff ActiveAttribute
        # 已在 character.player.Player.Addbuff() 中实现

    def init_active(self, buff_dict, func, *args, **kwargs):
        ID = buff_dict['ID']
        Level = buff_dict['Level']
        key = f'{ID}_{Level}'
        if not 'atActive' in self.table[key]:
            self.table[key]['atActive'] = []
        self.table[key]['atActive'].append((func, args, kwargs))

    def active(self, ID, Level):
        '''处理 Active 事件. 此方法由事件列表调用.'''
        key = f'{ID}_{Level}'

        # 实现 buff ActiveAttribute
        # 已在 character.player.Player.Addbuff() 中实现
        if 'atActive' in self.table[key]:
            for i in self.table[key]['atActive']:
                s_func, s_args, s_kwargs = i
                s_func(*s_args, **s_kwargs)

        if 1 == self.table[key]['buff_count']:
            self.delete(ID, Level, delete_event=False, all=True)  # 移除 buff, 由于导致 ActiveBuff 的正是事件列表的取出处理, 因此无需再移出事件列表, 仅需移出哈希表
        else:  # 计数类 buff 特殊处理
            self.table[key]['buff_count'] -= 1
            self.table[key]['buff_tick'] = Event.add(int(self.table[key]['buff_interval'] * 1024 / 16), self.active, ID, Level)

    def init_delete(self, buff_dict, func, *args, **kwargs):
        ID = buff_dict['ID']
        Level = buff_dict['Level']
        key = f'{ID}_{Level}'
        if not 'atEndTime' in self.table[key]:
            self.table[key]['atEndTime'] = []
        self.table[key]['atEndTime'].append((func, args, kwargs))

    def delete(self, ID, Level=None, delete_event=True, pop_table=True, all=False):
        '''移除 buff. 分为两个部分: 移出哈希表和移出事件列表. 两部分可以单独进行, 但如果都需要进行, 则应先移出事件列表.'''
        def temp_delete(key, delete_event, pop_table, all):
            if not all and self.table[key]['buff_stacknum'] > 1:
                # 这里肯定有 bug, 为了避免 bug, 这里做一个白名单
                whitelist = ['12850_2', '25716_1', '25716_2']
                if key in whitelist:
                    self.table[key]['buff_stacknum'] -= 1
                else:
                    raise RuntimeError('Need whitelist.', key, self.table[key]['buff_attr']['Name'])
            else:
                # 实现 buff EndTimeAttribute
                # 已在 character.player.Player.Addbuff() 中实现
                if 'atEndTime' in self.table[key]:
                    while len(self.table[key]['atEndTime']) > 0:
                        s_func, s_args, s_kwargs = self.table[key]['atEndTime'].pop()
                        s_func(*s_args, **s_kwargs)
                if 'atActive' in self.table[key]:
                    while len(self.table[key]['atActive']) > 0:
                        self.table[key]['atActive'].pop()
                parts = key.split('_')
                if delete_event and 'buff_tick' in self.table[key]:
                    Event.delete(self.table[key]['buff_tick'], self.active, int(parts[0]), int(parts[1]))
                if pop_table:
                    self.table.pop(key)
        key_list = self._get_key(ID, Level)
        for key in key_list:
            temp_delete(key, delete_event, pop_table, all)

    def is_exist(self, ID, Level=None):
        ret = self._get_key(ID, Level)
        return len(ret) > 0

    def get_dict(self, ID, Level=None):
        ret = self._get_key(ID, Level)
        for i in range(len(ret)):
            ret[i] = self.table[ret[i]]
        return ret

    def get_left_tick(self, ID, Level=None):
        ret_key = self._get_key(ID, Level)
        ret_left_tick = []
        for key in ret_key:
            ret_left_tick.append(self.table[key]['buff_tick'] - Event.tick)
        return ret_left_tick, ret_key

    def _get_key(self, ID, Level):
        ret = []
        if Level is None or Level == 0:
            for key in self.table:
                if f'{ID}' in key:
                    ret.append(key)
        if Level is not None and Level > 0:
            key = f'{ID}_{Level}'
            if key in self.table:
                ret.append(key)
        return ret
