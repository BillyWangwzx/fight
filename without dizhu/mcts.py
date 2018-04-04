from game import *

EXPAND_VISITS = 2
PUCT_C = 0.5


class Treenode():
    def __init__(self, net, pos, move=[]):
        self.move = move
        self.net = net
        self.pos = pos
        self.v = 0
        self.w = 0

        self.children = None

    def expand(self):
        """add and initialize children to a leaf node"""
        # distribution = self.net.predict_distribution(self.pos)
        self.children = []
        for c in self.pos.moves():
            pos2 = self.pos.move(c)
            # 如果存在斩杀，children应为空值（即表面以结束游戏？）
            if pos2 is int:
                self.children = [Treenode(self.net, pos2, c)]
            node = Treenode(self.net, pos2, move=c)
            node.v += 1
            tree_update([self, node], node.pos.simulate(self.net))
            self.children.append(node)

    def winrate(self):
        return float(self.w) / self.v if self.v > 0 else float('nan')

    def best_move(self, proportional=False):
        if self.children is None:
            return None
        if proportional:
            probs = [(float(node.v) / self.v) ** 2 for node in self.children]
            probs_tot = sum(probs)
            probs = [p / probs_tot for p in probs]
            i = np.random.choice(len(self.children), p=probs)
            return self.children[i]
        else:
            return max(self.children, key=lambda node: node.v)


def puct_urgency_input(nodes):
    w = np.array([float(n.w) for n in nodes])
    v = np.array([float(n.v) for n in nodes])
    return w, v


def global_puct_urgency(n0, w, v):
    expectation = w/v
    bonus = PUCT_C * np.square(2*np.log(n0)/v)
    return expectation+bonus


def tree_descend(tree, display=False):
    tree.v += 1
    nodes = [tree]
    root = True
    while nodes[-1].children is not None and nodes[-1].children[0].pos is not int:
        if display: print_pos(nodes[-1].pos)

        children = list(nodes[-1].children)
        random.shuffle(children)
        urgencies = global_puct_urgency(nodes[-1].v, *puct_urgency_input(children))
        # if root:
        #   print()
        node = max(zip(children, urgencies), key=lambda t: t[1])[0]
        node.v += 1
        nodes.append(node)
        if node.children is None and node.v > EXPAND_VISITS:
            node.expand()

    return nodes


def score(winner, pos):
    if winner == (pos.to_play_player+2)%3:
            return 1
    else: return 0


def tree_update(nodes, winner, display=False):
    for node in reversed(nodes):
        if display: print()
        node.w += score(winner, node.pos)


def tree_search(tree, n, display=False, debug_disp=False):
    if tree.children is None:
        tree.expand()
    i = 0
    while i < n:
        nodes = tree_descend(tree, debug_disp)
        i += 1
        last_node = nodes[-1]
        if last_node.children is not None and last_node.children[0].pos is int:
            winner = last_node.children[0].pos
        else:
            winner = last_node.pos.simulate(last_node.net, a=30)
        tree_update(nodes, winner, debug_disp)
    return tree.best_move()


def print_pos(position):
    print('地主：')
    print_card(position.players_cards[0])
    print('农名1：')
    print_card(position.players_cards[1])
    print('农名2：')
    print_card(position.players_cards[2])
    print('上一张牌')
    print_card(position.game_last_card)