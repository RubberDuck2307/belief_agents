from itertools import product

from Sentence import Sentence

class KnowledgeBase:
    def __init__(self, sentences: list[Sentence]):
        self.sentences = sentences


def check_entailment(left: Sentence, right: Sentence) -> bool:
    atoms = left.collect_atoms() | right.collect_atoms()

    for values in product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, values))
        if left.evaluate(world) and not right.evaluate(world):
            return False

    return True