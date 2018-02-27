# -*- coding:utf-8 -*-
from rules import *
from policy import *


def print_card(cards):
    print_cards = []
    dic = {0:'3',1:'4',2:'5',3:'6',4:'7',5:'8',6:'9',7:'10',8:'J',9:'Q',10:'K',11:'A',12:'2',13:'小王',14:'大王'}
    for i in cards:
        print_cards.append(dic[i])
    print(print_cards)


class Game:
    def __init__(self, policy=random_play):
        self.card = list(range(13)) + list(range(13)) + list(range(13)) + list(range(13)) + [13, 14]
        # 发牌,无地主
        random.shuffle(self.card)
        ''' 
        self.bonus_card = self.card_2[:3]
        self.card_2 = self.card_2[3:]
        '''
        # 每人18张牌，card_2为每个牌的编号
        # 定义游戏中三个玩家
        self.players = [Player(i, self, self.card[18 * i:(18 * i + 18)], brain=policy) for i in range(3)]
        # card_show为记录玩家出过的牌
        # last_card为记录本局游戏最后出现的牌（后面牌要按前面牌的规则出牌，如果另外两名玩家都选择不出，则可以任意出牌）
        self.card_show = []
        self.last_card = []
        # end=1代表游戏进行中，end=0代表游戏结束
        self.end = 1
        # 记录游戏回合数，round%3即为当前玩家编号
        self.round = 0
        self.card_num = [18, 18, 18]

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
                    self.card_show += handout_card
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
                    self.card_show += handout_card
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
                self.card_show += handout_card
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
        if move_card is None:
            handout = self.brain(legal_list, self.cards, self.game.card_show,
                                 self.game.players[(self.index + 1) % 3].cards,
                                 self.game.players[(self.index + 2) % 3].cards)
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
