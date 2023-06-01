# -*- coding: utf-8 -*-
import pandas as pd
from src.frame.fetchdata import TabAttr


class RecipeSkill():
    '''
        RecipeSkill 类用于存放某个对象的秘籍并实现相关功能, 可以通俗地理解为秘籍列表.
    '''
    tabattr = TabAttr('settings/skill/recipeSkill.tab')

    def __init__(self) -> None:
        # self.df = None  # 初始化, 用于存放当前对象的所有已激活秘籍
        self.df = self.__class__.tabattr.fetch('RecipeID', 0).to_frame().T
        self.forget(0)
        pass

    def add(self, RecipeID, RecipeLevel=1):
        # 获取秘籍属性
        talent_attr = self.__class__.tabattr.fetch(['RecipeID', 'RecipeLevel'], [RecipeID, RecipeLevel])
        self.df = pd.concat([self.df, talent_attr.to_frame().T], axis=0)

    def forget(self, RecipeID, RecipeLevel=1):
        '''取消秘籍.'''
        self.df = self.df[self.df['RecipeID'] != RecipeID]

    def is_exist(self, RecipeID, RecipeLevel=1):
        return self.df.index.isin([(RecipeID, RecipeLevel)]).any()

    def get_by_SkillID(self, SkillID) -> pd.DataFrame:
        return self.df[self.df['SkillID'] == SkillID]

    def get_by_SkillRecipeType(self, SkillRecipeType) -> pd.DataFrame:
        ret = self.df
        ret = ret[ret['SkillRecipeType'] != 0]
        ret = ret[ret['SkillRecipeType'] == SkillRecipeType]
        return ret
