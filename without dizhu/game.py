# -*- coding:utf-8 -*-
from rules import *
from policy import *
from collections import namedtuple


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
        self.card_show = [[], [], []]#分别记录三个玩家出过的牌
        self.last_card = []
        # end=1代表游戏进行中，end=0代表游戏结束
        self.end = 1
        # 记录游戏回合数，round%3即为当前玩家编号
        self.round = 0
        self.card_num = [18, 18, 18]



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


#positon


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
        while type(pos) is Position:
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



class YiModel(object):
    def __init__(self, load_snapshot=None,save_path=None):
        if save_path is None:
            self.save_path = load_snapshot
        else:
            self.save_path = save_path
        if load_snapshot:
            self.net = res_value_net(load_snapshot=load_snapshot)
        else:
            self.net = res_value_net()

    def reinforce_learning(self, n=1000, save_num=10, display=False):
        i = 0
        while i < n:
            print(i)
            new_game = Game()
            pos = game_to_position(new_game)
            x_positions = []
            while type(pos) is Position:
                move = self.net.predict_pos_move(pos, a=20, mode='qlearning')
                if display:
                    print(pos.to_play_player)
                    print_card(sorted(pos.players_cards[pos.to_play_player]))
                    print_card(move)
                x_positions.append((pos, move))
                pos = pos.move(move)
            print(pos)
            self.net.fit_game(x_positions, pos)
            i += 1
            if i % save_num == 0:
                self.net.save(self.save_path)
        self.net.save(self.save_path)

