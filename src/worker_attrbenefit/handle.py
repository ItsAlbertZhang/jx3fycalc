# -*- coding: utf-8 -*-
from src.frame.damage import Damage
from src.worker_attrbenefit.subattr import SubAttr
import src.worker_attrbenefit.method as method
import src.worker_attrbenefit.init as init


def handle(index: int, pub_arg: dict, queue_get=None, queue_put=None):
    selfattr = SubAttr()
    targetattr = SubAttr()
    init.init(selfattr)
    if queue_put is not None:
        Damage.connect_queue = queue_put
    if queue_get is not None:
        pub_arg = queue_get.get()
    selfattr.load_from_json(pub_arg['attr_self']['attr'])
    targetattr.load_from_json(pub_arg['attr_target']['attr'])
    selfattr.load_env(pub_arg['env'])
    selfattr.load_attr_benefit(index)
    targetattr.DamageSource = selfattr
    method.fight(pub_arg['fight'], selfattr, targetattr)
    # if 0 == index:
    #     fight_analysis = dict(sorted(Damage.damage_statistics().items(), key=lambda x: x[1]['proportion'], reverse=True))
    #     with open('tempres.json', 'w', encoding='utf-8') as f:
    #         json.dump(fight_analysis, f, ensure_ascii=False, indent=4)
    #     # print(f"\n战斗时长: {'{:.2f}'.format(Damage.damage_list[-1]['tick'] / 1024)} 秒. 已将战斗统计保存至 tempres.json 文件.")
    if queue_put is not None:
        fight_stat = {
            'fight_duration': Damage.damage_list[-1]['tick'] / 1024,
            'dps': Damage.dps,
        }
        fight_analysis = dict(sorted(Damage.damage_statistics().items(), key=lambda x: x[1]['proportion'], reverse=True))
        # queue_put.put(fight_stat)
        # queue_put.put(fight_analysis)
        queue_put.put([{
            'category': 'fight_stat',
            'data': fight_stat,
        }, {
            'category': 'fight_analysis',
            'data': fight_analysis,
        }])
    return Damage.dps
