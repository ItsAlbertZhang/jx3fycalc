# -*- coding: utf-8 -*-
from src.character.player import player
from src.frame.script import Script

'''
    脚本文件说明:
    cast 方法对应 lua 中的 GetSkillLevelData 函数.
    apply 方法对应 lua 中的 Apply 函数.

    由于实现逻辑不同, 在 cast 方法中需要对语句顺序做出调整:
    先执行检查. 注意, CD 的检查应当放在最后.
    然后设置属性, 如基础伤害, 浮动伤害, 技能系数等.
    最后执行魔法属性, 即 GetSkillLevelData 函数中最前面的 skill.AddAttribute() 方法.
'''


class ScriptBase():
    @classmethod
    def call_damage(cls, obj, skill, skilltype, surplus=False):
        nDamageBase = getattr(obj, 'nDamageBase', 0)
        nDamageRand = getattr(obj, 'nDamageRand', 0)
        nChannelInterval = getattr(obj, 'nChannelInterval', 0)
        nWeaponDamagePercent = getattr(obj, 'nWeaponDamagePercent', 0)
        return (skill['SkillID'], skill['Level'], skilltype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus)

    @classmethod
    def aftercast(cls, skill, func, *args, **kwargs):
        player.skill_effect_l.push(skill['SkillID'], skill['Level'], func, args, kwargs)

    @classmethod
    def set_cd(cls, skill, cd, index=0):
        skill_dict = player.skills.init_dict(skill['SkillID'], skill['Level'])
        # if skill_dict['cd_list'][index] != 0:
        #     raise RuntimeError('Skill CD in exist.')
        player.skills.set_cd(skill['SkillID'], cd, index)  # 设置 CD
        # if value not in skill_dict['cd_list']:

        #     player.cooldown.setcd(cd, haste=player.attr.calcHaste)  # 进入 CD
        #     if add > 0 and f'CoolDownAdd{add}' in kwargs:  # 调整 CD
        #         cd_add = kwargs[f'CoolDownAdd{add}']
        #         player.cooldown.modify(cd, cd_add * 1024 / 16)

    @classmethod
    def cast_cd(cls, skill, kwargs):
        skill_dict = player.skills.init_dict(skill['SkillID'], skill['Level'])
        cd_list = skill_dict['cd_list']
        for ID in cd_list:
            if player.cooldown.is_in_cd(ID):
                return False
        for i in range(len(cd_list)):
            if cd_list[i] > 0:
                Add = 0
                if f'CoolDownAdd{i}' in kwargs:
                    Add = int(kwargs[f'CoolDownAdd{i}'])
                player.cooldown.setcd(cd_list[i], Add=Add, haste=player.attr.calcHaste)
        return True

    @classmethod
    def apply(cls, path: str, *args, **kwargs):
        Script.apply(path, *args, **kwargs)
