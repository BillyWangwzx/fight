from copy import deepcopy


class MCState:
    def __init__(self, game):
        self.current_game = deepcopy(game)
        self.move = []
        self.round = self.current_game.round
        self.player = self.round % 3
        self.prob_win = 0

    def __call__(self, move, iter_num=200):
        self.move = move
        simulation_game_root = deepcopy(self.current_game)
        simulation_game_root.play_one_round(move)
        if simulation_game_root.end == 0:
            self.prob_win = 1
        else:
            win_time = 0
            for i in range(iter_num):
                simulation_game = deepcopy(simulation_game_root)
                if simulation_game.simulate_play() == self.player:
                    win_time += 1
            self.prob_win = win_time / float(iter_num)
