from game import Game
from data_save import data_saver
import numpy as np
from mc import *
from policy import card_transform
from keras.layers import Dense, Input, Conv2D, Dropout, Activation, Flatten, Reshape
from keras.models import Model
from keras.models import load_model


def generator(path='./data/stage1/', sample_size=50):
    print('start')
    value_net = load_model('C:/Users/wangzixi/Desktop/doudizhu_model/value.h5')
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

    saver = data_saver(path)
    games = [Game(value_net_random) for _ in range(sample_size)]
    for simu_game in games:
        while simu_game.end:
            best_score = 0
            best_move = []
            legal_list = simu_game.players[simu_game.round % 3].get_legal_move()
            print(legal_list)
            for move in legal_list:
                print(move)
                state = MCState(simu_game)
                state(move)
                score = state.prob_win
                print(score)
                if score > best_score:
                    best_score = score
                    best_move = move
                saver(state)
            simu_game.play_one_round(best_move)
            print(best_move)
        print('finish a game')

