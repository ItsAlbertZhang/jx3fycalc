# -*- coding: utf-8 -*-
from src.frame.attribute import Attribute
import json


class SubAttr(Attribute):
    def __init__(self) -> None:
        super().__init__()

    def load_attr_benefit(self, index):
        self.bool_record = True
        if 2 == index:
            self.atPhysicsAttackPowerBase += 360
            self.atSolarAttackPowerBase += 430
            self.atLunarAttackPowerBase += 430
            self.atNeutralAttackPowerBase += 430
            self.atPoisonAttackPowerBase += 430
        elif 1 == index:
            self.atSpunkBase += 179
        elif 3 == index:
            self.atAllTypeCriticalStrike += 799
        elif 4 == index:
            self.atAllTypeCriticalDamagePowerBase += 799
        elif 5 == index:
            self.atPhysicsOvercomeBase += 799
            self.atMagicOvercome += 799
        elif 6 == index:
            self.atStrainBase += 799
        elif 7 == index:
            self.atSurplusValueBase += 799
        self.bool_record = False
