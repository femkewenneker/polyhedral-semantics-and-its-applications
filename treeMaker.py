"""
Input: - an integer indicating the maximum amount of layers in the tree.
       - an integer indicating the maximum amount of children a node can have.
Output: a text file representing a random tree in a format that treezer.py can convert to a json file
    that can then be transformed to an input for PolyLogicA by treeToModel.py.

Femke Wenneker, June 20 2025.
"""

import random
import sys

def num_to_letters(i):
    if i == 0:
        return "(L)"
    return "[N]"


class Tree():
    def __init__(self, lvls, minnbr, maxnbr):
        self.maxLvls = lvls
        self.possibleNumOfNbrs = [0,0,0,0] + [i for i in range(minnbr, maxnbr+1)]
        self.tree = self.generate_tree()


    def generate_tree(self):
        nonleafnodes = [random.choice(self.possibleNumOfNbrs)]
        tree = [[nonleafnodes[0]]]
        while (len(tree) < self.maxLvls and len(nonleafnodes) > 0):
            new_level = [[random.choice(self.possibleNumOfNbrs) for _ in range(n)] for n in nonleafnodes]
            nonleafnodes = []
            for group in new_level:
                for node in group:
                    if node > 0: nonleafnodes.append(node)
            tree.append(new_level)
        final_level = [[0 for _ in range(n)] for n in nonleafnodes]
        tree.append(final_level)
        return tree


    def print(self):
        string = "// RANDOM TREE\n"
        tree = self.tree
        for i, level in enumerate(tree):
            if i == 0:
                string = string + "[R]\n"
                continue
            string = string + "--\nLayer {}\n".format(i)
            for group in level:
                letters = list(map(num_to_letters, group))
                string = string + ' '.join(letters) + "\n"
            string = string + "\n\n"
        print(string)


if __name__ == "__main__":
    n = len(sys.argv)
    if n != 3:
        print("Two arguments are expected: max amount of levels, and the max amount of children per node (both integers).")
    else:
        lvls = int(sys.argv[1])
        maxnbrs = int(sys.argv[2])
        tree = Tree(lvls, 2, maxnbrs)
        tree.print()

