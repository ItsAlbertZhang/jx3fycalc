# -*- coding: utf-8 -*-
from src.frame.damage import Damage
from src.frame.event import Event
from src.worker_attrbenefit.subattr import SubAttr
import hashlib
import json
import pickle


def fight(data: dict, selfattr: SubAttr, targetattr: SubAttr):
    cachename = hashlib.md5(json.dumps(data).encode('utf-8')).hexdigest()
    with open(f'data/cache/{cachename}', 'rb') as f:
        model_list = pickle.load(f)
    damage_source_dict = {}
    for i in model_list:
        t, Event.tick, attr_load_add_data, other = i
        selfattr_data, targetattr_data = attr_load_add_data
        selfattr.import_stat_change(selfattr_data)
        targetattr.import_stat_change(targetattr_data)
        if 'damagecalc_source' == t:
            SkillID, Level, skill, name, skilltype, kindtype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus, channel_interval_cof = other
            damage_source = Damage.damagecalc_source(selfattr, targetattr, SkillID, Level, skill, name, skilltype, kindtype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus, channel_interval_cof, False)
            damage_source_dict[damage_source['HashID']] = damage_source
        elif 'damagecalc_last' == t:
            damage_source = damage_source_dict[other]
            damage = Damage.damagecalc_last(selfattr, targetattr, damage_source, False)
