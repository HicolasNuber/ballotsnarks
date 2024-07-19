"""
This module provides access to comparison operations on wires.
"""
from typing import List

import src.gates.assertgates as assertgates
import src.gates.bits as bitgates
from src.groups.group import Group
from src.groups.wiregroup import Wire


def eq(group: Group, wire_one: Wire, wire_two: Wire) -> Wire:
    """
    Checks the equality of the values on the wires.

    The function outputs a wire with value 1 if the input wires have
    the same value, and a wire with value 0 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: One of the wires to compare to the other.
    :type wire_one: Wire
    :param wire_two: One of the wires to compare to the other.
    :type wire_two: Wire
    :return: Wire with value one if the two input wires have equal
        value, and wire with value 0 otherwise.
    :rtype: Wire
    """
    return eq_zero(group, wire_one - wire_two)


def eq_multiple(group: Group, wires_one: List[Wire], wires_two: List[Wire]) -> Wire:
    """
    Checks the equality of the sum of the values on the wires in the
    two sets.

    The function outputs a wire with value 1 if the input sets of wires
    have the same sum of value, and a wire with value 0 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wires_one: One of the set of wires to compare to the other.
    :type wires_one: List[Wire]
    :param wires_two: One of the set of wires to compare to the other.
    :type wires_two: List[Wire]
    :return: Wire with value one if the two input sets of wires have
        equal value, and wire with value 0 otherwise.
    :rtype: Wire
    """
    wires = [w for w in wires_one]
    wires += [-w for w in wires_two]
    return eq_zero_multiple(group, wires)


def eq_zero(group: Group, wire: Wire) -> Wire:
    """
    Checks whether the value of the wire is zero.

    The function outputs a wire with value 1 if the value of the input
    wire is 0, and a wire with value 1 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wire: Wire to compare the value to zero.
    :type wire: Wire
    :return: Wire with value one if the input input wire has value 0,
        and wire with value 0 otherwise.
    :rtype: Wire
    """
    if int(wire) == 0:
        helper_wire = group.gen(0)
        result_wire = group.gen(1)
    else:
        helper_wire = group.gen(pow(int(wire), -1, wire.modulus))
        result_wire = group.gen(0)
    assertgates.assert_equal(group, [result_wire * wire], [group.gen(0)])
    assertgates.assert_equal(group, [wire * helper_wire], [1 - result_wire])
    return result_wire


def eq_zero_multiple(group: Group, wires: List[Wire]) -> Wire:
    """
    Checks whether the sum of the value of the input wires is zero.

    The function outputs a wire with value 1 if the sum of the values
    of the input wires is 0, and a wire with value 1 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wires: Wires to compare the sum of the values to zero.
    :type wires: List[Wire]
    :return: Wire with value one if the input input wire has value 0,
        and wire with value 0 otherwise.
    :rtype: Wire
    """
    sum_value = sum(wires).value
    if sum_value == 0:
        helper_wire = group.gen(0)
        result_wire = group.gen(1)
    else:
        helper_wire = group.gen(pow(sum_value, -1, group.modulus))
        result_wire = group.gen(0)
    assertgates.assert_equal(group, [result_wire * sum_value], [group.gen(0)])
    assertgates.assert_equal(group, [sum_value * helper_wire], [1 - result_wire])
    return result_wire


def gt(group: Group, wire_one: Wire, wire_two: Wire, bits: int) -> Wire:
    """
    Checks whether the first wire is greater (or equal) than the
    second one.

    The function outputs a wire with value 1 if wire_one >= wire_two,
    and a wire with value 0 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: One of the wires to compare to the other.
    :type wire_one: Wire
    :param wire_two: One of the wires to compare to the other.
    :type wire_two: Wire
    :param bits: The maximum number of bits of the two input wires.
        This number needs to be lower than halve of the maximum bit
        size of the group, otherwise the gate is insecure.
    :type bits: int
    :raises ValueError: Raised if bit size is too large (greater or
        equal halve of the maximum bit size of the group).
    :return: Wire with value 1 if wire_one >= wire_two, and a wire
        with value 0 otherwise.
    :rtype: Wire
    """
    max_bits_allowed = group.bit_length // 2
    if bits > max_bits_allowed:
        raise ValueError(f'Value of bits ({bits}) is too large (must be at most {max_bits_allowed})')

    diff_wire = wire_one - wire_two

    if int(wire_one) >= int(wire_two):
        value_res_wire = 1
        value_b_wire = int(diff_wire)
    else:
        value_res_wire = 0
        value_b_wire = group.modulus - int(diff_wire) - 1

    wire_res = group.gen(value_res_wire)
    wire_b = group.gen(value_b_wire)

    bitgates.split(group, wire_b, bits)
    assertgates.assert_bit(wire_res)
    assertgates.assert_equal(group, [2 * wire_res * diff_wire], [diff_wire + wire_b + 1 - wire_res])

    return wire_res


def lt(group: Group, wire_one: Wire, wire_two: Wire, bits: int) -> Wire:
    """
    Checks whether the first wire is less (or equal) than the second
    one.

    The function outputs a wire with value 1 if wire_one <= wire_two,
    and a wire with value 0 otherwise.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: One of the wires to compare to the other.
    :type wire_one: Wire
    :param wire_two: One of the wires to compare to the other.
    :type wire_two: Wire
    :param bits: The maximum number of bits of the two input wires.
        This number needs to be lower than halve of the maximum bit
        size of the group, otherwise the gate is insecure.
    :type bits: int
    :raises ValueError: Raised if bit size is too large (greater or
        equal halve of the maximum bit size of the group).
    :return: Wire with value 1 if wire_one <= wire_two, and a wire
        with value 0 otherwise.
    :rtype: Wire
    """
    return gt(group, wire_two, wire_one, bits)
