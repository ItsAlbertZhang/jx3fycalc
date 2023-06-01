# -*- coding: utf-8 -*-
from src.character.player import player
from src.character.target import target
from src.frame.damage import Damage
from src.frame.fetchdata import TabAttr
import src.worker_calc.method.macro as macro
import hashlib
import json
import pickle


def custom_fight(data: dict):
    if '特效腰坠' in data['options'] and data['options']['特效腰坠']:
        player.skills.learn(6800, 101)  # 特效腰坠-笛泣
    if '套装-技能伤害' in data['options'] and data['options']['套装-技能伤害']:
        player.recipe_skill.add(948, 2)  # pve 套装效果-伤害秘籍
    if '套装-触发特效' in data['random_events'] and data['random_events']['套装-触发特效']:
        player.random_event.push(player.skill_event.add, 1922)  # pve 套装效果-触发效果
    if '腰带大附魔' in data['random_events'] and data['random_events']['腰带大附魔']:
        player.random_event.push(player.skill_event.add, 1705)  # 腰带大附魔
    if '鞋子大附魔' in data['random_events'] and data['random_events']['鞋子大附魔']:
        player.random_event.push(player.skill_event.add, 2393)  # 鞋子大附魔
    if '护腕大附魔' in data['random_events'] and data['random_events']['护腕大附魔']:
        player.random_event.push(player.skill_event.add, 1843)  # 护腕大附魔
    if data['random_event_work']:
        player.random_event.apply()


def fight(data: dict):
    custom_fight(data)
    with open('data/player.json', 'r', encoding='utf-8') as f:
        playerdata = json.load(f)
        kungfu_name = playerdata['KungFuSkill']['name']
    c = getattr(macro, f'MacroList_{kungfu_name}')
    macro_list = c(data)
    macro_list.calc()
    TabAttr.save_data()
    cachename = hashlib.md5(json.dumps(data).encode('utf-8')).hexdigest()
    with open(f'data/cache/{cachename}', 'wb') as f:
        pickle.dump(Damage.export_model(), f)
