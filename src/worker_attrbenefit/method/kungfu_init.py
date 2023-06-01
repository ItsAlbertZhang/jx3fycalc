# -*- coding: utf-8 -*-
from src.worker_attrbenefit.subattr import SubAttr

'''
    以下的方法被作为本 module 的 attr 在 src.worker_attrbenefit.init 中被 getattr 读取.
    读取时的依据为 data/player.json 中的 data['KungFuSkill']['name'].
'''


def init_焚影圣诀(obj: SubAttr):
    # 额外攻击力转换
    def calc_attack_power_add(self):
        return int(self.atSpunkBase * 1946 / 1024)  # 1 点元气转换为 1946 / 1024 点攻击力
    obj.kungfuSolarAttackPowerAdd = calc_attack_power_add
    obj.kungfuLunarAttackPowerAdd = calc_attack_power_add

    # 额外会心转换
    def calc_critical_strike_add(self):
        return int(self.atSpunkBase * 297 / 1024)  # 1 点元气转换为 297 / 1024 点会心等级
    obj.kungfuSolarCriticalStrikeAdd = calc_critical_strike_add
    obj.kungfuLunarCriticalStrikeAdd = calc_critical_strike_add

    obj.bool_kungfu_init_over = True
