# -*- coding:utf-8 -*-
'''
出牌方式
policy of playing cards
'''
import random
import numpy as np
from net import *
from keras.layers import Dense, Input, Conv2D, Dropout, Activation, Flatten, Reshape, BatchNormalization
from keras.models import Model
from keras.models import load_model


def card_transform(card):
    a = np.zeros(15)
    for i in card:
        a[i] += 1
    return a

def card_transform_all(mx):
    return [card_transform(i) for i in mx]


def random_play(a,b,c,d,e):
    random.shuffle(a)
    return a[0]


class Value_net():
    #first version of value net( input 5*15 )
    def __init__(self,path,method='best'):
        self.model = load_model(path)
        self.method = method

    def __call__(self, legal_list, card_in_hand, card_show,
                 next_player_hand_card, nnext_player_hand_card):
        if len(legal_list) == 1:
            return legal_list[0]
        x = [[card_transform(card_in_hand),
              card_transform(next_player_hand_card),
              card_transform(nnext_player_hand_card),
              card_transform(card_show),
              card_transform(move)] for move in legal_list]
        prob = self.model.predict(x)
        if self.method == 'best':
            return legal_list[np.argmax(prob)]
        else:
            prob = (np.exp(prob) / np.sum(np.exp(prob))).reshape(len(prob))
            index = np.random.choice(len(legal_list), 1, p=prob)[0]
            return legal_list[index]


class Choose_dizhu():
    def __init__(self,batch_size, archive_fit_sample):
        inp = Input(shape=(15,))
        x = Dense(64, activation='relu')(inp)
        x = Dense(1, activation='sigmoid')(x)
        self.model = Model(inp, x)
        self.model.compile(loss='binary_crossentropy', optimizer='nadam')
        self.archive = []
        self.batch_size = batch_size
        self.archive_fit_sample = archive_fit_sample
        self.wait = 32
        self.i = 0

    def predict(self, cards):
        return self.model.predict(cards)

    def fit_game(self, game):
        x = card_transform([i for i in game.players[0].cards])
        if game.simulate_play() == 0:
        #如果是地主赢了, 应该去叫地主
            x = (x, 1)
        #如果是地主输了，则不应该去叫地主
        else:
            x = (x, 0)
        self.archive.append(x)
        self.i += 1
        if self.i > self.wait:
            if len(self.archive) >= self.archive_fit_sample:
                archive_train_sample = random.sample(self.archive, self.archive_fit_sample)
                x_t,y_t = [], []
                for x, y in archive_train_sample:
                    x_t.append(x)
                    y_t.append(y)
                    if len(x_t) % self.archive_fit_sample:
                        self.model.train_on_batch(np.array(x_t),np.array(y_t))
                        x_t, y_t = [], []
                self.i = 0

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        self.model.load(path)


class random_value_net():
    def predict_pos_move(self,pos):
        moves = pos.moves()
        random.shuffle(moves)
        return moves[0]


class cnn_value_net():
    def __init__(self, model = 'best',load_snapshot=None):
        self.model = model
        if load_snapshot:
            self.model = load_model(load_snapshot)
        else:
            inp = Input((6, 15))
            x = Reshape((6, 15, 1))(inp)
            x = BatchNormalization()(x)
            x = Conv2D(filters=128, kernel_size=(6, 1), activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Conv2D(filters=128, kernel_size=(1, 3), activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Flatten()(x)
            x = Dense(64, activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Dense(1, activation='sigmoid')(x)
            self.model = Model(inputs=inp, outputs=x)
            self.model.compile(loss='mean_squared_error', optimizer='nadam', metrics=['mae'])

    def predict_pos_move(self, pos, a=1):
        moves = pos.moves()
        if len(moves) != 1:
            x = [card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                 pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.players_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            if self.model == 'best':
                return moves[np.argmax(value)]
            else:
                prob = (np.exp(a*value) / np.sum(np.exp(a*value))).reshape(len(value))
                index = np.random.choice(len(value), 1, p=prob)[0]
                return moves[index]
        else:
            return moves[0]


    def predict_pos_values(self,pos):
        moves = pos.moves()
        if pos.players_cards[pos.to_play_player] in moves:
            return pos.players_cards[pos.to_play_player]
        if len(moves) != 1:
            x = [card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                 pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.players_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            return zip(moves, value)
        else:
            return 1

class res_value_net:
    def __init__(self,batch_size=32, archive_fit_samples=64, n_stage=5, model='best',load_snapshot=None):
        self.batch_size = batch_size
        self.archive_fit_samples = archive_fit_samples
        self.position_archive = []
        self.model = model
        if load_snapshot:
            self.model = load_model(load_snapshot)
        else:
            net = ResNet(n_stage=n_stage)
            self.model = net.create()


    def predict_pos_move(self, pos):
        moves = pos.moves()
        if len(moves) != 1:
            x = [card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                 pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.players_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            if self.model == 'best':
                return moves[np.argmax(value)]
            else:
                prob = (np.exp(50*value) / np.sum(np.exp(50*value))).reshape(len(value))
                index = np.random.choice(len(value), 1, p=prob)[0]
                return moves[index]
        else:
            return moves[0]

    def predict_pos_values(self,pos):
        moves = pos.moves()
        if pos.players_cards[pos.to_play_player] in moves:
            return pos.players_cards[pos.to_play_player]
        if len(moves) != 1:
            x = [card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                 pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.players_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            return zip(moves, value)
        else:
            return 1

    def fit_game(self, X_positions, result):
        X_positions


class cnn_value_net_odd():
    def __init__(self, model = 'best',load_snapshot=None):
        self.model = model
        if load_snapshot:
            self.model = load_model(load_snapshot)
        else:
            inp = Input((6, 15))
            x = Reshape((6, 15, 1))(inp)
            x = BatchNormalization()(x)
            x = Conv2D(filters=128, kernel_size=(6, 1), activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Conv2D(filters=128, kernel_size=(1, 3), activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Flatten()(x)
            x = Dense(64, activation='relu')(x)
            x = Dropout(0.2)(x)
            x = Dense(1, activation='sigmoid')(x)
            self.model = Model(inputs=inp, outputs=x)
            self.model.compile(loss='mean_squared_error', optimizer='nadam', metrics=['mae'])

    def predict_pos_move(self, pos, a=1):
        moves = pos.moves()
        if pos.players_cards[pos.to_play_player] in moves:
            return pos.players_cards[pos.to_play_player]
        if len(moves) != 1:
            x = [card_transform_all([
                pos.player_last_card[pos.to_play_player],
                pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.player_last_card[(pos.to_play_player + 2) % 3],
                pos.players_cards[0]+pos.players_cards[1]+pos.players_cards[2],
                move]) for move in moves]
            value = self.model.predict(x)
            if self.model == 'best':
                return moves[np.argmax(value)]
            else:
                prob = (np.exp(a*value) / np.sum(np.exp(a*value))).reshape(len(value))
                index = np.random.choice(len(value), 1, p=prob)[0]
                return moves[index]
        else:
            return moves[0]

    def fit_game(self):
        return