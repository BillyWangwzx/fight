# -*- coding:utf-8 -*-
import numpy as np
import random
import itertools
from copy import deepcopy
import cPickle


# 用4*15的矩阵来表示牌，其中第一行最后两个为大王小王，第二、三、四行最后两个元素无意义，记为card_1
# 用index表示牌，0~12、15~27、30~42，45~57为四个花色，13、14为大小王，其他数字没有意义，记为card_2
def card_transform(card_2):
    card_1 = np.zeros(60)
    card_1[card_2] = 1
    return card_1.reshape(4, 15)


def card_transform_ver(card_1):
    card_2 = np.arange(60)[card_1.reshape(60) == 1]
    return card_2


def detect_con(card_1, length=False, minium=-1):
    cumsum = np.sum(card_1, 0)
    legal_csc = []
    cs = 0
    if minium + length < 13:
        for i in range(minium + 1, 12):
            if cumsum[i] > 0:
                cs += 1
                if not length:
                    if cs >= 5:
                        legal_csc.extend([range(int(i + 1 - j), int(i + 1)) for j in range(5, cs + 1)])
                else:
                    if cs >= length:
                        legal_csc.append(range(int(i + 1 - length), i + 1))

            else:
                cs = 0
    return legal_csc


def move_after(length, last_card, cumsum, card_1, card_3):
    legal_list = []
    num = np.arange(15)[np.sum(last_card, 0) == length]
    for i in np.arange(15)[(cumsum >= length) & (np.arange(15) > num)]:
        legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], length)])
    for i in np.arange(15)[cumsum >= 4]:
        legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], 4)])
    if np.sum(card_1[0, 13:]) == 2:
        legal_list.append(card_transform([13, 14]))
    legal_list.append(np.zeros((4, 15)))
    return legal_list


def legal_move(card_2, last_card, player_last_card):
    # 一个，两个，三个(不带),四个炸弹 // 顺
    card_1 = card_transform(card_2)
    card_3 = [np.arange(4)[card_1.T[i] == 1] * 15 + i for i in range(15)]
    cumsum = np.sum(card_1, 0)
    # 如果其他两个人都没有要
    if np.sum(last_card) == 0 or np.sum((last_card - player_last_card) ** 2) == 0:
        legal_list = []
        # 单个
        legal_list.extend([card_transform(i) for i in card_2])
        # 两个 对
        for i in np.arange(15)[cumsum >= 2]:
            legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], 2)])
        # 三个 飞机
        for i in np.arange(15)[cumsum >= 3]:
            legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], 3)])
        # 四个 炸弹
        for i in np.arange(15)[cumsum >= 4]:
            legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], 4)])
        if np.sum(card_1[0, 13:]) == 2:
            legal_list.append(card_transform([13, 14]))
        # 顺
        legal_csc = detect_con(card_1)
        for i in legal_csc:
            legal_list.extend(card_transform(list(comb)) for comb in itertools.product(*[card_3[j] for j in i]))
    # 单张
    elif np.sum(last_card) == 1:
        legal_list = move_after(1, last_card, cumsum, card_1, card_3)
        # 对
    elif np.max(np.sum(last_card, 0)) == 2:
        legal_list = move_after(2, last_card, cumsum, card_1, card_3)
    # 三张
    elif np.sum(last_card) == 3:
        legal_list = move_after(3, last_card, cumsum, card_1, card_3)
    # 炸弹
    elif np.sum(last_card[0, 13:]):
        return [np.zeros((4, 15))]
    elif np.sum(last_card) == 4:
        legal_list = []
        num = np.arange(15)[np.sum(last_card, 0) == 4]
        for i in np.arange(15)[cumsum >= 4]:
            legal_list.extend([card_transform(list(comb)) for comb in itertools.combinations(card_3[i], 4)])
        if np.sum(card_1[1, 13:]) == 2:
            legal_list.append(card_transform([52, 53]))
        legal_list.append(np.zeros((4, 15)))
    # 顺????还有问题！！！！
    elif np.sum(last_card) >= 5:
        legal_list = []
        length = np.sum(last_card)
        legal_csc = detect_con(card_1, length, np.min(np.arange(15)[np.sum(last_card, 0) != 0]))
        for i in legal_csc:
            legal_list.extend(card_transform(list(comb)) for comb in itertools.product(*[card_3[j] for j in i]))
        legal_list.append(np.zeros((4, 15)))

    return legal_list


class game:
    def __init__(self):
        self.card_2 = np.concatenate([np.arange(28), np.arange(13) + 30, np.arange(13) + 45])
        # 发牌,无地主
        random.shuffle(self.card_2)
        self.card_2 = self.card_2.reshape(3, 18)
        self.players = [player(self, self.card_2[_]) for _ in range(3)]
        #
        self.card_1 = card_transform(self.card_2)
        #
        self.card_show = np.zeros(self.card_1.shape)
        self.last_card = np.zeros(self.card_1.shape)
        self.end = 1
        self.round = 0

    def play(self):
        i = self.round % 3
        while self.end:
            handout_card = self.players[i].move(self.last_card)
            print i, handout_card
            if (handout_card==np.ones((4,15))).all():
                print 'player' + str(i) + 'win'
                self.end = 0
                break
            else:
                if np.sum(handout_card) != 0:
                    self.last_card = handout_card
                self.card_show += self.last_card
            self.round += 1
            i = (i + 1) % 3

    def simulate_play(self, score):
        i = self.round % 3
        while self.end:
            handout_card = self.players[i].move(self.last_card)
            if (handout_card==np.ones((4,15))).all():
                score[i] += 1
                self.end = 0
                break
            else:
                if np.sum(handout_card) != 0:
                    self.last_card = handout_card
                self.card_show += self.last_card
            i = (i + 1) % 3

    def play_one_round(self, move=None):
        handout_card = self.players[self.round % 3].move(self.last_card, move)
        if (handout_card==np.ones((4,15))).all():
            self.end = 0
        else:
            if np.sum(handout_card) != 0:
                self.last_card = handout_card
            self.card_show += self.last_card
        self.round += 1


class player:
    def __init__(self, game, card):
        self.game = game
        self.card2 = card
        self.card1 = card_transform(card)
        self.player_last_card = np.zeros((4, 15))

    def legal_move_list(self):
        return legal_move(self.card2, self.game.last_card, self.player_last_card)

    def move(self, last_card, move_card=None):
        legal_list = legal_move(self.card2, last_card, self.player_last_card)
        # 随机出牌
        if move_card is None:
            random.shuffle(legal_list)
            handout = legal_list[0]
        elif 0 not in [np.sum((i-move_card)**2) for i in legal_list]:
            print('INLEGAL MOVE')
            raise Exception('INLEGAL MOVE')
        else:
            handout = move_card
        self.card1 = self.card1 - handout
        self.card2 = card_transform_ver(self.card1)
        if np.sum(handout) != 0:
            self.player_last_card = handout
        if not np.sum(self.card1):
            return np.ones((4,15))
        else:
            return handout


# generate data for training value network!!!!
class mc_state:
    def __init__(self, game):
        self.current_game = deepcopy(game)
        self.score = np.zeros(3)
        self.move = None
        self.round = self.current_game.round

    def __call__(self, move, iter_num=5000):
        simulation_game_root = deepcopy(self.current_game)
        simulation_game_root.play_one_round(move)
        if simulation_game_root.end == 0:
            return 1
        for i in range(5000):
            simulation_game = deepcopy(simulation_game_root)
            simulation_game.simulate_play(self.score)
        return self.score[self.current_game.round % 3] / float(iter_num)

    def save(self, i):
        x = [self.current_game.players[(self.round + j) % 3].card1 for j in range(3)]
        x.append(self.current_game.card_show)
        x.append(self.move)


class data_saver:
    def __init__(self, path, batch_size=10000):
        self.num = 1
        self.batch_size = batch_size
        self.batch = 0
        self.path = path
        self.x_train = []
        self.y_train = []

    def __call__(self, state):
        x = [state.current_game.players[(state.round + j) % 3].card1 for j in range(3)]
        x.append(state.current_game.card_show)
        x.append(state.move)
        self.x_train.append(x)
        self.y_train.append(state.score[state.round % 3])
        if self.num % self.batch_size == 0:
            cPickle.dump(self.x_train, open(path + 'x_%d.pkl' % self.batch, "wb"))
            cPickle.dump(self.y_train, open(path + 'y_%d.pkl' % self.batch, "wb"))
            self.x_train = []
            self.y_train = []
            self.batch += 1
        self.num += 1

    def save(self):
        cPickle.dump(self.x_train, open(path + 'x_%d.pkl' % self.batch, "wb"))
        cPickle.dump(self.y_train, open(path + 'y_%d.pkl' % self.batch, "wb"))
        self.batch += 1

class generater:
    def __init__(self, path='./data/stage1/' , sample_size = 100000):
        self.sample_size = sample_size
        self.saver = data_saver(path)
    def __call__(self):
        self.games = [game() for _ in range(self.sample_size)]
        for simu_game in self.games:
            while simu_game.end:
                best_score = 0
                best_move = None
                legal_list = simu_game.players[simu_game.round % 3].legal_move_list()
                if len(legal_list) > 10:
                    random.shuffle(legal_list)
                    legal_list = legal_list[:10]
                print(len(legal_list))
                for move in simu_game.players[simu_game.round%3].legal_move_list():
                    state = mc_state(simu_game)
                    score = state(move)
                    if score > best_score:
                        best_move = move
                    self.saver(state)
                    print('get one score')
                simu_game.play_one_round(best_move)
                print 'finish 1 move'
            print 'finish a game'
data_generator = generater()
data_generator()