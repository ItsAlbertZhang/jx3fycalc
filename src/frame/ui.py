# -*- coding: utf-8 -*-
import pandas as pd
from src.frame.fetchdata import TabAttr


class SkillUI():
    '''
        SkillUI 类用于存放技能的 UI 信息. 由于功能不多, 使用单例模式.
    '''
    tabattr = TabAttr('ui/Scheme/Case/skill.txt')

    @classmethod
    def get_name(cls, SkillID, Level) -> str:
        ret = ''
        res = cls.tabattr.fetch(['SkillID', 'Level'], [SkillID, Level], alternative_value_list=[[SkillID, 0]])
        if type(res) == pd.Series:
            ret = res['Name']
        return ret


class BuffUI():
    '''
        BuffUI 类用于存放技能的 UI 信息. 由于功能不多, 使用单例模式.
    '''
    tabattr = TabAttr('ui/Scheme/Case/buff.txt')

    @classmethod
    def get_name(cls, BuffID, Level) -> str:
        ret = ''
        res = cls.tabattr.fetch(['BuffID', 'Level'], [BuffID, Level], alternative_value_list=[[BuffID, 0]])
        if type(res) == pd.Series:
            ret = res['Name']
        return ret
