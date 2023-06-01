# -*- coding: utf-8 -*-
from src.frame.fetchdata import TabAttr
import pandas as pd


class Talent():
    '''
        Talent 类用于存放某个对象奇穴信息, 可以通俗地理解为奇穴列表.
        注意, 奇穴的真实实现在 Skill 类中.
    '''
    tabattr = TabAttr('settings/skill/TenExtraPoint.tab')

    @classmethod
    def get_talent_list(cls, KungFuID):
        df: pd.DataFrame = cls.tabattr.fetch('KungFuID', KungFuID)
        ret = []
        for _, row in df.iterrows():
            list_add = []
            for i in range(5):  # 奇穴最多有5个可选
                if not pd.isna(row[f'SkillID{i+1}']):
                    list_add.append(int(row[f'SkillID{i+1}']))
            ret.append(list_add)
        return ret
