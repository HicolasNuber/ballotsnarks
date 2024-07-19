"""
This module provides access to assert operations on wires.

Assert operations ensure that certain properties hold. That is, if the wires do not satisfy the assertion, the circuit
cannot be verified.
"""
from typing import List

import src.gates.bits as bitgates
from src.groups.group import Group
from src.groups.wiregroup import Wire


def assert_equal(group: Group, wires_one: List[Wire], wires_two: List[Wire]) -> None:
    """
    Asserts that the values of two sets of wires are equal.

    The function will compute the sum of each set of wires and compares whether
    the sums are equal.

    :param group: The group used for the wires.
    :type group: Group
    :param wires_one: Set of wires.
    :type wires_one: List[Wire]
    :param wires_two: Set of wires.
    :type wires_two: List[Wire]
    :raises ValueError: Raised if the sums of the two sets are not equal.
    """
    wires_a_sum = sum(wires_one) * group.gen(1)
    wires_b_sum = sum(wires_two)
    if int(wires_a_sum) != int(wires_b_sum):
        raise ValueError('Equality does not hold.')


def assert_bit(wire: Wire) -> None:
    """
    Asserts that the value of the wire is binary.

    The function ensure that the value of the given wire is 0 or 1.

    :param wire: The wire with expected binary value.
    :type wire: Wire
    :raises ValueError: Raised if the value of the wire is not 0 or 1.
    """
    res_wire = wire * (1 - wire)
    if int(res_wire) != 0:
        raise ValueError('Value of the wire is not a bit.')


def assert_one_zero_minus_one(wire: Wire) -> None:
    """
    Asserts that the value on the wire is -1 or 0 or 1.

    :param wire: The wire with the expected value.
    :type wire: Wire
    :raises ValueError: Raised if the value of the wire is not 0 or 1
        or -1.
    """
    y = wire * (wire - 1)
    res = y * (wire + 1)
    if int(res) != 0:
        raise ValueError('Value of the wire is not in correct range.')


def assert_gt(group: Group, wire_one: Wire, wire_two: Wire, bits: int) -> None:
    """
    Asserts that the value of the first wire is greater than (or equal) to the
    value of the second wire.

    :param wire_one: Wire to be expected greater than (or equal) the second
        wire.
    :type wire_one: Wire
    :param wire_two: Wire with expected smaller value.
    :type wire_two: Wire
    :param bits: The maximum number of bits of the two input wires. This number
        needs to be lower than halve of the maximum bit size of the group,
        otherwise the gate is insecure.
    :type bits: int
    :raises ValueError: Raised if the value of the first wire is not greater
        than (or equal) the value of the second wire. Or if bit size is too
        large (greater or equal halve of the maximum bit size of the group).
    """
    max_bits_allowed = group.bit_length // 2
    if bits > max_bits_allowed:
        raise ValueError(f'Value of bits ({bits}) is too large (must be at most {max_bits_allowed})')

    diff_wire = wire_one - wire_two

    if int(wire_one) >= int(wire_two):
        value_b_wire = int(diff_wire)
    else:
        raise ValueError('Value of the first wire is not greater than (or equal) the value of the second wire.')

    wire_b = group.gen(value_b_wire)

    bitgates.split(group, wire_b, bits)
    assert_equal(group, [2 * diff_wire], [diff_wire + wire_b])
