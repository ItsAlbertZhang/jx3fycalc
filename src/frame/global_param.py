# -*- coding: utf-8 -*-
import json


class GlobalParam():
    '''
        GlobalParam 类用于调用全局变量. 注意, 该类不应被实例化.
    '''
    try:
        with open('data/GlobalParam.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        raise RuntimeError('data/GlobalParam.json loads failed.')

    @classmethod
    def Cof(cls, level):  # 等级系数
        res = 0
        if level <= 15:
            res = 50
        elif 15 < level and level <= 90:
            res = 4 * level - 10
        elif 90 < level and level <= 95:
            res = 85 * (level - 90) + 350
        elif 95 < level and level <= 100:
            res = 185 * (level - 95) + 775
        elif 100 < level and level <= 110:
            res = 205 * (level - 100) + 1700
        elif 110 < level and level <= 130:
            res = 450 * (level - 110) + 3750
        return res

    @classmethod
    def CriticalStrikeCof(cls, level):  # 会心
        return cls.data['fCriticalStrikeParam'] * cls.Cof(level)

    @classmethod
    def CriticalDamagePowerCof(cls, level):  # 会心效果
        return cls.data['fCriticalStrikePowerParam'] * cls.Cof(level)

    @classmethod
    def OvercomeCof(cls, level):  # 破防
        return cls.data['fOvercomeParam'] * cls.Cof(level)

    @classmethod
    def SurplusCof(cls):  # 破招
        return cls.data['fSurplusParam']

    @classmethod
    def StrainCof(cls, level):  # 无双
        return cls.data['fInsightParam'] * cls.Cof(level)

    @classmethod
    def HasteCof(cls, level):  # 加速
        return cls.data['fHasteRate'] * cls.Cof(level)

    @classmethod
    def PhysicsShieldCof(cls, level):  # 外功防御
        return cls.data['fPhysicsShieldParam'] * cls.Cof(level)

    @classmethod
    def MagicShieldCof(cls, level):  # 内功防御
        return cls.data['fMagicShieldParam'] * cls.Cof(level)

    @classmethod
    def DodgeCof(cls, level):  # 闪避
        return cls.data['fDodgeParam'] * cls.Cof(level)

    @classmethod
    def ParryCof(cls, level):  # 招架
        return cls.data['fParryParam'] * cls.Cof(level)

    @classmethod
    def ToughnessDefCriticalCof(cls, level):  # 御劲
        return cls.data['fDefCriticalStrikeParam'] * cls.Cof(level)

    @classmethod
    def ToughnessDecirDamageCof(cls, level):  # 御劲减会伤
        return cls.data['fToughnessDecirDamageCof'] * cls.Cof(level)

    @classmethod
    def DecriticalDamagePowerCof(cls, level):  # 化劲
        return cls.data['fDecriticalStrikePowerParam'] * cls.Cof(level)
