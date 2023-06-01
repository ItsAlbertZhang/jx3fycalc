# -*- coding: utf-8 -*-
from src.frame.event import Event
from src.frame.fetchdata import TabAttr


class CoolDown():
    '''
        SkillEvent 类用于存放某个对象的技能 CD 并实现相关功能.
    '''
    tabattr = TabAttr('settings/CoolDownList.tab')

    def __init__(self) -> None:
        self.table = {}
        # self.df = None  # 初始化, 用于存放当前对象的所有技能 CD 列表
        pass

    def check_notin_cd(self, ID):
        return ID not in self.table

    def setcd(self, ID, Add=0, haste=0) -> int:
        if ID in self.table:  # 判断技能能否释放 (是否处于 CD 中)
            raise RuntimeError('Cool down is not finished.', ID)
        # 获取技能 CD 属性
        cooldown_attr = self.__class__.tabattr.fetch('ID', ID)
        cooldown_duration = int(cooldown_attr['Duration'] * 16) + Add
        # if None == Add:
        # 加速处理
        cooldown_duration = int(cooldown_duration * (1024 - haste) / 1024)
        cooldown_duration = max(cooldown_duration, int(cooldown_attr['MinDuration'] * 16 + Add))
        cooldown_duration = min(cooldown_duration, int(cooldown_attr['MaxDuration'] * 16 + Add))
        # else:
        #     cooldown_duration = Add
        self.table[ID] = {
            'cooldown_attr': cooldown_attr,
            'cooldown_duration': cooldown_duration,
        }

        cooldown_tick = Event.add(int(cooldown_duration * 1024 / 16), self.over, ID)
        self.table[ID]['cooldown_tick'] = cooldown_tick  # 将 cooldown_tick 添加至哈希表
        return cooldown_tick

    def modify(self, ID, time_tick) -> int:  # value 为正值代表增加 CD
        if ID in self.table:
            new_cooldown_duration_tick = int(self.table[ID]['cooldown_tick'] - Event.tick + time_tick)
            Event.delete(self.table[ID]['cooldown_tick'], self.over, ID)
            if new_cooldown_duration_tick > 0:
                new_cooldown_tick = Event.add(new_cooldown_duration_tick, self.over, ID)
                self.table[ID]['cooldown_tick'] = new_cooldown_tick
                return new_cooldown_tick
            else:
                self.table.pop(ID)
                return Event.tick

    def over(self, ID):
        '''冷却结束.'''
        self.table.pop(ID)

    def clear_cd(self, ID):
        if ID in self.table:
            Event.delete(self.table[ID]['cooldown_tick'], self.over, ID)
            self.over(ID)

    def is_in_cd(self, ID):
        return ID in self.table

    def get_cd_tick(self, cd_list: list):
        cd_tick = 0
        for i in cd_list:
            if i in self.table:
                cd_tick = max(cd_tick, self.table[i]['cooldown_tick'])
        return cd_tick
