# -*- coding: utf-8 -*-
from src.character.player import player
from src.character.target import target
from src.scripts.base import ScriptBase
from src.frame.event import Event


class 明教_烈日斩():
    tSkillData = [
        {'nDamageBase': 125 * 0.95, 'nDamageRand': 67 * 0.1, 'nCostMana': 0},  # level 1
        {'nDamageBase': 145 * 0.95, 'nDamageRand': 80 * 0.1, 'nCostMana': 0},  # level 2
        {'nDamageBase': 165 * 0.95, 'nDamageRand': 94 * 0.1, 'nCostMana': 0},  # level 3
        {'nDamageBase': 185 * 0.95, 'nDamageRand': 107 * 0.1, 'nCostMana': 0},  # level 4
        {'nDamageBase': 205 * 0.95, 'nDamageRand': 121 * 0.1, 'nCostMana': 0},  # level 5
        {'nDamageBase': 225 * 0.95, 'nDamageRand': 134 * 0.1, 'nCostMana': 0},  # level 6
        {'nDamageBase': 245 * 0.95, 'nDamageRand': 148 * 0.1, 'nCostMana': 0},  # level 7
        {'nDamageBase': 265 * 0.95, 'nDamageRand': 161 * 0.1, 'nCostMana': 0},  # level 8
        {'nDamageBase': 285 * 0.95, 'nDamageRand': 175 * 0.1, 'nCostMana': 0},  # level 9
        {'nDamageBase': 305 * 0.95, 'nDamageRand': 188 * 0.1, 'nCostMana': 0},  # level 10
        {'nDamageBase': 325 * 0.95, 'nDamageRand': 202 * 0.1, 'nCostMana': 0},  # level 1
        {'nDamageBase': 345 * 0.95, 'nDamageRand': 215 * 0.1, 'nCostMana': 0},  # level 2
        {'nDamageBase': 365 * 0.95, 'nDamageRand': 229 * 0.1, 'nCostMana': 0},  # level 3
        {'nDamageBase': 375 * 0.95, 'nDamageRand': 242 * 0.1, 'nCostMana': 0},  # level 4
        {'nDamageBase': 385 * 0.95, 'nDamageRand': 256 * 0.1, 'nCostMana': 0},  # level 5
        {'nDamageBase': 395 * 0.95, 'nDamageRand': 269 * 0.1, 'nCostMana': 0},  # level 6
        {'nDamageBase': 405 * 0.95, 'nDamageRand': 283 * 0.1, 'nCostMana': 0},  # level 7
        {'nDamageBase': 415 * 0.95, 'nDamageRand': 296 * 0.1, 'nCostMana': 0},  # level 8
        {'nDamageBase': 425 * 0.95, 'nDamageRand': 310 * 0.1, 'nCostMana': 0},  # level 9
        {'nDamageBase': 430 * 0.95, 'nDamageRand': 323 * 0.1, 'nCostMana': 0},  # level 10
        {'nDamageBase': 435 * 0.95, 'nDamageRand': 337 * 0.1, 'nCostMana': 0},  # level 1
        {'nDamageBase': 440 * 0.95, 'nDamageRand': 350 * 0.1, 'nCostMana': 0},  # level 2
        {'nDamageBase': 445 * 0.95, 'nDamageRand': 364 * 0.1, 'nCostMana': 0},  # level 3
        {'nDamageBase': 450 * 0.95, 'nDamageRand': 377 * 0.1, 'nCostMana': 0},  # level 4
        {'nDamageBase': 455 * 0.95, 'nDamageRand': 391 * 0.1, 'nCostMana': 0},  # level 5
        {'nDamageBase': 460 * 0.95, 'nDamageRand': 404 * 0.1, 'nCostMana': 0},  # level 6
        {'nDamageBase': 465 * 0.95, 'nDamageRand': 418 * 0.1, 'nCostMana': 0},  # level 7
        {'nDamageBase': 470 * 0.95, 'nDamageRand': 431 * 0.1, 'nCostMana': 0},  # level 8
        {'nDamageBase': 475 * 0.95, 'nDamageRand': 445 * 0.1, 'nCostMana': 0},  # level 9
        {'nDamageBase': 480 * 0.95, 'nDamageRand': 458 * 0.1, 'nCostMana': 0},  # level 10
        {'nDamageBase': 485 * 0.95, 'nDamageRand': 472 * 0.1, 'nCostMana': 0},  # level 9
        {'nDamageBase': 490 * 0.95, 'nDamageRand': 485 * 0.1, 'nCostMana': 0},  # level 10
    ]

    @classmethod
    def cast(cls, skill, *args, **kwargs):
        ret = None
        dwSkillLevel = skill['Level']

        if player.buff.is_exist(6279):
            return

        # cd_list = []
        # cd_list.append([508, 1])  # 技能普通CD
        # cd_list.append([503])  # 明教公共CD 1秒
        # if not ScriptBase.set_cd(skill, cd_list, kwargs=kwargs):
        #     return ret
        ScriptBase.set_cd(skill, 508, 1)
        ScriptBase.set_cd(skill, 503)
        if not ScriptBase.cast_cd(skill, kwargs):
            return

        player.AddBuff(target, 4418, 1)

        if dwSkillLevel < 10:
            cls.nChannelInterval = 64 * 1.1*1.1*1.05 * 1.05
        elif dwSkillLevel < 32:
            cls.nChannelInterval = (64 + (dwSkillLevel - 9) * 3) * 1.1*1.1*1.05 * 1.05
        else:
            cls.nChannelInterval = 141 * 1.1*1.1*1.05 * 1.05

        # ---魔法属性---
        cls.nDamageBase = cls.tSkillData[dwSkillLevel - 1]['nDamageBase'] / 3
        cls.nDamageRand = cls.tSkillData[dwSkillLevel - 1]['nDamageRand'] / 3
        ret = [ScriptBase.call_damage(cls, skill, 'Solar')]  # call damage
        player.attr.atCurrentSunEnergy += 4000
        player.cast_skill(19055, 2)  # 武器伤害

        ScriptBase.apply("skill/明教/明教通用删buff.lua", 0)
        cls.apply()
        ScriptBase.apply("skill/明教/镇派/日月豆结算.lua", 0)

        player.cast_skill(34396, 1)  # 日月同辉
        player.cast_skill(26708, 1)  # 净体不畏

        return ret

    @classmethod
    def apply(cls, *args, **kwargs):

        lv = player.skills.get_level(3963)
        if player.skills.get_level(18279) == 1:
            # --处理无武器伤害Bug
            player.CastSkill(19055, 2)

            player.AddBuff(target, 12312, 1)
            player.CastSkill(18280, lv)

        # --洞若观火
        if player.skills.get_level(5978) == 1:
            # --target.AddBuff(dwSkillSrcID, player.nLevel, 6288, 1, 1)
            if not player.buff.is_exist(6358, 1):
                player.AddBuff(player, 6356, 1)
                player.AddBuff(player, 6358, 1)

        # --破招
        if target.buff.is_exist(4202):
            player.CastSkill(32816, 2)

        if player.skills.get_level(25166) == 1:  # 净体不畏减cd
            player.cooldown.modify(505, -16 * 1 * 1024 / 16)
            player.cooldown.modify(508, -16 * 1 * 1024 / 16)

        # --影子
        Event.add(int(8 * 1024 / 16), cls.timer)

    @classmethod
    def timer(cls):
        if player.skills.get_level(34347) == 1:  # 影子
            if player.buff.is_exist(25716, 1):  # 日影
                player.CastSkill(34356, 1)
                player.buff.delete(25716, 1)
                # player.PlayPublicShadowAnimation(1, 85575, false, true)
            elif player.buff.is_exist(25716, 2):  # 月影
                player.CastSkill(34355, 1)
                player.buff.delete(25716, 2)
                # player.PlayPublicShadowAnimation(1, 85576, false, true)
