# -*- coding:utf-8 -*-
'''
出牌方式
policy of playing cards
'''
import random
import numpy as np


def card_transform(card):
    a = np.zeros(15)
    for i in card:
        a[i] += 1
    return a


def random_play(a,b,c,d,e,f):
    random.shuffle(a)
    return a[0]


def value_net_random(legal_list, card_in_hand, card_show, next_player_hand_card, nnext_player_hand_card):
    if len(legal_list) == 1:
        return legal_list[0]
    x = [[card_transform(card_in_hand),
          card_transform(next_player_hand_card),
          card_transform(nnext_player_hand_card),
          card_transform(card_show),
          card_transform(move)] for move in legal_list]
    prob = value_net.predict(x)
    prob = (np.exp(prob) / np.sum(np.exp(prob))).reshape(len(prob))
    index = np.random.choice(len(legal_list), 1, p=prob)[0]
    return legal_list[index]

