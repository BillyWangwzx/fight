import pickle
from policy import card_transform

class data_saver:
    def __init__(self, path, batch_size=10):
        self.num = 1
        self.batch_size = batch_size
        self.batch = 0
        self.path = path
        self.x_train = []
        self.y_train = []

    def __call__(self, state):
        x = [card_transform(state.current_game.players[(state.round + j) % 3].player_last_card) for j in [2, 1]]
        x.append(card_transform(state.current_game.players[state.round % 3].cards))
        x.extend([card_transform(state.current_game.card_show[(state.round+i) % 3]) for i in range(3)])
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
