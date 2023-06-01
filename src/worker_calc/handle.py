# -*- coding: utf-8 -*-
import src.worker_calc.init as init
import src.worker_calc.method as method
from src.character.player import player
from src.character.target import target
from src.frame.damage import Damage
import traceback


def handle(queue_get, queue_put):

    init.init()

    message_recv: dict = queue_get.get()
    player.load_character(message_recv['attr_self'])
    target.load_character(message_recv['attr_target'])
    player.attr.load_env(message_recv['env'])
    Damage.connect_queue = queue_put
    try:
        method.fight(message_recv['fight'])
        message_send = [{
            'category': 'fight_stat',
            'data': {
                'fight_duration': Damage.damage_list[-1]['tick'] / 1024,
                'dps': Damage.dps,
            }
        }]
        queue_put.put(message_send)
    except Exception as e:
        traceback.print_exc()
        message_send = [{
            'category': 'error',
        }]
        queue_put.put(message_send)
