# -*- coding: utf-8 -*-
import json
from src.character.player import player
from src.frame.event import Event
from src.frame.damage import Damage


class MacroList():
    def __init__(self, data: dict) -> None:
        # with open('data/fight.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        self.normal_skill: dict = data['include']['normal_skill']
        self.special_skill: dict = data['include']['special_skill']
        self.ping: int = data['ping']
        self.skill_list = []
        for l in data['skill_list']:
            self.skill_list.extend(data['include']['lists'][l])
        self.index = 0
        self.normal_CD = 0

    def handle_skill(self):
        if self.normal_CD == 0:
            raise RuntimeError('Need to set normal CD before handle skill.')
        name = self.skill_list[self.index]
        if name in self.normal_skill:  # 常规技能 (占用 GCD)
            SkillID = self.normal_skill[name]
            # 检查 CD
            nextskill_cdlist = player.skills.get_cd_list(SkillID)
            cd_tick = player.cooldown.get_cd_tick(nextskill_cdlist)
            if cd_tick > Event.tick:  # 如果技能尚未冷却完毕, 则等技能冷却完毕再次施展
                Event.add(int(cd_tick - Event.tick + max(1, self.ping/1000*1024)), self.handle_skill)
                # 直接退出, index 不自增
            else:
                player.cast_skill(SkillID)
                if not player.cooldown.is_in_cd(self.normal_CD):
                    # for i in Damage.damage_list:
                    #     print(i)
                    # print('程序运行已中断, 已打印截至目前的伤害列表. DPS为:', Damage.dps)
                    # print(f'此技能此时无法释放. 此时的时间是:{Event.tick}, 技能是:{name}.')
                    raise RuntimeError(f'This skill ({name}) cannot be cast at this time ({Event.tick}).')
                self.index += 1  # 执行完毕, index 自增 1
        else:  # 非常规技能 (不占用 GCD) 或是执行特殊动作
            if name in self.special_skill and self.special_skill[name] > 0:  # 是不占用 GCD 且已知 SkillID 的技能, 释放即可
                player.cast_skill(self.special_skill[name])
                self.index += 1
                self.handle_skill()  # 未进入 GCD, 递归继续处理
            elif hasattr(self, f'handle_{name}'):  # 是未知技能 (特殊动作), 在 self 中寻找对应方法进行处理
                func = getattr(self, f'handle_{name}')
                func()
                self.index += 1
                self.handle_skill()  # 未进入 GCD, 递归继续处理
            else:  # 不是已知的技能, 且未在 self 中找到对应该特殊动作的方法, 抛出异常. 后续考虑实现自定义命令的 feature, coding...
                raise RuntimeError(f'Unsupported commands {name}. This feature is still under development.')


'''
    以下的类被作为本 module 的 attr 在 src.worker_calc.method 中被 getattr 读取.
    读取时的依据为 data/player.json 中的 data['KungFuSkill']['name'].
'''


class MacroList_焚影圣诀(MacroList):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.normal_CD = 503

        ping = self.ping
        handle_skill = self.handle_skill

        def cooldown_over(self, ID):
            self.table.pop(ID)
            if 503 == ID:
                Event.add(int(ping/1000*1024), handle_skill)
            if 8 == ID:
                player.cast_skill(4326)

        player.cooldown.over = cooldown_over.__get__(player.cooldown)

    def handle_开特效腰坠(self):
        if player.skills.is_exist(6800):
            player.cast_skill(6800)

    def handle_点掉日月齐光(self):
        player.buff.delete(25721, all=True)

    def handle_点掉魂·月(self):
        player.buff.delete(9911, 2, all=True)

    def handle_点掉日月灵魂(self):
        player.buff.delete(25765, all=True)

    def calc(self):
        # 起手状态设定
        player.attr.atCurrentSunEnergy = 10000
        player.attr.atCurrentMoonEnergy = 10000
        player.attr.atMoonPowerValue = 1
        # player.AddBuff(player, 12850, 2, stack_num=3)
        # 进入战斗
        self.handle_skill()  # 开技能
        player.cast_skill(4326)  # 开大漠刀法
        while len(Event.tick_list) > 0 and self.index < len(self.skill_list):
            Event.handle()
