# -*- coding: utf-8 -*-

import src.worker_attrbenefit.method.kungfu_init as kungfu_init
import json


def init(obj):
    with open('data/player.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        kungfu_name = data['KungFuSkill']['name']
    func = getattr(kungfu_init, f'init_{kungfu_name}')
    func(obj)
