# -*- coding:utf-8 -*-
'''
出牌方式
policy of playing cards
'''
import random
import numpy as np
from keras.models import load_model
from keras.layers import Dense, Input, Conv2D, Dropout, Activation, Flatten, Reshape, BatchNormalization

from net import *
import itertools

def card_transform(card):
    a = np.zeros(15)
    for i in card:
        a[i] += 1
    return a


def card_transform_all(mx):
    return [card_transform(i) for i in mx]


def random_play(a,b,c,d,e,f):
    random.shuffle(a)
    return a[0]

#changable
def pos_to_x(pos, move):
    x = card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                            pos.player_last_card[(pos.to_play_player + 1) % 3],
                            pos.players_cards[pos.to_play_player],
                            pos.shown_cards[pos.to_play_player],
                            pos.shown_cards[(pos.to_play_player + 1) % 3],
                            pos.shown_cards[(pos.to_play_player + 2) % 3],
                            move])
    return x


class res_value_net:
    def __init__(self, batch_size=32, archive_fit_samples=64, n_stages=5,load_snapshot=None):
        self.batch_size = batch_size
        self.archive_fit_samples = archive_fit_samples
        self.position_archive = []
        if load_snapshot:
            self.model = load_model(load_snapshot)
        else:
            net = ResNet(n_stages=n_stages)
            self.model = net.create()


    def predict_pos_move(self, pos,a=1,mode='best'):
        moves = pos.moves()
        if len(moves) != 1:
            x = [card_transform_all([pos.player_last_card[(pos.to_play_player + 2) % 3],
                 pos.player_last_card[(pos.to_play_player + 1) % 3],
                pos.players_cards[pos.to_play_player],
                pos.shown_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            if mode == 'best':
                return moves[np.argmax(value)]
            elif mode =='qlearning':
                if random.random() < 0.2:
                    prob = (np.exp(a * value) / np.sum(np.exp(a * value))).reshape(len(value))
                    index = np.random.choice(len(value), 1, p=prob)[0]
                    return moves[index]
                else:
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
                pos.shown_cards[pos.to_play_player],
                pos.shown_cards[(pos.to_play_player + 1) % 3],
                pos.shown_cards[(pos.to_play_player + 2) % 3],
                move]) for move in moves]
            value = self.model.predict(x)
            for i in zip(moves, value):print(i)
        else:
            return 1

    def fit_game(self, X_positions, result):
        X_posres = []
        for pos, move in X_positions:
            X_posres.append((pos_to_x(pos, move), 1 if pos.to_play_player == result else 0))
        self.position_archive.extend(X_posres)
        if len(self.position_archive) >= self.archive_fit_samples:
            archive_samples = random.sample(self.position_archive, self.archive_fit_samples)
        else:
            archive_samples = self.position_archive

        X_fit_samples = list(itertools.chain(X_posres, archive_samples))
        random.shuffle(X_fit_samples)
        x_t, y_t = [], []
        for x,y in  X_fit_samples:
            x_t.append(x)
            y_t.append(y)
            if len(x_t) % self.batch_size == 0:
                self.model.train_on_batch(np.array(x_t), np.array(y_t))
        if len(x_t) > 0:
            self.model.train_on_batch(np.array(x_t), np.array(y_t))

    def save(self,path):
        self.model.save(path)

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


