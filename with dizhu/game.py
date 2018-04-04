# -*- coding:utf-8 -*-
from rules import *
from policy import *
import numpy as np
from copy import deepcopy
from collections import namedtuple
from multiprocessing import Queue, Process

N = 5

def print_card(cards):
    print_cards = []
    dic = {0:'3',1:'4',2:'5',3:'6',4:'7',5:'8',6:'9',7:'10',8:'J',9:'Q',10:'K',11:'A',12:'2',13:'小王',14:'大王'}
    for i in sorted(cards):
        print_cards.append(dic[i])
    print(print_cards)


class Game:
    def __init__(self, policy_dizhu = Choose_dizhu(32, 64), policy=random_play):
        self.card = list(range(13)) + list(range(13)) + list(range(13)) + list(range(13)) + [13, 14]
        # 发牌,有地主
        random.shuffle(self.card)
        self.bonus_card = self.card[:3]
        self.card = self.card[3:]

        # 每人18张牌，card_2为每个牌的编号
        # 定义游戏中三个玩家
        self.players = [Player(i, self, self.card[17 * i:(17 * i + 17)], brain=policy) for i in range(3)]
        # card_show为记录玩家出过的牌
        # last_card为记录本局游戏最后出现的牌（后面牌要按前面牌的规则出牌，如果另外两名玩家都选择不出，则可以任意出牌）
        self.card_show = [[], [], []]#分别记录三个玩家出过的牌
        self.last_card = []
        # end=1代表游戏进行中，end=0代表游戏结束
        self.end = 1
        # 记录游戏回合数，round%3即为当前玩家编号
        self.round = 0
        #选地主
        value = policy_dizhu.predict(np.array([card_transform(self.players[i].cards) for i in range(3)]))
        dizhu_num = np.argmax(value)
        self.players = [self.players[(dizhu_num+i) % 3] for i in range(3)]
        self.dizhu = self.players[0]
        self.dizhu.cards += self.bonus_card
        self.card_num = [20, 17, 17]



    def play(self):
        # 显示出牌
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
                    self.card_num[i] -= len(handout_card)
                    self.card_show[i] += handout_card
            self.round += 1
            i = (i + 1) % 3

    def simulate_play(self):
        # 不显示出牌,返回胜利玩家
        i = self.round % 3
        while self.end:
            handout_card = self.players[i].move()
            if handout_card == 'winner':
                return i
            else:
                if handout_card != []:
                    self.last_card = handout_card
                    self.card_num[i] -= len(handout_card)
                    self.card_show[i] += handout_card
            self.round += 1
            i = (i + 1) % 3

    def play_one_round(self, move=None, verbose=0):
        # 游戏只进行一轮，
        if verbose == 1:
            print_card(sorted(self.players[self.round % 3].cards))
        handout_card = self.players[self.round % 3].move(move)

        if handout_card == 'winner':
            self.end = 0
        else:
            if handout_card != []:
                self.last_card = handout_card
                self.card_num[self.round % 3] -= len(handout_card)
                self.card_show[self.round % 3] += handout_card
            if verbose == 1:
                print_card(sorted(handout_card))
        self.round += 1


class Player:
    def __init__(self, i, game, cards, brain=random_play):

        self.index = i
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
        # 出牌
        #WARNING
        if move_card is None:
            handout = self.brain(legal_list, self.cards, self.game.card_show[0]+self.game.card_show[1]+self.game.card_show[2],self.game.players[(self.index + 1) % 3].cards,self.game.players[(self.index + 2) % 3].cards)
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

####新轮子


class Position(namedtuple('Position','players_cards shown_cards game_last_card player_last_card to_play_player')):
    def move(self, c):
        new_PC, new_SC, new_PLC = [[], [], []], [[], [], []], [i for i in self.player_last_card]
        for i in range(3):
            new_PC[i] = [card for card in self.players_cards[i]]
            new_SC[i] = [card for card in self.shown_cards[i]]
            if i == self.to_play_player:
                for card in c:
                    new_PC[i].remove(card)
                if len(new_PC[i]) == 0:
                    return self.to_play_player
                new_SC[i] += c
                new_PLC[i] = c
        if c == []:
            new_glc = self.game_last_card
        else:
            new_glc = c
        return Position(players_cards=new_PC, shown_cards=new_SC, game_last_card=new_glc
                        , player_last_card=new_PLC, to_play_player=(self.to_play_player+1) % 3)

    def moves(self):
        if self.player_last_card[self.to_play_player] == self.game_last_card:
            return all_legal_move(self.players_cards[self.to_play_player])
        else:
            return legal_move_after(self.game_last_card, self.players_cards[self.to_play_player])

    def simulate(self, net, a=1, display=False):
        pos = self
        while type(pos) is not int:
            move = net.predict_pos_move(pos, a)
            if display:
                print_card(pos.players_cards[pos.to_play_player])
                print_card(move)
            pos = pos.move(move)
        return pos


def game_to_position(game):
    players_cards = [game.players[i].cards for i in range(3)]
    shown_card = game.card_show
    game_last_card = game.last_card
    player_last_card = [game.players[i].player_last_card for i in range(3)]
    return Position(players_cards=players_cards, shown_cards=shown_card,
                    game_last_card=game_last_card, player_last_card=player_last_card,
                    to_play_player=game.round % 3)


class ModelServer(Process):
    def __init__(self, cmd_queue, res_queues, load_snapshot=None):
        super(ModelServer, self).__init__()
        self.cmd_queue = cmd_queue
        self.res_queues = res_queues
        self.load_snapshot = load_snapshot

    def run(self):
        try:
            if self.load_snapshot:
                net = load_model(self.load_snapshot)
            else:
                from net import ResNet
                net = ResNet(N)
                net.create()

            class PredictStash(object):
                def __init__(self, trigger, res_queues):
                    self.stash = []
                    self.trigger = trigger
                    self.res_queues = res_queues

                def add(self,kind, X_pos):
                    self.stash.append((kind, X_pos))
                    if len(self.stash) >= self.trigger:
                        self.process()

                def process(self):
                    if not self.stash:
                        return
                    value = net.predict([s[1] for s in self.stash])

        except:
            import traceback
            traceback.print_exc()


class YiModel(object):
    def __init__(self, load_snapshot=None):
        self.cmd_queue = Queue()
        self.res_queues = [Queue() for i in range(128)]
        self.server = Model