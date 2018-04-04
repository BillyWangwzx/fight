# -*- coding:utf-8 -*-
'''
出牌规则
rules for legal action
'''
ALLOW_THREE_ONE = True
ALLOW_THREE_TWO = True


def all_legal_move(cards):
    #最快找到所有出牌可能，主动出击
    combs = []
    dic = {}
    for card in cards:
        dic[card] = dic.get(card, 0) + 1
    for card in dic:
        if dic[card] >= 1:
            combs.append([card])
        if dic[card] >= 2:
            combs.append([card] * 2)
        if dic[card] >= 3:
            combs.append([card] * 3)
            if ALLOW_THREE_TWO:
                for another_card in dic:
                    if dic[another_card] >= 2 and another_card != 13 and another_card != 14 and another_card != card:
                        combs.append([card] * 3 + [another_card] * 2)
            if ALLOW_THREE_ONE:
                for another_card in dic:
                    if dic[another_card] >= 1 and another_card != 13 and another_card != 14 and another_card != card:
                        combs.append([card] * 3 + [another_card])
        if dic[card] >= 4:
            combs.append([card] * 4)
    if 13 in cards and 14 in cards:
        combs.append([13, 14])
    combs.extend(detect_con(cards))
    combs.extend(detect_double_con(cards))
    return combs


def detect_con(cards, length=False, minimum=-1):
    # 顺,最短5最长12，3~A
    combs = []
    distinct_cards = sorted(list(set(cards)))
    cs = 0
    last = distinct_cards[0] - 1
    for i in distinct_cards:
        if i > minimum and i < 12:
            if i - last == 1:
                cs += 1
            else:
                cs = 1
            if cs >= 5:
                if not length:
                    combs.extend([list(range(i + 1 - j, i + 1)) for j in range(5, cs + 1)])
                elif cs >= length:
                    combs.append(list(range(i + 1 - length, i + 1)))
            last = i
    return combs


def detect_bomb(cards, minimum=-1):
    #炸弹
    combs = []
    dic = {}
    for card in cards:
        dic[card] = dic.get(card, 0) + 1
    for card in dic:
        if dic[card] == 4 and card > minimum:
            combs.append([card] * 4)
    if 13 in cards and 14 in cards:
        combs.append([13, 14])
    return combs



def detect_triple(cards, minimum=-1, dai=0):
    #飞机
    combs = []
    dic = {}
    for card in cards:
        dic[card] = dic.get(card, 0) + 1
    for card in dic:
        if dic[card] >= 3 and card > minimum:
            if dai == 0:
                combs.append([card] * 3)
            elif dai == 1:
                for another_card in dic:
                    if dic[another_card] >= 1 and another_card != 13 and another_card != 14 and another_card != card:
                        combs.append([card] * 3 + [another_card])
            else:
                for another_card in dic:
                    if dic[another_card] >= 2 and another_card != 13 and another_card != 14 and another_card != card:
                        combs.append([card] * 3 + [another_card] * 2)
    return combs


def detect_double(cards, minimum=-1):
    #对
    combs = []
    dic = {}
    for card in cards:
        dic[card] = dic.get(card, 0) + 1
    for card in dic:
        if dic[card] >= 2 and card > minimum:
            combs.append([card] * 2)
    return combs


def legal_move_after(last_card, cards):
    #接上一家
    combs = [[]]
    dic = {}
    for i in last_card:
        dic[i] = dic.get(i, 0) + 1
    if len(dic) == 2:
        for i in dic:
            if dic[i] == 3:
                minimum = i
                break
    else:
        minimum = min(last_card)
    if 13 in last_card and 14 in last_card:
        return combs
    else:
        if len(last_card) == 4 and len(dic) == 1:
            combs.extend(detect_bomb(cards, minimum))
        else:
            combs.extend(detect_bomb(cards))
            if len(last_card) >= 6 and min(dic.values()) == 2:
                combs.extend(detect_double_con(cards, len(dic), minimum))
            elif max(dic.values()) == 3:
                combs.extend(detect_triple(cards, minimum, len(last_card) - 3))
            elif len(last_card) == 2:
                combs.extend(detect_double(cards, minimum))
            elif len(last_card) == 1:
                combs.extend([[i] for i in set(cards) if i > minimum])
            else:
                combs.extend(detect_con(cards, len(last_card), minimum))
        return combs



def detect_double_con(cards, length=False, minimum=-1):
    # 对顺,最短5最长12，3~A
    dic = {}
    for i in cards:
        dic[i] = dic.get(i, 0)+1
    combs = []
    distinct_cards = sorted(list(dic.keys()))
    cs = 0
    last = distinct_cards[0] - 1
    for i in distinct_cards:
        if 12 > i > minimum:
            if dic[i] > 1:
                if i - last == 1:
                    cs += 1
                    if cs >= 3:
                        if not length:
                            combs.extend([list(range(i + 1 - j, i + 1)) * 2 for j in range(3, cs + 1)])
                        elif cs >= length:
                            combs.append(list(range(i + 1 - length, i + 1)) * 2)
                else:
                    cs = 1
                last = i
            else:
                pass
    return combs

ALL_POSSIBLE_MOVE = all_legal_move(list(range(13)) + list(range(13)) + list(range(13)) + list(range(13)) + [13, 14])
ALL_POSSIBLE_MOVE_DICT = {}
for card, i in zip(ALL_POSSIBLE_MOVE, range(len(ALL_POSSIBLE_MOVE))):
    card = tuple(card)
    ALL_POSSIBLE_MOVE_DICT[card] = i