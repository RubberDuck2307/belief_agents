from typing import Dict, Tuple

from DataStructure import LiteralStore

class Sentence:
    def evaluate(self, world: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def collect_atoms(self) -> set[str]:
        raise NotImplementedError

    def to_cnf(self):
        return self.eliminate_implications().push_not().distribute()

    def eliminate_implications(self):
        raise NotImplementedError

    def push_not(self):
        raise NotImplementedError

    def distribute(self):
        raise NotImplementedError

    def is_literal(self):
        return False

    def collect_literals(self, literal_store: LiteralStore):
        raise NotImplementedError

    def check_value(self, literal: str, is_true: bool) -> bool:
        raise NotImplementedError


    def __repr__(self) -> str:
        raise NotImplementedError


class Atom(Sentence):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return world[self.name]

    def collect_atoms(self) -> set[str]:
        return {self.name}

    def get_literal_value(self) -> Tuple[str, bool]:
        return self.name, True

    def eliminate_implications(self):
        return self

    def push_not(self):
        return self

    def distribute(self):
        return self

    def is_literal(self):
        return True

    def collect_literals(self, literal_store: LiteralStore):
        literal_store.add(self.name, True)

    def check_value(self, literal: str, is_true: bool) -> bool:
        return self.name == literal and is_true

    def __repr__(self) -> str:
        return self.name


class Not(Sentence):
    def __init__(self, child: Sentence):
        self.child = child

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return not self.child.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.child.collect_atoms()

    def get_literal_value(self) -> Tuple[str, bool]:
        if isinstance(self.child, Atom):
            return self.child.name, False
        raise ValueError("Not is not literal")

    def eliminate_implications(self):
        return Not(self.child.eliminate_implications())

    def push_not(self):
        c = self.child
        if isinstance(c, Atom):
            return self
        if isinstance(c, Not):
            return c.child.push_not()
        if isinstance(c, And):
            return Or(Not(c.left).push_not(), Not(c.right).push_not())
        if isinstance(c, Or):
            return And(Not(c.left).push_not(), Not(c.right).push_not())
        return Not(c.push_not())

    def distribute(self):
        return self

    def is_literal(self):
        return isinstance(self.child, Atom)

    def collect_literals(self, literal_store: LiteralStore):
        if isinstance(self.child, Atom):
            literal_store.add(self.child.name, False)
        else:
            raise ValueError("Not is still not literal after push_not")

    def check_value(self, literal: str, is_true: bool) -> bool:
        return isinstance(self.child, Atom) and self.child.name == literal and not is_true

    def __repr__(self) -> str:
        return f"¬({self.child})"


class And(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) and self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        return And(self.left.eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        return And(self.left.push_not(), self.right.push_not())

    def distribute(self):
        return And(self.left.distribute(), self.right.distribute())

    def add_clause(self, sentence):
        return And(self, sentence)

    def collect_literals(self, literal_store: LiteralStore):
        self.left.collect_literals(literal_store)
        self.right.collect_literals(literal_store)

    def __repr__(self) -> str:
        return f"({self.left} ∧ {self.right})"


class Or(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) or self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        return Or(self.left.eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        return Or(self.left.push_not(), self.right.push_not())

    def distribute(self):
        l = self.left.distribute()
        r = self.right.distribute()

        if isinstance(l, And):
            return And(Or(l.left, r).distribute(), Or(l.right, r).distribute())
        if isinstance(r, And):
            return And(Or(l, r.left).distribute(), Or(l, r.right).distribute())
        return Or(l, r)

    def collect_literals(self, literal_store: LiteralStore):
        self.left.collect_literals(literal_store)
        self.right.collect_literals(literal_store)

    def __repr__(self) -> str:
        return f"({self.left} ∨ {self.right})"


class Implies(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return (not self.left.evaluate(world)) or self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        return Or(Not(self.left).eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        return self.eliminate_implications().push_not()

    def distribute(self):
        return self.push_not().distribute()

    def __repr__(self) -> str:
        return f"({self.left} → {self.right})"


class Biconditional(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) == self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        a = self.left
        b = self.right
        return And(Implies(a, b).eliminate_implications(),
                   Implies(b, a).eliminate_implications())

    def push_not(self):
        return self.eliminate_implications().push_not()

    def distribute(self):
        return self.push_not().distribute()

    def __repr__(self) -> str:
        return f"({self.left} ↔ {self.right})"