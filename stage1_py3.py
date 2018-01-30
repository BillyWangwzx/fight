# -*- coding:utf-8 -*-
import random
import numpy as np
from copy import deepcopy
import pickle
ALLOW_THREE_ONE = True
ALLOW_THREE_TWO = True

class game:
    def __init__(self):
        self.card = list(range(13))+list(range(13))+list(range(13))+list(range(13))+[13,14]
        # 发牌,无地主
        random.shuffle(self.card)
        ''' 
        self.bonus_card = self.card_2[:3]
        self.card_2 = self.card_2[3:]
        '''
        #每人18张牌，card_2为每个牌的编号
        #定义游戏中三个玩家
        self.players = [player(self, self.card[18*i:(18*i+18)]) for i in range(3)]
        #card_show为记录玩家出过的牌
        #last_card为记录本局游戏最后出现的牌（后面牌要按前面牌的规则出牌，如果另外两名玩家都选择不出，则可以任意出牌）
        self.card_show = []
        self.last_card = []
        #end=1代表游戏进行中，end=0代表游戏结束
        self.end = 1
        #记录游戏回合数，round%3即为当前玩家编号
        self.round = 0

    def play(self):
        #显示出牌
        i = self.round % 3
        while self.end:
            handout_card = self.players[i].move()
            print(i, handout_card)
            if handout_card == 'winner':
                print('player ' + str(i) + ' win')
                self.end = 0
                break
            else:
                if handout_card != []:
                    self.last_card = handout_card
                    self.card_show += handout_card
            self.round += 1
            i = (i + 1) % 3

    def simulate_play(self):
        #不显示出牌,返回胜利玩家
        i = self.round % 3
        while self.end:
            handout_card = self.players[i].move()
            if handout_card == 'winner':
                return i
            else:
                if handout_card != []:
                    self.last_card = handout_card
                    self.card_show += handout_card
            i = (i + 1) % 3

    def play_one_round(self, move=None):
        #游戏只进行一轮，
        handout_card = self.players[self.round % 3].move(move)
        if handout_card == 'winner':
            self.end = 0
        else:
            if handout_card != []:
                self.last_card = handout_card
                self.card_show += handout_card
        self.round += 1


def all_legal_move(cards):
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
    combs = []
    dic = {}
    for card in cards:
        dic[card] = dic.get(card, 0) + 1
    for card in dic:
        if dic[card] >= 2 and card > minimum:
            combs.append([card] * 2)
    return combs


def legal_move_after(last_card, cards):
    combs = [[]]
    dic = {}
    for i in last_card:
        dic[i] = dic.get(i, 0) + 1
    if len(dic)==2:
        for i in dic:
            if dic[i]==3:
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
            if max(dic.values()) == 3:
                combs.extend(detect_triple(cards, minimum, len(last_card) - 3))
            elif len(last_card) == 2:
                combs.extend(detect_double(cards, minimum))
            elif len(last_card) == 1:
                combs.extend([[i] for i in set(cards) if i > minimum])
            else:
                combs.extend(detect_con(cards, len(last_card), minimum))
        return combs


def random_play(a):
    random.shuffle(a)
    return (a[0])


class player:
    def __init__(self, game, cards, brain=random_play):
        self.game = game
        self.cards = cards
        self.brain = brain
        self.player_last_card = []

    ''' 
    def jiaodizhu_random(self):
        return(np.random.rand(1))
    '''

    def get_legal_move(self):
        if self.game.last_card == self.player_last_card:
            legal_list = all_legal_move(self.cards)
        else:
            legal_list = legal_move_after(self.game.last_card, self.cards)
        return legal_list

    def move(self, move_card=None):
        legal_list = self.get_legal_move()
        # 随机出牌
        if move_card is None:
            handout = self.brain(legal_list)
        elif move_card not in legal_list:
            print('INLEGAL MOVE')
            raise Exception('INLEGAL MOVE')
        else:
            handout = move_card
        for card in handout:
            self.cards.remove(card)
        self.player_last_card = handout
        if len(self.cards) == 0:
            return 'winner'
        else:
            return handout

def card_transform(card):
    a = np.zeros(15)
    for i in card:
        a[i]+=1
    return a

class mc_state:
    def __init__(self, game):
        self.current_game = deepcopy(game)
        self.move = []
        self.round = self.current_game.round
        self.player = self.round % 3
        self.prob_win = 0

    def __call__(self, move, iter_num=5000):
        self.move = move
        simulation_game_root = deepcopy(self.current_game)
        simulation_game_root.play_one_round(move)
        if simulation_game_root.end == 0:
            self.prob_win =  1
        else:
            win_time = 0
            for i in range(iter_num):
                simulation_game = deepcopy(simulation_game_root)
                if simulation_game.simulate_play() == self.player:
                    win_time += 1
            self.prob_win = win_time / float(iter_num)

class data_saver:
    def __init__(self, path, batch_size=10):
        self.num = 1
        self.batch_size = batch_size
        self.batch = 0
        self.path = path
        self.x_train = []
        self.y_train = []

    def __call__(self, state):
        x = [card_transform(state.current_game.players[(state.round + j) % 3].cards) for j in range(3)]
        x.append(card_transform(state.current_game.card_show))
        x.append(card_transform(state.move))
        self.x_train.append(x)
        self.y_train.append(state.prob_win)
        if self.num % self.batch_size == 0:
            pickle.dump(self.x_train, open(self.path + 'x_%d.pkl' % self.batch, "wb"))
            pickle.dump(self.y_train, open(self.path + 'y_%d.pkl' % self.batch, "wb"))
            self.x_train = []
            self.y_train = []
            self.batch += 1
        print('record %d scores' % self.num)
        self.num += 1

    def save(self):
        pickle.dump(self.x_train, open(self.path + 'x_%d.pkl' % self.batch, "wb"))
        pickle.dump(self.y_train, open(self.path + 'y_%d.pkl' % self.batch, "wb"))
        self.batch += 1

class generater:
    def __init__(self, path='./data/stage1/' , sample_size = 10000):
        self.sample_size = sample_size
        self.saver = data_saver(path)
        self.games = [game() for _ in range(self.sample_size)]
        for simu_game in self.games:
            while simu_game.end:
                best_score = 0
                best_move = []
                legal_list = simu_game.players[simu_game.round%3].get_legal_move()
                print(legal_list)
                for move in legal_list:
                    print(move)
                    state = mc_state(simu_game)
                    state(move)
                    score = state.prob_win
                    print(score)
                    if score > best_score:
                        best_move = move
                    self.saver(state)
                simu_game.play_one_round(best_move)
                print(best_move)
            print('finish a game')

if __name__=='__main__':
    from multiprocessing import Pool
    import os
    print('Parent process %s.' % os.getpid())
    p = Pool(8)
    for i in range(8):
        p.apply_async(generater, args=('./data/stage1_%d/'%i,1250,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')