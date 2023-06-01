# -*- coding: utf-8 -*-
import json
from typing import Any
from src.frame.global_param import GlobalParam


class Attribute():
    '''
        Attribute 类中有一些以固定字符串开头的特殊属性. 以下对这些特殊属性进行说明.

        ### 'kungfu', 'calc' 开头:
            - 'kungfu' 代表心法转换的额外属性.
            - 'calc' 代表最终属性.

            这几类属性的特点是在调用时需要实时计算, 并返回一个值 (我们希望在使用它们时, 逻辑与正常调用一个类实例的属性相同).
            这些属性的 setattr 方法应当传入一个 callable 对象 (通常是一个函数) 作为值, 并且这个 callable 对象应当需要一个参数并返回一个值. 进行 setattr 时, 这个 callable 对象会被存为当前实例对象 (即 self) 的方法, 名字为 f'method_{name}'.
            进行 getattr 操作会调用在 setattr 中传入的 callable 对象, 参数为当前实例对象 (即 self), 并将其返回的值进行返回. 如果这一属性并未进行过 setattr 操作, 那么会返回 0 (无论这一属性是否存在于类实例中).
            值得注意的是, setattr 并不拒绝传入 0 作为值 (尽管 0 并不是一个 callable 对象), 以方便对属性的初始化 (以使 IDE 进行补全提示).

            for example:
            ```python
                o = Attribute()
                o.calcAttackPowerBase = 0  # 并不会有实际效果, 仅仅为了 IDE 的补全提示.
                def calc_method(self):
                    return self.atAttackPowerBase * (1 + self.atAttackPowerPercent)
                o.calcAttackPowerBase = calc_method  # 进行 setattr
                print(o.calcAttackPowerBase)  # o.calcAttackPowerBase 的值是 o.atAttackPowerBase * (1 + o.atAttackPowerPercent)
            ```

        ### 'record', 'diff' 开头:

            这两个属性综合构成记录系统, 并配合 'last_stat' 属性与 'export_stat_change', 'import_stat_change' 方法使用.
            有时, 一些实战的属性会加成至 base 属性上 (例如水特效加成基础攻击, 特效腰坠加成基础破防等级). 如果完全按照游戏内的逻辑进行还原, 则无法将其与配装等来源的 base 属性区分, 也自然无法将其作为 stat 导出与导入. 因此, 采用一套特殊的逻辑进行实现.
            使用 'bool_record' 属性控制记录的开关. 平时该开关默认为关闭状态, 在进行配装或属性导入时, 该开关打开.
            在开关打开的情况下对 base 类属性进行 setattr 会在当前实例对象 (即 self) 中创建一个 f'record_{name}' 的属性副本.
            进行 'export_stat_change' 时, 在导出 base 属性时, 如果需要导出, 那么会计算属性与 record 属性的差值并导出. 这个差值的名字会以 'diff_' 开头, 并且像真实的属性一样被调用, 但其本质上只是语法糖, 不是真正的属性.
            进行 'import_stat_change' 时, 如果有差值属性存在, 那么会基于 recoed 属性进行计算并赋给 base 属性.
    '''

    # 在 __getattribute__ 方法和 __setattr__ 方法的内部, 如果使用 getattr() 和 setattr(), 一定要注意可能产生无穷递归的问题.
    # 为了降低代码出错的可能性, 建议每次直接使用 getattr 和 setattr (而不是使用 super().__getattribute__ 和 super().__setattr__) 时, 都在其后进行备注.

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith('kungfu') or __name.startswith('calc'):
            try:
                method = super().__getattribute__(f'method_{__name}')
                return method(self)
            except:
                return 0
        elif __name.startswith('record_'):
            try:
                return super().__getattribute__(__name)
            except:
                return 0
        elif __name.startswith('diff_'):
            diff = super().__getattribute__(__name[5:]) - getattr(self, f'record_{__name[5:]}')  # 小心! 这里直接使用了 getattr().
            return diff
        else:
            return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name.startswith('kungfu') or __name.startswith('calc'):
            if 0 == __value:  # 不拒绝 0, 以方便初始化
                return
            if not callable(__value):
                raise RuntimeError('"kungfu" or "calc" attr must be callable.')
            super().__setattr__(f'method_{__name}', __value)
        elif __name.startswith('diff_'):
            __value += getattr(self, f'record_{__name[5:]}')  # 小心! 这里直接使用了 getattr().
            super().__setattr__(__name[5:], __value)
        else:  # 详细逻辑请查看 self.bool_record 的注解
            if hasattr(self, 'bool_record') and self.bool_record and __name in self.__class__.base_list:
                super().__setattr__(f'record_{__name}', __value)
            super().__setattr__(__name, __value)

    def __init__(self) -> None:
        self.level = 120
        self.is_npc = True

        self.atBasePotentialAdd = 0  # 所有主属性
        self.atVitalityBase = 0  # 体质
        self.atStrengthBase = 0  # 力道
        self.atAgilityBase = 0  # 身法
        self.atSpiritBase = 0  # 根骨
        self.atSpunkBase = 0  # 元气
        self.atVitalityBasePercentAdd = 0  # 体质%
        self.atStrengthBasePercentAdd = 0  # 力道%
        self.atAgilityBasePercentAdd = 0  # 身法%
        self.atSpiritBasePercentAdd = 0  # 根骨%
        self.atSpunkBasePercentAdd = 0  # 元气%

        self.atPhysicsAttackPowerBase = 0  # 外功基础攻击
        self.atMagicAttackPowerBase = 0  # 内功基础攻击
        self.atSolarAttackPowerBase = 0  # 阳性内功基础攻击
        self.atLunarAttackPowerBase = 0  # 阴性内功基础攻击
        self.atNeutralAttackPowerBase = 0  # 混元内功基础攻击
        self.atPoisonAttackPowerBase = 0  # 毒性内功基础攻击
        self.atPhysicsAttackPowerPercent = 0  # 外功基础攻击提升1024分数
        self.atMagicAttackPowerPercent = 0  # 内功基础攻击提升1024分数
        self.atSolarAttackPowerPercent = 0  # 阳性内功基础攻击提升1024分数
        self.atLunarAttackPowerPercent = 0  # 阴性内功基础攻击提升1024分数
        self.atNeutralAttackPowerPercent = 0  # 混元内功基础攻击提升1024分数
        self.atPoisonAttackPowerPercent = 0  # 毒性内功基础攻击提升1024分数
        self.atTherapyPowerBase = 0  # 治疗量
        self.atTherapyPowerPercent = 0  # 治疗量%

        self.atAllTypeCriticalStrike = 0  # 全会心等级
        self.atPhysicsCriticalStrike = 0  # 外功会心等级
        self.atMagicCriticalStrike = 0  # 内功会心等级
        self.atSolarCriticalStrike = 0  # 阳性内功会心等级
        self.atLunarCriticalStrike = 0  # 阴性内功会心等级
        self.atNeutralCriticalStrike = 0  # 混元内功会心等级
        self.atPoisonCriticalStrike = 0  # 毒性内功会心等级
        self.atPhysicsCriticalStrikeBaseRate = 0  # 外功额外会心万分数
        self.atSolarCriticalStrikeBaseRate = 0  # 阳性内功额外会心万分数
        self.atLunarCriticalStrikeBaseRate = 0  # 阴性内功额外会心万分数
        self.atNeutralCriticalStrikeBaseRate = 0  # 混元内功额外会心万分数
        self.atPoisonCriticalStrikeBaseRate = 0  # 毒性内功额外会心万分数

        self.atAllTypeCriticalDamagePowerBase = 0  # 全会心效果等级
        self.atPhysicsCriticalDamagePowerBase = 0  # 外功会心效果等级
        self.atMagicCriticalDamagePowerBase = 0  # 内功会心效果等级
        self.atPhysicsCriticalDamagePowerBaseKiloNumRate = 0  # 外功额外会心效果1024分数
        self.atMagicCriticalDamagePowerBaseKiloNumRate = 0  # 内功额外会心效果1024分数
        self.atSolarCriticalDamagePowerBaseKiloNumRate = 0  # 阳性内功额外会心效果1024分数
        self.atLunarCriticalDamagePowerBaseKiloNumRate = 0  # 阴性内功额外会心效果1024分数
        self.atNeutralCriticalDamagePowerBaseKiloNumRate = 0  # 混元内功额外会心效果1024分数
        self.atPoisonCriticalDamagePowerBaseKiloNumRate = 0  # 毒性内功额外会心效果1024分数

        self.atPhysicsOvercomeBase = 0  # 外功基础破防等级
        self.atMagicOvercome = 0  # 内功基础破防等级
        self.atSolarOvercomeBase = 0  # 阳性内功破防等级
        self.atLunarOvercomeBase = 0  # 阴性内功破防等级
        self.atNeutralOvercomeBase = 0  # 混元内功破防等级
        self.atPoisonOvercomeBase = 0  # 毒性内功破防等级
        self.atPhysicsOvercomePercent = 0  # 外功基础破防等级提升1024分数
        self.atSolarOvercomePercent = 0  # 阳性内功基础破防等级提升1024分数
        self.atLunarOvercomePercent = 0  # 阴性内功基础破防等级提升1024分数
        self.atNeutralOvercomePercent = 0  # 混元内功基础破防等级提升1024分数
        self.atPoisonOvercomePercent = 0  # 毒性内功基础破防等级提升1024分数

        self.atSurplusValueBase = 0  # 破招值
        self.atStrainBase = 0  # 无双等级
        self.atStrainRate = 0  # 无双等级提升1024分数
        self.atStrainPercent = 0  # 额外无双1024分数

        self.atHasteBase = 0  # 基础加速等级
        self.atHasteBasePercentAdd = 0  # 额外加速1024分数
        self.atUnlimitHasteBasePercentAdd = 0  # 突破上限加速1024分数

        self.atMaxLifeBase = 0  # 最大气血值
        self.atMaxLifePercentAdd = 0  # 最大气血值%
        self.atMaxLifeAdditional = 0  # 额外气血值
        self.atFinalMaxLifeAddPercent = 0  # 最终气血值%

        self.atPhysicsShieldBase = 0  # 外功基础防御等级
        self.atPhysicsShieldPercent = 0  # 外功基础防御等级提升1024分数
        self.atPhysicsShieldAdditional = 0  # 额外外功防御等级
        self.atMagicShield = 0  # 内功基础防御等级
        self.atSolarMagicShieldBase = 0  # 阳性内功防御等级
        self.atLunarMagicShieldBase = 0  # 阴性内功防御等级
        self.atNeutralMagicShieldBase = 0  # 混元内功防御等级
        self.atPoisonMagicShieldBase = 0  # 毒性内功防御等级
        self.atSolarMagicShieldPercent = 0  # 阳性内功基础防御提升1024分数
        self.atLunarMagicShieldPercent = 0  # 阴性内功基础防御提升1024分数
        self.atNeutralMagicShieldPercent = 0  # 混元内功基础防御提升1024分数
        self.atPoisonMagicShieldPercent = 0  # 毒性内功基础防御提升1024分数

        self.atDodge = 0  # 闪避等级
        self.atDodgeBaseRate = 0  # 闪避%
        self.atParryBase = 0  # 招架等级
        self.atParryPercent = 0  # 招架等级%
        self.atParryBaseRate = 0  # 招架%
        self.atParryValueBase = 0  # 拆招值
        self.atParryValuePercent = 0  # 拆招值%

        self.atGlobalResistPercent = 0  # 通用减伤
        self.atPhysicsResistPercent = 0  # 外功通用减伤%
        self.atSolarMagicResistPercent = 0  # 阳性内功通用减伤%
        self.atLunarMagicResistPercent = 0  # 阴性内功通用减伤%
        self.atNeutralMagicResistPercent = 0  # 混元内功通用减伤%
        self.atPoisonMagicResistPercent = 0  # 毒性内功通用减伤%

        self.atPhysicsDamageCoefficient = 0  # 物理易伤1024分数
        self.atSolarDamageCoefficient = 0  # 阳性内功易伤1024分数
        self.atLunarDamageCoefficient = 0  # 阴性内功易伤1024分数
        self.atNeutralDamageCoefficient = 0  # 混元内功易伤1024分数
        self.atPoisonDamageCoefficient = 0  # 毒性内功易伤1024分数

        self.atToughnessBase = 0  # 御劲等级
        self.atToughnessPercent = 0  # 御劲等级%
        self.atToughnessBaseRate = 0  # 御劲%

        self.atDecriticalDamagePowerBase = 0  # 化劲等级
        self.atDecriticalDamagePowerPercent = 0  # 化劲等级%
        self.atDecriticalDamagePowerBaseKiloNumRate = 0  # 化劲%

        self.atMeleeWeaponDamageBase = 0  # 武器伤害
        self.atMeleeWeaponDamageRand = 0  # 武器伤害浮动

        self.atAllDamageAddPercent = 0  # 造成的全伤害和治疗效果提升1024分数
        self.atAllMagicDamageAddPercent = 0  # 造成的内功伤害和治疗效果提升1024分数
        self.atAddDamageByDstMoveState = 0  # 根据目标移动状态造成的伤害提升1024分数

        self.atAllShieldIgnorePercent = 0  # 无视防御1024分数
        self.atActiveThreatCoefficient = 0  # 仇恨提升1024分数
        self.atDstNpcDamageCoefficient = 0  # 非侠士伤害

        # def init_property(self: Attribute, name: str):
        #     '''
        #         通过这种方式初始化的属性, 其在被调用时与其他属性没有任何区别.

        #         但在被赋值时, 需要传入的不是属性的值, 而是一个函数. 函数应当计算并返回属性的值.

        #         这样处理是为了方便调用. 例如, 对于最终攻击力属性, 需要频繁被调用, 但其本身不应作为一个"属性"出现.

        #         因此, 可以定义一个函数, 在函数中对最终攻击力进行计算并返回. 然后将这个函数"赋值"给最终攻击力变量. 以下是示例代码实现:

        #         self.calcAttackPower = 0

        #         init_property(self, 'calcAttackPower')

        #         此时如果调用 self.calcAttackPower, 会得到 0. 下面定义一个函数用来计算最终攻击力.

        #         def calc_attack_power(self):
        #             return self.atAttackPowerBase + self.atAttackPowerAdd

        #         self.calcAttackPower = calc_attack_power
        #     '''

        #     def calc(self: Attribute):  # 实际计算函数. 注意, 由于需要将这个函数添加至类方法, 所以函数至少需要一个 self 参数.
        #         return 0
        #     setattr(self.__class__, f'method_{name}', calc)  # 将实际计算函数添加至类方法

        #     def getter(self: Attribute):  # getter 函数. 它返回实际计算函数的调用结果.
        #         method = getattr(self, f'method_{name}')
        #         return method()

        #     def setter(self: Attribute, newfunc):  # setter 函数. 使用它以更换实际计算函数.
        #         setattr(self.__class__, f'method_{name}', newfunc)
        #     setattr(self.__class__, name, property(getter, setter))  # 将其伪装为类的属性

        # 这些属性表示心法转换的额外属性. 这些属性官方没有, 我这里偷个懒, 就不去做全套的心法转换体系了. 属性名为 kungfu{属性名}Add, 其中 kungfu 代表心法, Add 表示是额外属性.
        # 先赋值为 0 再初始化可以尽量减少 code 错误. 建议遵循此代码逻辑, 理论上消耗不了多少性能.
        self.kungfuPhysicsAttackPowerAdd = 0  # 外功额外攻击
        self.kungfuSolarAttackPowerAdd = 0  # 阳性内功额外攻击
        self.kungfuLunarAttackPowerAdd = 0  # 阴性内功额外攻击
        self.kungfuNeutralAttackPowerAdd = 0  # 混元内功额外攻击
        self.kungfuPoisonAttackPowerAdd = 0  # 毒性内功额外攻击
        # init_property(self, 'kungfuPhysicsAttackPowerAdd')
        # init_property(self, 'kungfuSolarAttackPowerAdd')
        # init_property(self, 'kungfuLunarAttackPowerAdd')
        # init_property(self, 'kungfuNeutralAttackPowerAdd')
        # init_property(self, 'kungfuPoisonAttackPowerAdd')
        self.kungfuPhysicsCriticalStrikeAdd = 0  # 外功额外会心等级
        self.kungfuSolarCriticalStrikeAdd = 0  # 阳性内功额外会心等级
        self.kungfuLunarCriticalStrikeAdd = 0  # 阴性内功额外会心等级
        self.kungfuNeutralCriticalStrikeAdd = 0  # 混元内功额外会心等级
        self.kungfuPoisonCriticalStrikeAdd = 0  # 毒性内功额外会心等级
        # init_property(self, 'kungfuPhysicsCriticalStrikeAdd')
        # init_property(self, 'kungfuSolarCriticalStrikeAdd')
        # init_property(self, 'kungfuLunarCriticalStrikeAdd')
        # init_property(self, 'kungfuNeutralCriticalStrikeAdd')
        # init_property(self, 'kungfuPoisonCriticalStrikeAdd')
        self.kungfuPhysicsOvercomeAdd = 0  # 外功额外破防等级
        self.kungfuSolarOvercomeAdd = 0  # 阳性内功额外破防等级
        self.kungfuLunarOvercomeAdd = 0  # 阴性内功额外破防等级
        self.kungfuNeutralOvercomeAdd = 0  # 混元内功额外破防等级
        self.kungfuPoisonOvercomeAdd = 0  # 毒性内功额外破防等级
        # init_property(self, 'kungfuPhysicsOvercomeAdd')
        # init_property(self, 'kungfuSolarOvercomeAdd')
        # init_property(self, 'kungfuLunarOvercomeAdd')
        # init_property(self, 'kungfuNeutralOvercomeAdd')
        # init_property(self, 'kungfuPoisonOvercomeAdd')

        # 简单地设置一些最终属性的计算逻辑, 可以在其他地方更改.

        # self.calcPhysicsAttackPower = 0  # 外功最终攻击
        # self.calcSolarAttackPower = 0  # 阳性内功最终攻击
        # self.calcLunarAttackPower = 0  # 阴性内功最终攻击
        # self.calcNeutralAttackPower = 0  # 混元内功最终攻击
        # self.calcPoisonAttackPower = 0  # 毒性内功最终攻击
        # init_property(self, 'calcPhysicsAttackPower')
        # init_property(self, 'calcSolarAttackPower')
        # init_property(self, 'calcLunarAttackPower')
        # init_property(self, 'calcNeutralAttackPower')
        # init_property(self, 'calcPoisonAttackPower')

        def calc_AttackPower(name: str):  # 定义一个函数 calc_AttackPower, 该函数返回一个函数 func. 根据调用 calc_AttackPower 时传入的参数不同, 函数 func 的作用亦有区分, 目的是计算最终攻击.
            def func(self: Attribute):
                # 最终攻击的计算公式是: 基础攻击 + int(基础攻击 * 基础攻击提升1024分数 / 1024) + 额外攻击.
                # 基础攻击 = 对应属性的基础攻击. 如果是内功, 那么还需要再加上内功基础攻击.
                # 基础攻击提升1024分数 = 对应属性的基础攻击提升1024分数. 如果是内功, 那么还需要再加上内功基础攻击提升1024分数.
                # 额外攻击是指来自心法转换的额外攻击.
                AttackPowerBase = getattr(self, f'at{name}AttackPowerBase')
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    AttackPowerBase += self.atMagicAttackPowerBase
                AttackPowerPercent = getattr(self, f'at{name}AttackPowerPercent')
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    AttackPowerPercent += self.atMagicAttackPowerPercent
                return AttackPowerBase + int(AttackPowerBase * AttackPowerPercent / 1024) + getattr(self, f'kungfu{name}AttackPowerAdd')
            return func
        self.calcPhysicsAttackPower = calc_AttackPower('Physics')
        self.calcSolarAttackPower = calc_AttackPower('Solar')
        self.calcLunarAttackPower = calc_AttackPower('Lunar')
        self.calcNeutralAttackPower = calc_AttackPower('Neutral')
        self.calcPoisonAttackPower = calc_AttackPower('Poison')

        # self.calcPhysicsCriticalStrike = 0  # 外功最终会心
        # self.calcSolarCriticalStrike = 0  # 阳性内功最终会心
        # self.calcLunarCriticalStrike = 0  # 阴性内功最终会心
        # self.calcNeutralCriticalStrike = 0  # 混元内功最终会心
        # self.calcPoisonCriticalStrike = 0  # 毒性内功最终会心
        # init_property(self, 'calcPhysicsCriticalStrike')
        # init_property(self, 'calcSolarCriticalStrike')
        # init_property(self, 'calcLunarCriticalStrike')
        # init_property(self, 'calcNeutralCriticalStrike')
        # init_property(self, 'calcPoisonCriticalStrike')

        def calc_CriticalStrike(name: str):  # 目的是计算最终会心.
            def func(self: Attribute):
                # 最终会心的计算公式是: int((会心等级 + 额外会心等级) / 会心系数 * 10000) + 额外会心万分数.
                # 会心等级 = 对应属性的会心等级 + 全会心等级. 如果是内功, 那么还需要加上内功会心等级.
                # 额外会心等级是指来自心法转换的额外会心等级.
                # 注意, 计算得到的最终会心是一个万分数, 这符合游戏内的实际原理.
                CriticalStrikeBase = getattr(self, f'at{name}CriticalStrike') + self.atAllTypeCriticalStrike
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    CriticalStrikeBase += self.atMagicCriticalStrike
                return int((CriticalStrikeBase + getattr(self, f'kungfu{name}CriticalStrikeAdd')) / GlobalParam.CriticalStrikeCof(self.level) * 10000) + getattr(self, f'at{name}CriticalStrikeBaseRate')
            return func
        self.calcPhysicsCriticalStrike = calc_CriticalStrike('Physics')
        self.calcSolarCriticalStrike = calc_CriticalStrike('Solar')
        self.calcLunarCriticalStrike = calc_CriticalStrike('Lunar')
        self.calcNeutralCriticalStrike = calc_CriticalStrike('Neutral')
        self.calcPoisonCriticalStrike = calc_CriticalStrike('Poison')

        # self.calcPhysicsCriticalDamagePower = 0  # 外功最终会心效果
        # self.calcSolarCriticalDamagePower = 0  # 阳性内功最终会心效果
        # self.calcLunarCriticalDamagePower = 0  # 阴性内功最终会心效果
        # self.calcNeutralCriticalDamagePower = 0  # 混元内功最终会心效果
        # self.calcPoisonCriticalDamagePower = 0  # 毒性内功最终会心效果
        # init_property(self, 'calcPhysicsCriticalDamagePower')
        # init_property(self, 'calcSolarCriticalDamagePower')
        # init_property(self, 'calcLunarCriticalDamagePower')
        # init_property(self, 'calcNeutralCriticalDamagePower')
        # init_property(self, 'calcPoisonCriticalDamagePower')

        def calc_CriticalDamagePower(name: str):  # 目的是计算最终会心效果.
            def func(self: Attribute):
                # 最终会心效果的计算公式是: max(int(1.75 * 1024) + int(会心效果等级 * 1024 / 会心效果系数) + 额外会心效果1024分数, 3).
                # 会心效果等级 = 全会心效果等级 + 内功/外功会心效果等级.
                # 额外会心效果1024分数 = 对应属性的额外会心效果1024分数. 如果是内功, 那么还需要加上内功额外会心效果1024分数.
                # 注意, 计算得到的最终会心效果是一个1024分数, 且最大为 1280 (对应 300% 会心效果), 这符合游戏内的实际原理.
                CriticalDamagePowerBase = self.atAllTypeCriticalDamagePowerBase
                if 'Physics' == name:
                    CriticalDamagePowerBase += self.atPhysicsCriticalDamagePowerBase
                elif 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    CriticalDamagePowerBase += self.atMagicCriticalDamagePowerBase
                CriticalDamagePowerBaseKiloNumRate = getattr(self, f'at{name}CriticalDamagePowerBaseKiloNumRate')
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    CriticalDamagePowerBaseKiloNumRate += self.atMagicCriticalDamagePowerBaseKiloNumRate
                return min(int(CriticalDamagePowerBase * 1024 / GlobalParam.CriticalDamagePowerCof(self.level)) + CriticalDamagePowerBaseKiloNumRate, 1280)
            return func
        self.calcPhysicsCriticalDamagePower = calc_CriticalDamagePower('Physics')
        self.calcSolarCriticalDamagePower = calc_CriticalDamagePower('Solar')
        self.calcLunarCriticalDamagePower = calc_CriticalDamagePower('Lunar')
        self.calcNeutralCriticalDamagePower = calc_CriticalDamagePower('Neutral')
        self.calcPoisonCriticalDamagePower = calc_CriticalDamagePower('Poison')

        # self.calcPhysicsOvercome = 0  # 外功最终破防
        # self.calcSolarOvercome = 0  # 阳性内功最终破防
        # self.calcLunarOvercome = 0  # 阴性内功最终破防
        # self.calcNeutralOvercome = 0  # 混元内功最终破防
        # self.calcPoisonOvercome = 0  # 毒性内功最终破防
        # init_property(self, 'calcPhysicsOvercome')
        # init_property(self, 'calcSolarOvercome')
        # init_property(self, 'calcLunarOvercome')
        # init_property(self, 'calcNeutralOvercome')
        # init_property(self, 'calcPoisonOvercome')

        def calc_Overcome(name: str):  # 目的是计算最终破防.
            def func(self: Attribute):
                # 最终破防的计算公式是: int((基础破防等级 + int(基础破防等级 * 基础破防等级提升1024分数 / 1024) + 额外破防等级) * 1024 / 破防系数).
                # 基础破防等级 = 对应属性的基础破防等级. 如果是内功, 那么还需要加上内功基础破防等级.
                # 额外破防等级是指来自心法转换的额外破防等级.
                # 注意, 计算得到的最终破防是一个 1024 分数, 这符合游戏内的实际原理.
                OvercomeBase = getattr(self, f'at{name}OvercomeBase')
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    OvercomeBase += self.atMagicOvercome
                return int((OvercomeBase + int(OvercomeBase * getattr(self, f'at{name}OvercomePercent') / 1024) + getattr(self, f'kungfu{name}OvercomeAdd')) * 1024 / GlobalParam.OvercomeCof(self.level))
            return func
        self.calcPhysicsOvercome = calc_Overcome('Physics')
        self.calcSolarOvercome = calc_Overcome('Solar')
        self.calcLunarOvercome = calc_Overcome('Lunar')
        self.calcNeutralOvercome = calc_Overcome('Neutral')
        self.calcPoisonOvercome = calc_Overcome('Poison')

        # 计算防御属性需要先初始化伤害来源
        self.DamageSource = None
        # self.calcPhysicsShield = 0  # 外功最终防御
        # self.calcSolarShield = 0  # 阳性内功最终防御
        # self.calcLunarShield = 0  # 阴性内功最终防御
        # self.calcNeutralShield = 0  # 混元内功最终防御
        # self.calcPoisonShield = 0  # 毒性内功最终防御
        # init_property(self, 'calcPhysicsShield')
        # init_property(self, 'calcSolarShield')
        # init_property(self, 'calcLunarShield')
        # init_property(self, 'calcNeutralShield')
        # init_property(self, 'calcPoisonShield')

        def calc_Shield(name: str):  # 目的是计算最终防御
            def func(self: Attribute):
                # 最终防御的计算公式是: int(最终防御等级 * 1024 / (最终防御等级 + 防御系数))
                # 最终防御等级 = int(int(基础防御等级 + 基础防御等级 * 基础防御等级提升1024分数 + 额外防御等级) * (1024 - 无视防御1024分数) / 1024)
                # 基础防御等级 = 对应属性的基础防御等级. 如果是内功, 那么还需要加上内功基础防御等级.
                # 只有外功才有额外防御等级.
                # 注意, 计算得到的最终防御是一个 1024 分数, 且最大为 768, 这符合游戏内的实际原理.
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    realname = name + 'Magic'
                else:
                    realname = name
                ShieldBase = getattr(self, f'at{realname}ShieldBase')
                ShieldAdditional = 0
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    ShieldBase += self.atMagicShield
                if 'Physics' == name:
                    ShieldAdditional = self.atPhysicsShieldAdditional
                Shield = int(int(ShieldBase + ShieldBase * getattr(self, f'at{realname}ShieldPercent') + ShieldAdditional) * (1024 - (0 if self.DamageSource is None else self.DamageSource.atAllShieldIgnorePercent)) / 1024)
                return min(int(Shield * 1024 / (Shield + (GlobalParam.PhysicsShieldCof(self.level) if 'Physics' == name else GlobalParam.MagicShieldCof(self.level)))), 768)
            return func
        self.calcPhysicsShield = calc_Shield('Physics')
        self.calcSolarShield = calc_Shield('Solar')
        self.calcLunarShield = calc_Shield('Lunar')
        self.calcNeutralShield = calc_Shield('Neutral')
        self.calcPoisonShield = calc_Shield('Poison')

        # self.calcStrain = 0
        # init_property(self, 'calcStrain')

        def calc_Strain(self: Attribute):
            # 最终无双的计算公式是: int((基础无双等级 + int(基础无双等级 * 基础无双等级提升1024分数 / 1024)) * 1024 / 无双系数 + 额外无双1024分数).
            # 注意, 计算得到的最终无双是一个 1024 分数, 这符合游戏内的实际原理.
            return int((self.atStrainBase + int(self.atStrainBase * self.atStrainPercent / 1024)) * 1024 / GlobalParam.StrainCof(self.level) + self.atStrainRate)
        self.calcStrain = calc_Strain

        # self.calcHaste = 0
        # init_property(self, 'calcHaste')

        def calc_Haste(self: Attribute):
            # 最终加速的计算公式是: min(int(基础加速等级 * 1024 / 加速系数) + 额外加速1024分数, 256) + 突破上限加速1024分数
            return min(int(self.atHasteBase * 1024 / GlobalParam.HasteCof(self.level)) + self.atHasteBasePercentAdd, 256) + self.atUnlimitHasteBasePercentAdd
        self.calcHaste = calc_Haste

        # self.calcPhysicsDamageAddPercent = 0  # 外功最终伤害和治疗效果提升1024分数
        # self.calcSolarDamageAddPercent = 0  # 阳性内功最终伤害和治疗效果提升1024分数
        # self.calcLunarDamageAddPercent = 0  # 阴性内功最终伤害和治疗效果提升1024分数
        # self.calcNeutralDamageAddPercent = 0  # 混元内功最终伤害和治疗效果提升1024分数
        # self.calcPoisonDamageAddPercent = 0  # 毒性内功最终伤害和治疗效果提升1024分数
        # init_property(self, 'calcPhysicsDamageAddPercent')
        # init_property(self, 'calcSolarDamageAddPercent')
        # init_property(self, 'calcLunarDamageAddPercent')
        # init_property(self, 'calcNeutralDamageAddPercent')
        # init_property(self, 'calcPoisonDamageAddPercent')

        def calc_DamageAddPercent(name: str):  # 目的是计算最终伤害和治疗效果提升
            def func(self: Attribute):
                # 最终伤害和治疗效果提升1024分数的计算公式是: 造成的全伤害和治疗效果提升1024分数. 如果是内功, 那么还需要加上内功伤害和治疗效果提升1024分数.
                # 注意, 计算得到的最终伤害和治疗效果提升是一个 1024 分数, 这符合游戏内的实际原理.
                DamageAddPercentBase = self.atAllDamageAddPercent
                if 'Solar' == name or 'Lunar' == name or 'Neutral' == name or 'Poison' == name:
                    DamageAddPercentBase += self.atAllMagicDamageAddPercent
                return DamageAddPercentBase
            return func
        self.calcPhysicsDamageAddPercent = calc_DamageAddPercent('Physics')
        self.calcSolarDamageAddPercent = calc_DamageAddPercent('Solar')
        self.calcLunarDamageAddPercent = calc_DamageAddPercent('Lunar')
        self.calcNeutralDamageAddPercent = calc_DamageAddPercent('Neutral')
        self.calcPoisonDamageAddPercent = calc_DamageAddPercent('Poison')

        self.bool_kungfu_init_over = False
        self.bool_record = False
        '''
            bool_record: 是否记录属性. 这一变量的设置是为了实现模型功能.

            对于额外属性, 模型会记录原始值, 直接记录即可.

            但对于基础属性, 模型会记录其与配装属性的差值. 因此, 如果需要变更配装属性 (或使变更长久生效), 例如导入配装属性, 添加属性以计算属性收益, 设置长久生效的个人增益和团队增益时, 需要对本变量执行操作.

            具体做法是: 在设置这些长久生效的个人增益和团队增益之前, 先将本变量设置为 True, 然后再设置这些长久生效的个人增益和团队增益, 最后再将本变量设置为 False.
        '''
        self.last_stat = {}

    def load_from_json(self, data):
        '''
            导入属性.
            注意, 由于心法影响, 属性可能出现错误. 应当先初始化心法 (无论是以何种方式) 再导入属性.
        '''
        try:
            if type(data) == str:
                data: dict = json.loads(data)

            def get_value_by_key_string(data: dict, key: str) -> int:
                try:
                    return data[key]
                except:
                    return 0

            def get_value_by_key_substring(data: dict, key_sub_string: str, key_exclude_string='none') -> int:
                for key in data:
                    if key_sub_string in key and ('none' == key_exclude_string or not key_exclude_string in key):
                        return data[key]
                return 0

            self.bool_record = True

            # 主属性
            self.atVitalityBase = get_value_by_key_string(data, 'Vitality')
            self.atStrengthBase = get_value_by_key_string(data, 'Strength')
            self.atAgilityBase = get_value_by_key_string(data, 'Agility')
            self.atSpiritBase = get_value_by_key_string(data, 'Spirit')
            self.atSpunkBase = get_value_by_key_string(data, 'Spunk')

            # 基础攻击
            AttackPowerBase = get_value_by_key_substring(data, 'AttackPowerBase')
            self.atPhysicsAttackPowerBase = AttackPowerBase
            self.atSolarAttackPowerBase = AttackPowerBase
            self.atLunarAttackPowerBase = AttackPowerBase
            self.atNeutralAttackPowerBase = AttackPowerBase
            self.atPoisonAttackPowerBase = AttackPowerBase

            self.atAllTypeCriticalStrike = int(get_value_by_key_substring(data, 'CriticalStrikeRate') * GlobalParam.CriticalStrikeCof(self.level))  # 会心
            self.atAllTypeCriticalStrike -= max(self.kungfuSolarCriticalStrikeAdd, self.kungfuLunarCriticalStrikeAdd, self.kungfuNeutralCriticalStrikeAdd, self.kungfuPoisonCriticalStrikeAdd)

            self.atAllTypeCriticalDamagePowerBase = int((get_value_by_key_substring(data, 'CriticalDamagePowerPercent') - 1.75) * GlobalParam.CriticalDamagePowerCof(self.level))  # 会心效果

            Overcome = get_value_by_key_substring(data, 'Overcome', 'Percent')  # 破防
            self.atPhysicsOvercomeBase = Overcome
            self.atMagicOvercome = Overcome
            self.atPhysicsOvercomeBase -= self.kungfuPhysicsOvercomeAdd
            self.atMagicOvercome -= max(self.kungfuSolarOvercomeAdd, self.kungfuLunarOvercomeAdd, self.kungfuNeutralOvercomeAdd, self.kungfuPoisonOvercomeAdd)

            self.atStrainBase = get_value_by_key_substring(data, 'Strain', 'Percent')  # 无双
            self.atHasteBase = get_value_by_key_substring(data, 'Haste', 'Percent')  # 加速
            self.atSurplusValueBase = get_value_by_key_string(data, 'SurplusValue')  # 破招
            self.atMeleeWeaponDamageBase = get_value_by_key_substring(data, 'MeleeWeaponDamage', 'Rand')  # 武器伤害基础
            self.atMeleeWeaponDamageRand = get_value_by_key_string(data, 'MeleeWeaponDamageRand')  # 武器伤害浮动

            # 以下为 jx3box 标准 json 中没有的数据
            self.level = max(self.level, get_value_by_key_string(data, 'level'))
            self.atPhysicsShieldBase = get_value_by_key_string(data, 'atPhysicsShieldBase')
            self.atMagicShield = get_value_by_key_string(data, 'atMagicShield')

            self.bool_record = False

            self.bool_kungfu_init_over = True  # 添加一个标志位, 在导入属性后拒绝初始化心法.

        except:
            raise RuntimeError

    add_list = [
        'atBasePotentialAdd',  # 所有主属性
        # 'atVitalityBase',  # 体质
        # 'atStrengthBase',  # 力道
        # 'atAgilityBase',  # 身法
        # 'atSpiritBase',  # 根骨
        # 'atSpunkBase',  # 元气
        'atVitalityBasePercentAdd',  # 体质%
        'atStrengthBasePercentAdd',  # 力道%
        'atAgilityBasePercentAdd',  # 身法%
        'atSpiritBasePercentAdd',  # 根骨%
        'atSpunkBasePercentAdd',  # 元气%

        # 'atPhysicsAttackPowerBase',  # 外功基础攻击
        # 'atMagicAttackPowerBase',  # 内功基础攻击
        # 'atSolarAttackPowerBase',  # 阳性内功基础攻击
        # 'atLunarAttackPowerBase',  # 阴性内功基础攻击
        # 'atNeutralAttackPowerBase',  # 混元内功基础攻击
        # 'atPoisonAttackPowerBase',  # 毒性内功基础攻击
        'atPhysicsAttackPowerPercent',  # 外功基础攻击提升1024分数
        'atMagicAttackPowerPercent',  # 内功基础攻击提升1024分数
        'atSolarAttackPowerPercent',  # 阳性内功基础攻击提升1024分数
        'atLunarAttackPowerPercent',  # 阴性内功基础攻击提升1024分数
        'atNeutralAttackPowerPercent',  # 混元内功基础攻击提升1024分数
        'atPoisonAttackPowerPercent',  # 毒性内功基础攻击提升1024分数
        # 'atTherapyPowerBase',  # 治疗量
        'atTherapyPowerPercent',  # 治疗量%

        # 'atAllTypeCriticalStrike',  # 全会心等级
        # 'atPhysicsCriticalStrike',  # 外功会心等级
        # 'atMagicCriticalStrike',  # 内功会心等级
        # 'atSolarCriticalStrike',  # 阳性内功会心等级
        # 'atLunarCriticalStrike',  # 阴性内功会心等级
        # 'atNeutralCriticalStrike',  # 混元内功会心等级
        # 'atPoisonCriticalStrike',  # 毒性内功会心等级
        'atPhysicsCriticalStrikeBaseRate',  # 外功额外会心万分数
        'atSolarCriticalStrikeBaseRate',  # 阳性内功额外会心万分数
        'atLunarCriticalStrikeBaseRate',  # 阴性内功额外会心万分数
        'atNeutralCriticalStrikeBaseRate',  # 混元内功额外会心万分数
        'atPoisonCriticalStrikeBaseRate',  # 毒性内功额外会心万分数

        # 'atAllTypeCriticalDamagePowerBase',  # 全会心效果等级
        # 'atPhysicsCriticalDamagePowerBase',  # 外功会心效果等级
        # 'atMagicCriticalDamagePowerBase',  # 内功会心效果等级
        'atPhysicsCriticalDamagePowerBaseKiloNumRate',  # 外功额外会心效果1024分数
        'atMagicCriticalDamagePowerBaseKiloNumRate',  # 内功额外会心效果1024分数
        'atSolarCriticalDamagePowerBaseKiloNumRate',  # 阳性内功额外会心效果1024分数
        'atLunarCriticalDamagePowerBaseKiloNumRate',  # 阴性内功额外会心效果1024分数
        'atNeutralCriticalDamagePowerBaseKiloNumRate',  # 混元内功额外会心效果1024分数
        'atPoisonCriticalDamagePowerBaseKiloNumRate',  # 毒性内功额外会心效果1024分数

        # 'atPhysicsOvercomeBase',  # 外功基础破防等级
        # 'atMagicOvercome',  # 内功基础破防等级
        # 'atSolarOvercomeBase',  # 阳性内功破防等级
        # 'atLunarOvercomeBase',  # 阴性内功破防等级
        # 'atNeutralOvercomeBase',  # 混元内功破防等级
        # 'atPoisonOvercomeBase',  # 毒性内功破防等级
        'atPhysicsOvercomePercent',  # 外功基础破防等级提升1024分数
        'atSolarOvercomePercent',  # 阳性内功基础破防等级提升1024分数
        'atLunarOvercomePercent',  # 阴性内功基础破防等级提升1024分数
        'atNeutralOvercomePercent',  # 混元内功基础破防等级提升1024分数
        'atPoisonOvercomePercent',  # 毒性内功基础破防等级提升1024分数

        # 'atSurplusValueBase',  # 破招值
        # 'atStrainBase',  # 无双等级
        'atStrainRate',  # 无双等级提升1024分数
        'atStrainPercent',  # 额外无双1024分数

        # 'atHasteBase',  # 基础加速等级
        'atHasteBasePercentAdd',  # 额外加速1024分数
        'atUnlimitHasteBasePercentAdd',  # 突破上限加速1024分数

        # 'atMaxLifeBase',  # 最大气血值
        'atMaxLifePercentAdd',  # 最大气血值%
        'atMaxLifeAdditional',  # 额外气血值
        'atFinalMaxLifeAddPercent',  # 最终气血值%

        # 'atPhysicsShieldBase',  # 外功基础防御等级
        'atPhysicsShieldPercent',  # 外功基础防御等级提升1024分数
        'atPhysicsShieldAdditional',  # 额外外功防御等级
        # 'atMagicShield',  # 内功基础防御等级
        # 'atSolarMagicShieldBase',  # 阳性内功防御等级
        # 'atLunarMagicShieldBase',  # 阴性内功防御等级
        # 'atNeutralMagicShieldBase',  # 混元内功防御等级
        # 'atPoisonMagicShieldBase',  # 毒性内功防御等级
        'atSolarMagicShieldPercent',  # 阳性内功基础防御提升1024分数
        'atLunarMagicShieldPercent',  # 阴性内功基础防御提升1024分数
        'atNeutralMagicShieldPercent',  # 混元内功基础防御提升1024分数
        'atPoisonMagicShieldPercent',  # 毒性内功基础防御提升1024分数

        # 'atDodge',  # 闪避等级
        'atDodgeBaseRate',  # 闪避%
        # 'atParryBase',  # 招架等级
        'atParryPercent',  # 招架等级%
        'atParryBaseRate',  # 招架%
        # 'atParryValueBase',  # 拆招值
        'atParryValuePercent',  # 拆招值%

        'atGlobalResistPercent',  # 通用减伤
        'atPhysicsResistPercent',  # 外功通用减伤%
        'atSolarMagicResistPercent',  # 阳性内功通用减伤%
        'atLunarMagicResistPercent',  # 阴性内功通用减伤%
        'atNeutralMagicResistPercent',  # 混元内功通用减伤%
        'atPoisonMagicResistPercent',  # 毒性内功通用减伤%

        'atPhysicsDamageCoefficient',  # 物理易伤1024分数
        'atSolarDamageCoefficient',  # 阳性内功易伤1024分数
        'atLunarDamageCoefficient',  # 阴性内功易伤1024分数
        'atNeutralDamageCoefficient',  # 混元内功易伤1024分数
        'atPoisonDamageCoefficient',  # 毒性内功易伤1024分数

        # 'atToughnessBase',  # 御劲等级
        'atToughnessPercent',  # 御劲等级%
        'atToughnessBaseRate',  # 御劲%

        # 'atDecriticalDamagePowerBase',  # 化劲等级
        'atDecriticalDamagePowerPercent',  # 化劲等级%
        'atDecriticalDamagePowerBaseKiloNumRate',  # 化劲%

        # 'atMeleeWeaponDamageBase',  # 武器伤害
        # 'atMeleeWeaponDamageRand',  # 武器伤害浮动

        'atAllDamageAddPercent',  # 造成的全伤害和治疗效果提升1024分数
        'atAllMagicDamageAddPercent',  # 造成的内功伤害和治疗效果提升1024分数
        'atAddDamageByDstMoveState',  # 根据目标移动状态造成的伤害提升1024分数

        'atAllShieldIgnorePercent',  # 无视防御1024分数
        'atActiveThreatCoefficient',  # 仇恨提升1024分数
        'atDstNpcDamageCoefficient',  # 非侠士伤害
    ]

    base_list = [
        # 'atBasePotentialAdd',  # 所有主属性
        'atVitalityBase',  # 体质
        'atStrengthBase',  # 力道
        'atAgilityBase',  # 身法
        'atSpiritBase',  # 根骨
        'atSpunkBase',  # 元气
        # 'atVitalityBasePercentAdd',  # 体质%
        # 'atStrengthBasePercentAdd',  # 力道%
        # 'atAgilityBasePercentAdd',  # 身法%
        # 'atSpiritBasePercentAdd',  # 根骨%
        # 'atSpunkBasePercentAdd',  # 元气%

        'atPhysicsAttackPowerBase',  # 外功基础攻击
        'atMagicAttackPowerBase',  # 内功基础攻击
        'atSolarAttackPowerBase',  # 阳性内功基础攻击
        'atLunarAttackPowerBase',  # 阴性内功基础攻击
        'atNeutralAttackPowerBase',  # 混元内功基础攻击
        'atPoisonAttackPowerBase',  # 毒性内功基础攻击
        # 'atPhysicsAttackPowerPercent',  # 外功基础攻击提升1024分数
        # 'atMagicAttackPowerPercent',  # 内功基础攻击提升1024分数
        # 'atSolarAttackPowerPercent',  # 阳性内功基础攻击提升1024分数
        # 'atLunarAttackPowerPercent',  # 阴性内功基础攻击提升1024分数
        # 'atNeutralAttackPowerPercent',  # 混元内功基础攻击提升1024分数
        # 'atPoisonAttackPowerPercent',  # 毒性内功基础攻击提升1024分数
        'atTherapyPowerBase',  # 治疗量
        # 'atTherapyPowerPercent',  # 治疗量%

        'atAllTypeCriticalStrike',  # 全会心等级
        'atPhysicsCriticalStrike',  # 外功会心等级
        'atMagicCriticalStrike',  # 内功会心等级
        'atSolarCriticalStrike',  # 阳性内功会心等级
        'atLunarCriticalStrike',  # 阴性内功会心等级
        'atNeutralCriticalStrike',  # 混元内功会心等级
        'atPoisonCriticalStrike',  # 毒性内功会心等级
        # 'atPhysicsCriticalStrikeBaseRate',  # 外功额外会心万分数
        # 'atSolarCriticalStrikeBaseRate',  # 阳性内功额外会心万分数
        # 'atLunarCriticalStrikeBaseRate',  # 阴性内功额外会心万分数
        # 'atNeutralCriticalStrikeBaseRate',  # 混元内功额外会心万分数
        # 'atPoisonCriticalStrikeBaseRate',  # 毒性内功额外会心万分数

        'atAllTypeCriticalDamagePowerBase',  # 全会心效果等级
        'atPhysicsCriticalDamagePowerBase',  # 外功会心效果等级
        'atMagicCriticalDamagePowerBase',  # 内功会心效果等级
        # 'atPhysicsCriticalDamagePowerBaseKiloNumRate',  # 外功额外会心效果1024分数
        # 'atMagicCriticalDamagePowerBaseKiloNumRate',  # 内功额外会心效果1024分数
        # 'atSolarCriticalDamagePowerBaseKiloNumRate',  # 阳性内功额外会心效果1024分数
        # 'atLunarCriticalDamagePowerBaseKiloNumRate',  # 阴性内功额外会心效果1024分数
        # 'atNeutralCriticalDamagePowerBaseKiloNumRate',  # 混元内功额外会心效果1024分数
        # 'atPoisonCriticalDamagePowerBaseKiloNumRate',  # 毒性内功额外会心效果1024分数

        'atPhysicsOvercomeBase',  # 外功基础破防等级
        'atMagicOvercome',  # 内功基础破防等级
        'atSolarOvercomeBase',  # 阳性内功破防等级
        'atLunarOvercomeBase',  # 阴性内功破防等级
        'atNeutralOvercomeBase',  # 混元内功破防等级
        'atPoisonOvercomeBase',  # 毒性内功破防等级
        # 'atPhysicsOvercomePercent',  # 外功基础破防等级提升1024分数
        # 'atSolarOvercomePercent',  # 阳性内功基础破防等级提升1024分数
        # 'atLunarOvercomePercent',  # 阴性内功基础破防等级提升1024分数
        # 'atNeutralOvercomePercent',  # 混元内功基础破防等级提升1024分数
        # 'atPoisonOvercomePercent',  # 毒性内功基础破防等级提升1024分数

        'atSurplusValueBase',  # 破招值
        'atStrainBase',  # 无双等级
        # 'atStrainRate',  # 无双等级提升1024分数
        # 'atStrainPercent',  # 额外无双1024分数

        'atHasteBase',  # 基础加速等级
        # 'atHasteBasePercentAdd',  # 额外加速1024分数
        # 'atUnlimitHasteBasePercentAdd',  # 突破上限加速1024分数

        'atMaxLifeBase',  # 最大气血值
        # 'atMaxLifePercentAdd',  # 最大气血值%
        # 'atMaxLifeAdditional',  # 额外气血值
        # 'atFinalMaxLifeAddPercent',  # 最终气血值%

        'atPhysicsShieldBase',  # 外功基础防御等级
        # 'atPhysicsShieldPercent',  # 外功基础防御等级提升1024分数
        # 'atPhysicsShieldAdditional',  # 额外外功防御等级
        'atMagicShield',  # 内功基础防御等级
        'atSolarMagicShieldBase',  # 阳性内功防御等级
        'atLunarMagicShieldBase',  # 阴性内功防御等级
        'atNeutralMagicShieldBase',  # 混元内功防御等级
        'atPoisonMagicShieldBase',  # 毒性内功防御等级
        # 'atSolarMagicShieldPercent',  # 阳性内功基础防御提升1024分数
        # 'atLunarMagicShieldPercent',  # 阴性内功基础防御提升1024分数
        # 'atNeutralMagicShieldPercent',  # 混元内功基础防御提升1024分数
        # 'atPoisonMagicShieldPercent',  # 毒性内功基础防御提升1024分数

        'atDodge',  # 闪避等级
        # 'atDodgeBaseRate',  # 闪避%
        'atParryBase',  # 招架等级
        # 'atParryPercent',  # 招架等级%
        # 'atParryBaseRate',  # 招架%
        'atParryValueBase',  # 拆招值
        # 'atParryValuePercent',  # 拆招值%

        # 'atGlobalResistPercent',  # 通用减伤
        # 'atPhysicsResistPercent',  # 外功通用减伤%
        # 'atSolarMagicResistPercent',  # 阳性内功通用减伤%
        # 'atLunarMagicResistPercent',  # 阴性内功通用减伤%
        # 'atNeutralMagicResistPercent',  # 混元内功通用减伤%
        # 'atPoisonMagicResistPercent',  # 毒性内功通用减伤%

        # 'atPhysicsDamageCoefficient',  # 物理易伤1024分数
        # 'atSolarDamageCoefficient',  # 阳性内功易伤1024分数
        # 'atLunarDamageCoefficient',  # 阴性内功易伤1024分数
        # 'atNeutralDamageCoefficient',  # 混元内功易伤1024分数
        # 'atPoisonDamageCoefficient',  # 毒性内功易伤1024分数
        #
        'atToughnessBase',  # 御劲等级
        # 'atToughnessPercent',  # 御劲等级%
        # 'atToughnessBaseRate',  # 御劲%

        'atDecriticalDamagePowerBase',  # 化劲等级
        # 'atDecriticalDamagePowerPercent',  # 化劲等级%
        # 'atDecriticalDamagePowerBaseKiloNumRate',  # 化劲%

        'atMeleeWeaponDamageBase',  # 武器伤害
        'atMeleeWeaponDamageRand',  # 武器伤害浮动

        # 'atAllDamageAddPercent',  # 造成的全伤害和治疗效果提升1024分数
        # 'atAllMagicDamageAddPercent',  # 造成的内功伤害和治疗效果提升1024分数
        # 'atAddDamageByDstMoveState',  # 根据目标移动状态造成的伤害提升1024分数

        # 'atAllShieldIgnorePercent',  # 无视防御1024分数
        # 'atActiveThreatCoefficient',  # 仇恨提升1024分数
        # 'atDstNpcDamageCoefficient',  # 非侠士伤害
    ]

    def export_stat_change(self):
        ret = {}
        for name in self.__class__.add_list:
            value = getattr(self, name)
            if name not in self.last_stat or value != self.last_stat[name]:
                self.last_stat[name] = value
                ret[name] = value
        for name in self.__class__.base_list:
            value = getattr(self, name)
            if name not in self.last_stat or value != self.last_stat[name]:
                self.last_stat[name] = value
                ret[f'diff_{name}'] = getattr(self, f'diff_{name}')  # 语法糖, 实际上 self 并没有名为 f'diff_{name}' 的属性, 具体实现见 self.__getattribute__ 方法
        return ret

    def import_stat_change(self, data):
        for name in data:
            setattr(self, name, data[name])  # 语法糖. 当名为 f'diff_{name}' 的属性被 setattr 时, self.__setattr__ 方法会对此有特殊处理.

    def load_env(self, data: dict):
        '''
        注意, 此方法只能操作 base_list 中的属性. 原理是: 对于 base_list 中的属性, 导入和导出是记载与配装属性的差值并进行计算. 而对于 add_list 中的属性, 导入和导出是直接覆盖.
        '''
        self.bool_record = True

        if '帽子大附魔' in data and data['帽子大附魔']:
            self.atPhysicsOvercomeBase += 999
            self.atMagicOvercome += 999
        if '衣服大附魔' in data and data['衣服大附魔']:
            self.atPhysicsAttackPowerBase += 450
            self.atSolarAttackPowerBase += 538
            self.atLunarAttackPowerBase += 538
            self.atNeutralAttackPowerBase += 538
            self.atPoisonAttackPowerBase += 538

        self.bool_record = False
