from typing import List
from src.groups.group import Group


class Wire():
    """
    Represents a wire.
    """

    n_mul = 0
    n_wires = 0

    @classmethod
    def create(cls, value, modulus, is_const=False) -> 'Wire':
        residue = Wire()
        residue.value = value
        residue.modulus = modulus
        residue.is_const = is_const
        return residue

    def __init__(self):
        self.value = None
        self.modulus = None
        self.is_const = None

    def __int__(self):
        return self.value

    def __neg__(self):
        return Wire.create(self.modulus - int(self), self.modulus, is_const=self.is_const)

    def __repr__(self):
        return f'Wire <{self.__str__()}>'

    def __str__(self):
        return str(int(self))

    def __eq__(self, other):
        return int(self) == int(other)

    def __add__(self, other) -> 'Wire':
        is_const = self.is_const
        if isinstance(other, Wire):
            if not other.is_const:
                is_const = False
        other_val = int(other)
        s = (self.value + other_val) % self.modulus
        return Wire.create(s, self.modulus, is_const=is_const)

    def __radd__(self, other) -> 'Wire':
        return self + other

    def __sub__(self, other) -> 'Wire':
        return self + other.__neg__()

    def __rsub__(self, other) -> 'Wire':
        return other + self.__neg__()

    def __mul__(self, other) -> 'Wire':
        is_const = self.is_const
        if isinstance(other, Wire):
            if not other.is_const:
                Wire.n_mul += 1
                Wire.n_wires += 1
                is_const = False
        other_val = int(other)
        s = (self.value * other_val) % self.modulus
        return Wire.create(s, self.modulus, is_const=is_const)

    def __rmul__(self, other) -> 'Wire':
        return self * other

    def __pow__(self, other) -> 'Wire':
        other_val = int(other)
        s = (self.value ** other_val) % self.modulus
        return Wire.create(s, self.modulus)

    def __truediv__(self, other) -> 'Wire':
        try:
            other_inv = other.invert()
        except AttributeError:
            other_inv = pow(int(other), -1, self.modulus)
        return self * other_inv

    def __rtruediv__(self, other) -> 'Wire':
        return other * self.invert()

    def __floordiv__(self, other) -> 'Wire':
        return self.__truediv__(other)

    def __rfloordiv__(self, other) -> 'Wire':
        return self.__rtruediv__(other)

    def invert(self):
        if not self.is_const:
            Wire.n_mul += 1
            Wire.n_wires += 1
        inv_val = pow(self.value, -1, self.modulus)
        return Wire.create(inv_val, self.modulus, is_const=self.is_const)

class WireGroup(Group):

    def __init__(self, modulus):
        self.modulus = modulus

    @property
    def bit_length(self):
        return len(bin(self.modulus)[2:])

    def __len__(self):
        return self.modulus

    def gen(self, x: int, is_const=False) -> Wire:
        return Wire.create(x, self.modulus, is_const=is_const)

    def gen_list(self, values: List[int]) -> List['Wire']:
        """Creates a list of group elements.

        :param values: The list of values
        :type values: List[int]
        :return: A list of group elements with the given values.
        :rtype: List[Wire]
        """
        return [self.gen(v) for v in values]

    def inv(self, x) -> Wire:
        Wire = self.gen(int(x))
        return Wire.invert()
