# -*- coding: utf-8 -*-
import pandas as pd
from src.frame.fetchdata import TabAttr


class SkillEvent():
    '''
        SkillEvent 类用于存放某个对象的技能触发事件并实现相关功能, 可以通俗地理解为触发类事件列表.
    '''
    tabattr = TabAttr('settings/skill/SkillEvent.tab')

    def __init__(self) -> None:
        # self.df = None  # 初始化, 用于存放当前对象的所有技能触发事件
        self.df = self.__class__.tabattr.fetch('ID', 0).to_frame().T
        self.forget(0)
        pass

    def add(self, ID):
        # 获取技能触发事件属性
        skillevent_attr = self.__class__.tabattr.fetch('ID', ID)
        self.df = pd.concat([self.df, skillevent_attr.to_frame().T], axis=0)

    def forget(self, ID):
        '''取消技能触发事件.'''
        self.df = self.df[self.df['ID'] != ID]

    def is_exist(self, ID):
        return ID in self.df.index

    def get_by_EventSkillID(self, EventSkillID) -> pd.DataFrame:
        return self.df[self.df['EventSkillID'] == EventSkillID]

    def get_by_EventMask(self, EventMask1, EventMask2) -> pd.DataFrame:
        return self.df[(self.df['EventMask1'] & EventMask1) | (self.df['EventMask2'] & EventMask2)]


class RandomEvent():
    '''
        RandomEvent 类用于存放某个对象的随机事件.
    '''

    def __init__(self) -> None:
        self.random_event = []

    def push(self, func, *args, **kwargs):
        self.random_event.append((func, args, kwargs))

    def apply(self):
        while len(self.random_event) > 0:
            func, args, kwargs = self.random_event.pop()
            func(*args, **kwargs)
