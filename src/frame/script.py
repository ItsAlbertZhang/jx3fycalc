# -*- coding: utf-8 -*-
import importlib
import sys
from pathlib import Path


class Script():
    @classmethod
    def get_moudle(cls, path: str):
        # 对传入的路径字符串进行处理
        path = path.replace('%', '')
        name = path[max(path.rfind('/'), path.rfind('\\'))+1:path.rfind('.')]
        # 获取模块
        modulepath = 'src.scripts.' + name
        if modulepath in sys.modules:  # 如果模块存在
            moudle = sys.modules[modulepath]
        elif Path('src/scripts').exists() and Path('src/scripts').is_dir():  # 如果模块不存在, 且当前处于开发环境中
            with open(Path('src/scripts/' + name + '.py'), 'x', encoding='utf-8') as f:
                s = f'# -*- coding: utf-8 -*-\nfrom src.character.player import player\nfrom src.scripts.base import ScriptBase\n\n\nclass {name}():\n    @classmethod\n    def cast(cls, skill, *args, **kwargs):\n        ret = None\n        dwSkillLevel = skill[\'Level\']\n        return ret'
                f.write(s)
            raise RuntimeError(f'Script file not found: {name}')
        else:  # 否则
            # moudle = importlib.import_module(modulepath)
            raise RuntimeError('Module not exist.')
        # 执行模块类中的 cast 函数
        modulecls = getattr(moudle, name)
        return modulecls

    @classmethod
    def execute(cls, path: str, skill, *args, **kwargs):
        '''执行脚本. 传入的参数应当原封不动传递给脚本模块类中的 cast 方法. 返回值原封不动返回给调用本方法的函数.'''
        modulecls = cls.get_moudle(path)
        return modulecls.cast(skill, *args, **kwargs)

    @classmethod
    def apply(cls, path: str, *args, **kwargs):
        '''执行脚本的 apply 方法. 传入的参数应当原封不动传递给脚本模块类中的 apply 方法.'''
        modulecls = cls.get_moudle(path)
        return modulecls.apply(*args, **kwargs)

    @classmethod
    def unapply(cls, path: str, *args, **kwargs):
        '''执行脚本的 unapply 方法. 传入的参数应当原封不动传递给脚本模块类中的 unapply 方法.'''
        modulecls = cls.get_moudle(path)
        return modulecls.unapply(*args, **kwargs)

    @classmethod
    def on_remove(cls, path: str, *args, **kwargs):
        '''执行脚本的 on_remove 方法. 传入的参数应当原封不动传递给脚本模块类中的 on_remove 方法.'''
        modulecls = cls.get_moudle(path)
        return modulecls.on_remove(*args, **kwargs)
