# -*- coding: utf-8 -*-
from src.character.base import Character
from src.character.target import target
from src.frame.damage import Damage
from src.frame.talent import Talent
from src.frame.ui import SkillUI, BuffUI
import pandas as pd
from src.frame.script import Script
import random
import json


class Player(Character):
    def __init__(self) -> None:
        super().__init__()
        self.attr.is_npc = False
        target.attr.DamageSource = self.attr
        self.queue_unlock = True

    def init_calc(self):
        '''这一方法依赖于 scripts 模块, 必须在其被导入的情况下使用 (本项目中其导入位置在 src.worker_calc 中).'''
        with open('data/player.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.kungfu_name = data['KungFuSkill']['name']
            self.KungFuID = data['KungFuID']
            self.skills.learn(data['KungFuSkill']['SkillID'], data['KungFuSkill']['Level'])
            self.cast_skill(data['KungFuSkill']['SkillID'])
            for skill in data['skill']:
                self.skills.learn(skill['SkillID'], skill['Level'])

    def cast_skill(self, SkillID, Level=None, *args, **kwargs):
        '''
            通过这种方式施展, 技能会以队列的方式执行.
        '''
        self.skill_cast_q.enqueue(SkillID, Level, args, kwargs)
        if self.queue_unlock:
            self.queue_unlock = False
            while not self.skill_cast_q.empty:
                s_SkillID, s_Level, s_args, s_kwargs = self.skill_cast_q.dequeue()
                self.CastSkill(s_SkillID, s_Level, s_args, s_kwargs)
            self.queue_unlock = True

    def CastSkill(self, SkillID, Level=None, *args, **kwargs):
        '''
            通过这种方式施展, 技能会以栈的方式执行.
        '''
        # skill attr
        skillattr = self.skills.get_attr(SkillID)
        skilldict = self.skills.init_dict(SkillID, Level)
        if Level is not None:
            skilldict['Level'] = Level

        # 检查技能是否能施展 coding... 后续可以优化, 避免无法释放的技能重复判定
        # 检查技能CD
        for ID in skilldict['cd_list']:
            if not self.cooldown.check_notin_cd(ID):
                return
        # 检查战斗状态
        if skillattr['NeedOutOfFight'] == 1 and self.is_in_fight:
            return
        # # 检查目标类型
        # if skillattr['TargetTypePlayer'] == 0 and target.is_npc == False:
        #     return
        # if skillattr['TargetTypeNpc'] == 0 and target.is_npc == True:
        #     return

        # skill event
        se1 = self.skill_event.get_by_EventSkillID(SkillID)
        SkillEventMask1 = skillattr['SkillEventMask1'] if not pd.isna(skillattr['SkillEventMask1']) else 0
        SkillEventMask2 = skillattr['SkillEventMask2'] if not pd.isna(skillattr['SkillEventMask2']) else 0
        se2 = self.skill_event.get_by_EventMask(int(SkillEventMask1), int(SkillEventMask2))
        skillevent = pd.concat([se1, se2], axis=0).drop_duplicates()

        def temp_handle_skillevent(row: pd.Series):
            if random.randint(0, 1024-1) < row['Odds']:
                self.CastSkill(row['SkillID'], row['SkillLevel'])

        # skill event Precast
        for _, row in skillevent.iterrows():
            if 'PreCast' == row['EventType']:
                temp_handle_skillevent(row)

        # skill recipe CoolDownAdd
        skillrecipe = self.recipe_skill.get_by_SkillID(SkillID)
        if not pd.isna(skillattr['RecipeType']):
            sr = self.recipe_skill.get_by_SkillRecipeType(int(skillattr['RecipeType']))
            skillrecipe = pd.concat([skillrecipe, sr], axis=0).drop_duplicates()
        kwargs['CoolDownAdd1'] = 0
        kwargs['CoolDownAdd2'] = 0
        kwargs['CoolDownAdd3'] = 0
        for _, row in skillrecipe.iterrows():
            if not pd.isna(row['CoolDownAdd1']):  # 冷却时间秘籍1
                kwargs['CoolDownAdd1'] += int(row['CoolDownAdd1'])
            if not pd.isna(row['CoolDownAdd2']):  # 冷却时间秘籍2
                kwargs['CoolDownAdd2'] += int(row['CoolDownAdd2'])
            if not pd.isna(row['CoolDownAdd3']):  # 冷却时间秘籍3
                kwargs['CoolDownAdd3'] += int(row['CoolDownAdd3'])

        # cast
        ret_list = self.skills.cast(SkillID, Level, *args, **kwargs)

        # skill recipe DamageAddPercent and ScriptFile
        for _, row in skillrecipe.iterrows():
            if not pd.isna(row['DamageAddPercent']):  # 伤害提高秘籍
                self._skill_recipe_add_all_damage_add_percent(int(row['DamageAddPercent']))
                self.skill_effect_l.push(SkillID, Level, self._skill_recipe_add_all_damage_add_percent, -int(row['DamageAddPercent']))
            if not pd.isna(row['ScriptFile']):  # 执行脚本秘籍.
                Script.execute(row['ScriptFile'], skilldict)

        # damage calc
        if None != ret_list:
            for ret in ret_list:
                SkillID, Level, skilltype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus = ret
                kindtype = skillattr['KindType']
                if 'Magic' in kindtype:
                    kindtype = kindtype[:-5]
                damage = Damage.damagecalc_source(self.attr, target.attr, SkillID, Level, skillattr['SkillName'], SkillUI.get_name(SkillID, Level), skilltype, kindtype, nDamageBase, nDamageRand, nChannelInterval, nWeaponDamagePercent, surplus)
                damage = Damage.damagecalc_last(self.attr, target.attr, damage)
                # print(damage)
                # Damage.damage_event(damage)
                self.is_in_fight = True
                target.is_in_fight = True

        # skill event Cast, Hit and Critical
        iscritical = False
        if None != ret_list:
            iscritical = random.randint(0, 10000-1) < damage['critical_except']
        for _, row in skillevent.iterrows():
            if 'Cast' == row['EventType'] or 'Hit' == row['EventType']:
                temp_handle_skillevent(row)
            if 'CriticalStrike' == row['EventType'] and iscritical:
                temp_handle_skillevent(row)

        # after cast
        ret = self.skill_effect_l.pop(SkillID, Level)

    def _skill_recipe_add_all_damage_add_percent(self, value):
        self.attr.atAllDamageAddPercent += value

    def AddBuff(self, buff_target: Character, ID, Level, time_second=None, time_tick=None, stack_num=1):
        buff_dict = buff_target.buff.init_add(ID, Level, stack_num)
        # 加速处理
        buff_interval = buff_dict['buff_attr']['Interval']
        buff_interval = int(buff_interval * (1024 - self.attr.calcHaste) / 1024)
        buff_interval = max(buff_interval, int(buff_dict['buff_attr']['MinInterval']))
        buff_interval = min(buff_interval, int(buff_dict['buff_attr']['MaxInterval']))
        buff_dict['buff_interval'] = buff_interval
        if time_second is None and time_tick is None:
            tick = None
        elif time_second is not None and time_tick is None:
            tick = time_second * 1024
        elif time_tick is not None and time_second is None:
            tick = time_tick
        else:
            raise RuntimeError('time_second and time_tick arg cannot be used at the same time.', time_second, time_tick)
        buff_target.buff.add(buff_dict, tick)
        # if ret:  # buff 不存在, 需要进行属性处理
        self._handle_buff_attr(buff_target, buff_dict)

    def _handle_buff_attr(self, buff_target: Character, buff_dict):
        # 处理 ScriptFile
        if not pd.isna(buff_dict['buff_attr']['ScriptFile']):
            buff_target.buff.init_delete(buff_dict, Script.on_remove, str(buff_dict['buff_attr']['ScriptFile']), buff_dict)
        # 处理 buff BeginAttribute
        max_BeginAttribute_count = 15
        for i in range(max_BeginAttribute_count):
            BeginAttrib = buff_dict['buff_attr'][f'BeginAttrib{i + 1}']
            BeginValue = buff_dict['buff_attr'][f'BeginValue{i + 1}A']
            BeginValue2 = buff_dict['buff_attr'][f'BeginValue{i + 1}B']
            if not pd.isna(BeginAttrib):
                if 'atExecuteScript' == BeginAttrib:
                    Script.apply(BeginValue)
                    buff_target.buff.init_delete(buff_dict, Script.unapply, BeginValue)
                elif 'atSetTalentRecipe' == BeginAttrib:
                    buff_target.recipe_skill.add(int(BeginValue), int(BeginValue2))  # 秘籍
                    buff_target.buff.init_delete(buff_dict, buff_target.recipe_skill.forget, int(BeginValue))  # buff 消失时移除秘籍
                elif 'atSkillEventHandler' == BeginAttrib:
                    buff_target.skill_event.add(int(BeginValue))  # 触发事件
                    buff_target.buff.init_delete(buff_dict, buff_target.skill_event.forget, int(BeginValue))  # buff 消失时移除触发事件
                elif 'atHalt' == BeginAttrib:  # 眩晕
                    pass
                elif 'atBeTherapyCoefficient' == BeginAttrib:  # 减疗
                    pass
                elif 'atImmunity' == BeginAttrib:  # 免疫施法击退
                    pass
                elif 'atKnockedDownRate' == BeginAttrib:  # 被击倒概率
                    pass
                elif 'atKnockedOffRate' == BeginAttrib:  # 被击飞概率
                    pass
                elif 'atImmuneSkillMove' == BeginAttrib:  # 免疫僵直
                    pass
                elif 'atAddTransparencyValue' == BeginAttrib:  # 调整透明度
                    pass
                elif 'atSetSelectableType' == BeginAttrib:  # 不可被选取
                    pass
                elif 'atStealth' == BeginAttrib:  # 隐身
                    pass
                elif 'atMoveSpeedPercent' == BeginAttrib:  # 移速提高
                    pass
                elif 'atNoLimitChangeSkillIcon' == BeginAttrib:  # 更换技能图标
                    pass
                else:
                    try:
                        def temp_add(attr, BeginAttrib, BeginValue):
                            value = getattr(attr, BeginAttrib)
                            setattr(attr, BeginAttrib, value + BeginValue)
                        temp_add(buff_target.attr, BeginAttrib, int(BeginValue))
                        buff_target.buff.init_delete(buff_dict, temp_add, buff_target.attr, BeginAttrib, -int(BeginValue))  # buff 消失时移除属性
                    except:
                        raise RuntimeError('Add buff failed.', BeginAttrib, BeginValue)

        # 处理 buff ActiveAttribute
        max_ActiveAttribute_count = 2
        for i in range(max_ActiveAttribute_count):
            ActiveAttrib = buff_dict['buff_attr'][f'ActiveAttrib{i + 1}']
            ActiveValue = buff_dict['buff_attr'][f'ActiveValue{i + 1}A']
            if not pd.isna(ActiveAttrib):
                if 'atCall' in ActiveAttrib and 'Damage' in ActiveAttrib:
                    def atCallDamage(target: Character, buff_dict):
                        func = buff_dict['call_dot']
                        func(target, buff_dict['ID'], buff_dict['Level'])
                        # self.buff.init_active(buff_dict, func, buff_dict['ID'], buff_dict['Level'])
                    buff_target.buff.init_active(buff_dict, atCallDamage, buff_target, buff_dict)
                elif 'atExecuteScript' == ActiveAttrib:
                    buff_target.buff.init_active(buff_dict, Script.apply, ActiveValue)
                else:
                    raise RuntimeError('Add buff failed.', ActiveAttrib, ActiveValue)

        # 处理 buff EndTimeAttribute
        max_EndTimeAttribute_count = 2
        for i in range(max_EndTimeAttribute_count):
            EndTimeAttrib = buff_dict['buff_attr'][f'EndTimeAttrib{i + 1}']
            EndTimeValue = buff_dict['buff_attr'][f'EndTimeValue{i + 1}A']
            EndTimeValue2 = buff_dict['buff_attr'][f'EndTimeValue{i + 1}B']
            if not pd.isna(EndTimeAttrib):
                if 'atExecuteScript' == EndTimeAttrib:
                    def atEndTime(EndTimeValue):
                        Script.apply(EndTimeValue)
                    buff_target.buff.init_delete(buff_dict, atEndTime, EndTimeValue)
                elif 'atCallBuff' == EndTimeAttrib:
                    def atEndTime(EndTimeValue):
                        player.AddBuff(player, int(EndTimeValue), int(EndTimeValue2))
                    buff_target.buff.init_delete(buff_dict, atEndTime, EndTimeValue)
                else:
                    raise RuntimeError('Add buff failed.', EndTimeAttrib, EndTimeValue)

    def set_dot(self, target: Character, BuffID, BuffLevel, SkillID, SkillLevel, skilltype, nChannelInterval):

        # 伤害秘籍特殊处理 (DOT 无法享受秘籍的伤害加成) (暂时这样处理)
        # self.skill_effect_l.pop_by_func(SkillID, self.skill_recipe_add_all_damage_add_percent)
        # 调整秘籍的生效位置后, 秘籍不会在 cast 之前被调用, 而是在 cast 之后在计算伤害时被调用, 所以这里不再需要取消掉伤害秘籍. 相应的, 这里需要调用其他秘籍 (主要是脚本秘籍, 其中有双会)
        # skill recipe ScriptFile
        skillattr = self.skills.get_attr(SkillID)
        skilldict = self.skills.init_dict(SkillID, SkillLevel)
        skillrecipe = self.recipe_skill.get_by_SkillID(SkillID)
        if not pd.isna(skillattr['RecipeType']):
            sr = self.recipe_skill.get_by_SkillRecipeType(int(skillattr['RecipeType']))
            skillrecipe = pd.concat([skillrecipe, sr], axis=0).drop_duplicates()
        for _, row in skillrecipe.iterrows():
            if not pd.isna(row['ScriptFile']):  # 执行脚本秘籍.
                Script.execute(row['ScriptFile'], skilldict)
        # 调用栈的顺序是: self.CastSkill -> skills.cast -> self.set_dot, 所以本函数执行完毕退栈后, self.CastSkill 会立即将秘籍效果回收. 故本函数中无需考虑秘籍效果的回收问题.

        self.AddBuff(target, BuffID, BuffLevel)
        buff_dict = target.buff.get_dict(BuffID, BuffLevel)
        if len(buff_dict) == 0:
            raise RuntimeError('Set DOT failed.', BuffID, BuffLevel)
        buff_dict = buff_dict[0]
        buff_attr = buff_dict['buff_attr']
        nDamageBase = int(buff_attr['ActiveValue1A'])
        sum_count = int(buff_attr['Count'])
        sum_interval = int(buff_attr['Count']) * int(buff_attr['Interval'])
        channel_interval_cof = 1 / sum_count * max(16, int(sum_interval / 12)) / 16
        kindtype = buff_attr['ActiveAttrib1']  # atCall{kindtype}Damage
        kindtype = kindtype[:-6][6:]
        damage_source = Damage.damagecalc_source(self.attr, target.attr, SkillID, SkillLevel, skillattr['SkillName'], BuffUI.get_name(BuffID, BuffLevel), skilltype, kindtype, nDamageBase, 0, nChannelInterval, 0, channel_interval_cof=channel_interval_cof)
        buff_dict['damage_source'] = damage_source
        buff_dict['call_dot'] = self._call_dot

    def _call_dot(self, target: Character, ID, Level):
        buff_dict = target.buff.get_dict(ID, Level)
        if len(buff_dict) == 0:
            raise RuntimeError('Call DOT failed.', ID, Level)
        buff_dict = buff_dict[0]
        damage = Damage.damagecalc_last(self.attr, target.attr, buff_dict['damage_source'])
        # Damage.damage_event(damage)

    def set_talent(self, KungFuID, choice_list):
        talent_list = Talent.get_talent_list(KungFuID)
        if len(choice_list) != len(talent_list):
            raise RuntimeError('Talent choice list has an invalid length.')
        for i in range(len(choice_list)):
            SkillID = talent_list[i][choice_list[i] - 1]
            self.skills.learn(SkillID, 1)  # 奇穴技能固定为 1 级.
            self.cast_skill(SkillID)

    def load_character(self, data: dict):
        '''
            重写导入角色数据.
        '''
        super().load_character(data)
        try:
            if 'recipe_skill' in data:
                recipe_skill = data['recipe_skill']
                for skill in recipe_skill:
                    for RecipeID in skill:
                        self.recipe_skill.add(RecipeID)
            if 'talent_list' in data:
                talent_list = data['talent_list']
                self.set_talent(self.KungFuID, talent_list)
        except:
            raise RuntimeError


player = Player()
