# -*- coding: utf-8 -*-
from src.frame.script import Script
from src.frame.fetchdata import TabAttr


class Skill():
    '''
        Skill 类用于存放某个对象的技能并实现相关功能, 可以通俗地理解为技能列表.
    '''
    tabattr = TabAttr('settings/skill/skills.tab')
    general_table = {}  # 初始化哈希表, 用于存放未学习的通用技能

    def __init__(self) -> None:
        self.table = {}  # 初始化哈希表, 用于存放当前对象的所有已学习技能

    def learn(self, SkillID, Level):
        # 获取技能属性
        skill_attr = self.__class__.tabattr.fetch('SkillID', SkillID)
        if Level > skill_attr['MaxLevel']:
            raise RuntimeError('Learn skill failed.')
        # 将技能添加至哈希表, 并覆盖当前技能
        self.table[SkillID] = {
            'skill_attr': skill_attr,
            'SkillID': SkillID,
            'Level': Level,
            'cd_list': [0, 0, 0, 0],
        }

    def cast(self, SkillID, Level=None, *args, **kwargs):
        '''
            注意: 此方法返回的是一个 tuple, 而非伤害, 原因在于伤害的计算需要与角色属性进行耦合. 如果希望计算伤害, 应当使用 Player 类的 cast 方法.
            施展技能. 传入的参数应当原封不动传递给执行脚本, 再传递给脚本模块类中的 cast 方法. 返回值为 伤害值(int) 或 None.
        '''
        if SkillID in self.table:
            arg_skill = self.table[SkillID]
        elif SkillID in self.__class__.general_table:
            arg_skill = self.__class__.general_table[SkillID]
        else:
            # if None == Level:
            raise RuntimeError(f'Cast {SkillID} error. Need a learnt skill or skill\'s level.')
            # else:
            #     # 将技能添加至通用技能表
            #     self.__class__.general_table[SkillID] = {
            #         'skill_attr': self.__class__.tabattr.fetch('SkillID', SkillID),
            #         'SkillID': SkillID,
            #         'Level': Level,
            #         'cd_list': [],
            #     }
        # 实现 skill recipe
        # 已在 character.player.Player.CastSkill() 中实现
        return Script.execute(arg_skill['skill_attr']['ScriptFile'], arg_skill, *args, **kwargs)

    def forget(self, SkillID):
        '''遗忘技能.'''
        self.table.pop(SkillID)

    def is_exist(self, SkillID, Level=None):
        if None == Level:
            return SkillID in self.table
        else:
            return SkillID in self.table and self.table[SkillID]['Level'] == Level

    def get_level(self, SkillID):
        if not SkillID in self.table:
            return 0
        else:
            return self.table[SkillID]['Level']

    def get_attr(self, SkillID):
        return self.__class__.tabattr.fetch('SkillID', SkillID)

    def init_dict(self, SkillID, Level):
        if SkillID in self.table:
            return self.table[SkillID]
        elif SkillID in self.__class__.general_table:
            return self.__class__.general_table[SkillID]
        elif Level is not None:
            # 将技能添加至通用技能表
            self.__class__.general_table[SkillID] = {
                'skill_attr': self.__class__.tabattr.fetch('SkillID', SkillID),
                'SkillID': SkillID,
                'Level': Level,
                'cd_list': [0, 0, 0, 0],
            }
            return self.__class__.general_table[SkillID]
        else:
            raise RuntimeError(f'Init {SkillID} error. Need a learnt skill or skill\'s level.')

    def set_cd(self, SkillID, ID, index=0):
        if SkillID in self.table:
            self.table[SkillID]['cd_list'][index] = ID
        elif SkillID in self.__class__.general_table:
            self.__class__.general_table[SkillID]['cd_list'][index] = ID
        else:
            raise RuntimeError('Need to learn skills before set cd.')

    def get_cd_list(self, SkillID):
        if SkillID in self.table:
            return self.table[SkillID]['cd_list']


class SkillEffectList():
    '''
        SkillEffectQueue 类是技能效果的列表.
    '''

    def __init__(self) -> None:
        self.effect = []  # 定义一个列表, 用于存放技能效果

    @property
    def empty(self):
        return len(self.effect) == 0

    def push(self, SkillID, Level, func, *args, **kwargs):
        self.effect.append((SkillID, Level, func, args, kwargs))

    def pop(self, SkillID, Level):
        l = len(self.effect)
        for i in range(l):
            index = l - i - 1
            s_SkillID, _, s_func, s_args, s_kwargs = self.effect[index]
            if s_SkillID == SkillID:
                s_func(*s_args, **s_kwargs)
                self.effect.pop(index)

    # def pop_by_func(self, SkillID, func):
    #     l = len(self.effect)
    #     for i in range(l):
    #         index = l - i - 1
    #         s_SkillID, _, s_func, s_args, s_kwargs = self.effect[index]
    #         if s_SkillID == SkillID and s_func == func:
    #             s_func(*s_args, **s_kwargs)
    #             self.effect.pop(index)


class SkillCastQueue():
    '''
        SkillCastQueue 类是技能释放的队列.
    '''

    def __init__(self) -> None:
        self.cast = []  # 定义一个队列, 用于存放技能

    @property
    def empty(self):
        return len(self.cast) == 0

    def enqueue(self, SkillID, Level, *args, **kwargs):
        self.cast.append((SkillID, Level, args, kwargs))

    def dequeue(self):
        return self.cast.pop(0)
