# -*- coding: utf-8 -*-
from typing import BinaryIO
from src.frame.attribute import Attribute
from src.frame.event import Event
from src.frame.global_param import GlobalParam
import json


class Damage():
    """
        Damage 类为伤害列表, 用于处理伤害事件. 注意, 该类不应当被实例化.
    """
    damage_list = []  # 伤害列表. 从 0 时刻开始起的所有伤害均记录在内.
    model_list = []
    _dps = 0
    connect_queue = None

    @classmethod
    @property
    def dps(cls):
        if 0 != Event.tick:
            sum_damage = 0
            for item in cls.damage_list:
                sum_damage += item['damage']['except']
            return sum_damage * 1024 / Event.tick
        else:
            return cls._dps

    @classmethod
    def damagecalc_source(cls, selfattr: Attribute, targetattr: Attribute, SkillID, Level, skill, name, skilltype, kindtype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus=False, channel_interval_cof=1, export_model=True):
        '''原始伤害计算'''
        raw_ap = int(getattr(selfattr, f'calc{skilltype}AttackPower') * int(nChannelInterval) * channel_interval_cof / 16 / (10 if 'Physics' == skilltype else 12))
        if surplus:
            raw_ap = int(selfattr.atSurplusValueBase * GlobalParam.SurplusCof() * nChannelInterval)
        raw_min = int(nDamageBase) + raw_ap + int(selfattr.atMeleeWeaponDamageBase * nWeaponDamagePercent / 1024)
        raw_max = int(nDamageBase + nDamageRand) + raw_ap + int((selfattr.atMeleeWeaponDamageBase + selfattr.atMeleeWeaponDamageRand) * nWeaponDamagePercent / 1024)
        cof_overcome = 1024 + getattr(selfattr, f'calc{skilltype}Overcome')
        cof_damage_add_percent = 1024 + getattr(selfattr, f'calc{skilltype}DamageAddPercent')
        cof_damage_add_by_dstmovestate = 1024 + selfattr.atAddDamageByDstMoveState
        cof_strain = 1024 + (selfattr.calcStrain if targetattr.is_npc else 0)
        cof_npc = 1024 + (selfattr.atDstNpcDamageCoefficient if targetattr.is_npc else 0)
        cof_list = [cof_overcome, cof_damage_add_percent, cof_damage_add_by_dstmovestate, cof_strain, cof_npc]
        cof = 1 + (selfattr.level - targetattr.level) * 0.05 * (3 if selfattr.level > targetattr.level else 1)
        for i in cof_list:
            cof *= i
        base_damage_min = int(raw_min * cof / (1024**len(cof_list)))
        base_damage_max = int(raw_max * cof / (1024**len(cof_list)))
        critical_damage_min = int(base_damage_min * 1.75) + int(base_damage_min * getattr(selfattr, f'calc{kindtype}CriticalDamagePower') / 1024)
        critical_damage_max = int(base_damage_max * 1.75) + int(base_damage_max * getattr(selfattr, f'calc{kindtype}CriticalDamagePower') / 1024)
        critical_except = min(getattr(selfattr, f'calc{kindtype}CriticalStrike'), 10000)
        except_damage = 0
        damage_source = {
            'HashID': f'{Event.tick}_{SkillID}_{Level}',
            'SkillID': SkillID,
            'Level': Level,
            'skill': skill,
            'name': name,
            'base': {
                'min': base_damage_min,
                'max': base_damage_max,
            },
            'critical': {
                'min': critical_damage_min,
                'max': critical_damage_max,
            },
            'critical_except': critical_except,
            'except': except_damage,
            'skilltype': skilltype,
        }

        if export_model:
            a = ('damagecalc_source', Event.tick, (selfattr.export_stat_change(), targetattr.export_stat_change()), (SkillID, Level, skill, name, skilltype, kindtype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus, channel_interval_cof))
            cls.model_list.append(a)

        return damage_source

    @classmethod
    def damagecalc_last(cls, selfattr: Attribute, targetattr: Attribute, damage_source, export_model=True):
        '''最终伤害计算'''
        def mydictcopy(src: dict):  # 递归复制一个字典. 注意, 原字典中的键值如果是可变对象, 那么必须也是字典.
            ret = {}
            for key in src:
                if type(src[key]) == dict:
                    ret[key] = mydictcopy(src[key])
                else:
                    ret[key] = src[key]
            return ret
        damage = mydictcopy(damage_source)
        cof_shield = 1024 - getattr(targetattr, f'calc{damage["skilltype"]}Shield')
        cof_damage_coefficient = 1024 + getattr(targetattr, f'at{damage["skilltype"]}DamageCoefficient')
        cof_list = [cof_shield, cof_damage_coefficient]
        cof = 1
        for i in cof_list:
            cof *= i
        damage['base']['min'] = int(damage['base']['min'] * cof / (1024**len(cof_list)))
        damage['base']['max'] = int(damage['base']['max'] * cof / (1024**len(cof_list)))
        damage['critical']['min'] = int(damage['critical']['min'] * cof / (1024**len(cof_list)))
        damage['critical']['max'] = int(damage['critical']['max'] * cof / (1024**len(cof_list)))
        damage['except'] = int(((damage['base']['min'] + damage['base']['max']) / 2 * (10000 - damage['critical_except']) + (damage['critical']['min'] + damage['critical']['max']) / 2 * damage['critical_except']) / 10000)
        # damage['用晦而明'] = self.buff.is_exist(12575)

        item = {'tick': Event.tick, 'damage': damage}
        cls.damage_list.append(item)

        if cls.connect_queue is not None:
            message = {
                'category': 'damage',
                'data': {
                    'tick': Event.tick,
                    'except': damage['except'],
                }
            }
            # print(message)
            cls.connect_queue.put(message)

        if export_model:
            a = ('damagecalc_last', Event.tick, (selfattr.export_stat_change(), targetattr.export_stat_change()), damage_source['HashID'])
            cls.model_list.append(a)

        return damage

    @classmethod
    def damage_statistics(cls):
        '''伤害占比分析'''
        ret_dict = {}
        sum_damage = 0
        for item in cls.damage_list:
            sum_damage += item['damage']['except']
            if f"{item['damage']['SkillID']}_{item['damage']['Level']}" not in ret_dict:
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"] = {
                    'skill': item['damage']['skill'],
                    'name': item['damage']['name'],
                    'min': item['damage']['base']['min'],
                    'max': item['damage']['critical']['max'],
                    'critical_except': item['damage']['critical_except'],
                    'sum_damage': item['damage']['except'],
                    'count': 1,
                }
            else:
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['min'] = min(ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['min'], item['damage']['base']['min'])
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['max'] = max(ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['max'], item['damage']['critical']['max'])
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['critical_except'] += item['damage']['critical_except']
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['sum_damage'] += item['damage']['except']
                ret_dict[f"{item['damage']['SkillID']}_{item['damage']['Level']}"]['count'] += 1
        for key in ret_dict:
            ret_dict[key]['critical_except'] /= ret_dict[key]['count']
            ret_dict[key]['count_hit'] = int(ret_dict[key]['count'] * (10000 - ret_dict[key]['critical_except']) / 10000 + 0.5)
            ret_dict[key]['count_critical'] = int(ret_dict[key]['count'] * ret_dict[key]['critical_except'] / 10000 + 0.5)
            ret_dict[key]['proportion'] = ret_dict[key]['sum_damage'] / sum_damage
        return ret_dict

    @classmethod
    def export_model(cls):
        return cls.model_list
