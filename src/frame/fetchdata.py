# -*- coding: utf-8 -*-
import pandas as pd
import pickle
from pathlib import Path


class TabAttr():
    '''
        该类用于获取表数据(如 buff.tab, skills.tab, recipeSkill.tab 等)的属性.
    '''
    instance = []

    def __init__(self, pathstr: str) -> None:
        self.path = 'pak' / Path(pathstr)
        self.index = []
        self.data_loaded = False
        self.data_index_changed = False
        self.pakdata_loaded = False
        self.pakdata_index_changed = False
        self.rows_added = 0
        try:  # 尝试打开二进制文件以获取数据
            with open(f'data/{self.path.stem}{self.path.suffix[1:]}.bin', 'rb') as f:
                self.df = pickle.load(f)
                self.data_loaded = True
        except:  # 打开失败
            if False == self.pakdata_loaded:
                try:
                    self.load_pakdata()
                    self.pakdata_loaded = True  # 设置已加载标志, 防止再次加载.
                except:
                    raise RuntimeError(f'{self.path} loads failed, need pak file as data source.')
        # try:
        #     self.load_pakdata()
        #     self.pakdata_loaded = True  # 设置已加载标志, 防止再次加载.
        # except:
        #     pass
        self.__class__.instance.append(self)
        # print(f'Init {self.path} over.')

    def load_pakdata(self):
        '''
            尝试加载 pak 包中完整的 tab. 该方法应当只在开发环境中被确实调用.
            在生产环境中, 应当保证 data 包中包含所有要使用的数据.
        '''
        # 打开以获取表头
        self.df_pak = pd.read_table(self.path, encoding='gbk', low_memory=False)
        for col in self.df_pak.columns:
            if self.df_pak[col].dtype != 'object':
                self.df_pak[col] = self.df_pak[col].astype('Int64', errors='ignore')
            # buff.tab 的特殊处理
            if 'buff.tab' == self.path.name:
                if 'BeginAttrib' in col or 'BeginValue' in col or 'ActiveAttrib' in col or 'ActiveValue' in col or 'EndTimeAttrib' in col or 'EndTimeValue' in col:
                    self.df_pak[col] = self.df_pak[col].astype('object')
        # 保存表头并重新打开
        self.dtype_dict = self.df_pak.dtypes.apply(lambda x: x.name).to_dict()
        self.df_pak = pd.read_table(self.path, encoding='gbk', dtype=self.dtype_dict, keep_default_na=False, na_values=[''])
        if False == self.data_loaded:
            # 如果 self.df 还没有加载, 说明文件不存在, 此时新建一个 self.df
            self.df = self.df_pak.copy()
            self.df.drop(self.df.index, inplace=True)
            self.data_loaded = True
        print(f'Warning: Load pak data file {self.path}.')

    def fetch(self, key, value, alternative_value_list=None):
        '''
            获取某条数据.
        '''
        if type(key) == str:
            key = [key]
            value = [value]
        for i in key:
            if i not in self.index:
                if not self.data_index_changed:
                    self.df = self.df.set_index(i, drop=False)
                    self.data_index_changed = True
                else:
                    self.df = self.df.set_index(i, append=True, drop=False)
                self.index.append(i)
        # search = [value[key.index(x)] if x in key else slice(None) for x in self.index]
        search = tuple(value[key.index(x)] if x in key else slice(None) for x in self.index)
        # df_ret = self.df.loc[search]
        try:  # 尝试直接在 data 包的 buff.tab 对应的数据中获取.
            return self.df.loc[search]
        except:
            if alternative_value_list is not None:
                for i in alternative_value_list:
                    search_alternative = tuple(i[key.index(x)] if x in key else slice(None) for x in self.index)
                    try:
                        return self.df.loc[search_alternative]
                    except:
                        pass
        '''
            无法在 data 包中的数据中获取所需的数据. 转而去 pak 包中寻找.
            注意, 本段代码应当只在开发环境中被真正运行. 在生产环境中, 应当保证 data 包中包含所有要使用的数据.
        '''
        if False == self.pakdata_loaded:
            try:
                self.load_pakdata()
                self.pakdata_loaded = True  # 设置已加载标志, 防止再次加载.
            except:
                raise RuntimeError(f'{self.path} loads failed, need pak file as data source.')
        # 将属性加载入 data 包的数据中. 注意, 仅对 key[0] 做检查 (例如, key 为 ['BuffID', 'BuffLevel'], 此时仅对第一项做检查)
        df_ret = self.df_pak.loc[self.df_pak[key[0]] == value[0]]
        df_ret = df_ret.set_index(self.index, drop=False)
        self.df = pd.concat([self.df, df_ret], axis=0).sort_index()
        self.rows_added += len(df_ret)
        print(f'Warning: Load data from {self.path}.')
        try:  # 尝试直接在 data 包的 buff.tab 对应的数据中获取.
            return self.df.loc[search]
        except:
            if alternative_value_list is not None:
                for i in alternative_value_list:
                    search_alternative = tuple(i[key.index(x)] if x in key else slice(None) for x in self.index)
                    try:
                        return self.df.loc[search_alternative]
                    except:
                        pass

    @classmethod
    def save_data(cls):
        '''
            将数据保存至 data 包. 同样, 本方法应当只在开发环境中被确实调用. 注意, 该方法不应当通过实例化的对象调用, 而是应当直接通过类调用.
        '''
        for i in cls.instance:
            i: TabAttr
            if i.rows_added > 0:
                with open(f'data/{i.path.stem}{i.path.suffix[1:]}.bin', 'wb') as f:
                    pickle.dump(i.df, f)
                print(f'Add {i.rows_added} rows in {i.path}.')
            # else:
            #     print(f'{i.path} is not used.')
