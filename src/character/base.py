# -*- coding: utf-8 -*-
from src.frame.attribute import Attribute
from src.frame.buff import Buff
from src.frame.skills import Skill, SkillEffectList, SkillCastQueue
from src.frame.recipeskill import RecipeSkill
from src.frame.skillevent import SkillEvent, RandomEvent
from src.frame.cooldown import CoolDown
import json


class Character():
    def __init__(self) -> None:
        self.attr = Attribute()
        self.buff = Buff()
        self.skills = Skill()
        self.skill_effect_l = SkillEffectList()
        self.skill_cast_q = SkillCastQueue()
        self.recipe_skill = RecipeSkill()
        self.skill_event = SkillEvent()
        self.random_event = RandomEvent()
        self.cooldown = CoolDown()
        self.is_in_fight = False

    def load_character(self, data: dict):
        '''
            导入角色数据.
        '''
        try:
            self.attr.load_from_json(data['attr'])
        except:
            raise RuntimeError
