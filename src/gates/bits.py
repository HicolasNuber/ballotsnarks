"""
This module provides access to bit operations on wires.
"""
import logging
from typing import List

import src.gates.assertgates as assertgates
import src.gates.comparison as comparison
from src.groups.group import Group
from src.groups.wiregroup import Wire

log = logging.getLogger(__name__)


def split(group: Group, wire: Wire, bit_length: int = None) -> List[Wire]:
    """
    Splits the value on the wire into bits (MSB ordering).

    The function computes a list of wires containing the bit
    representation of the input wire. The ordering of the list in
    big-endian, that is the least significant bit is the last element
    in the list.

    :param group: The group used for the wires.
    :type group: Group
    :param wire: To wire to be split in binary representation.
    :type wire: Wire
    :param bit_length: The maximum bit length of the wire. This will
        determine the length of the output list. If no bit_length is
        given, the bit length of the group is used.
    :type bit_length: int
    :return: List of wires representing the value of the wire in
        binary (big-endian representation).
    :rtype: List[Wire]
    """
    if bit_length is None:
        bit_length = group.bit_length
    input_val = int(wire)
    bits = bin(input_val)[2:].zfill(bit_length)
    bit_values_sum = 0
    two_exp = 1
    for bit in reversed(bits):
        if bit == '1':
            bit_values_sum += two_exp
        two_exp *= 2
    bit_wires = [group.gen(int(bit)) for bit in bits]
    assertgates.assert_equal(group, [bit_values_sum], [wire])
    for bit_wire in bit_wires:
        assertgates.assert_bit(bit_wire)
    return bit_wires


def verify_bit(group: Group, wire: Wire) -> Wire:
    """
    Verifies that the value of the wire is binary.

    The function ensure that the value of the given wire is 0 or 1.

    :param group: The underlying group
    :type group: Group
    :param wire: The wire with expected binary value.
    :type wire: Wire
    :return: A wire with value 1 if the input wire is of binary value.
        Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    mul_wire = wire * (1 - wire)
    return comparison.eq_zero(group, mul_wire)


def and_gate(group: Group, wires: List[Wire]) -> Wire:
    """Evaluates an AND gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary.

    :param group: The group used for the wires.
    :type group: Group
    :param wires: List of the input wires
    :type wires: List[Wire]
    :return: A wire with value 1 if all input wires are of value 1.
        Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    if len(wires) == 2:
        return and_gate_two_inputs(group, *wires)
    return and_gate_multiple_inputs(group, wires)


def and_gate_two_inputs(group: Group, wire_one: Wire, wire_two: Wire) -> Wire:
    """Evaluates an AND gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: Input wire one.
    :type wire_one: Wire
    :param wire_two: Input wire one.
    :type wire_two: Wire
    :return: A wire with value 1 if both input wires are of value 1.
        Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    if wire_one.value not in [0, 1]:
        log.warning('Warning: Value of input wire_one is not binary.')
    if wire_two.value not in [0, 1]:
        log.warning('Warning: Value of input wire_two is not binary.')
    return wire_one * wire_two


def and_gate_multiple_inputs(group: Group, wires: List[Wire]) -> Wire:
    """Evaluates an AND gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary.

    :param group: The group used for the wires.
    :type group: Group
    :param wires: List of the input wires
    :type wires: List[Wire]
    :return: A wire with value 1 if all input wires are of value 1.
        Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    for wire in wires:
        if wire.value not in [0, 1]:
            log.warning('Warning: Value of an input wire is not binary.')
    sum_wire = group.gen(len(wires), is_const=True)
    return comparison.eq_multiple(group, wires, [sum_wire])


def or_gate(group: Group, wires: List[Wire]) -> Wire:
    """Evaluates an OR gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary or if there are as many input wires as the size of the
    group.

    :param group: The group used for the wires.
    :type group: Group
    :param wires: List of the input wires
    :type wires: List[Wire]
    :return: A wire with value 1 if at least one of the input wires is
        of value 1. Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    if len(wires) == 2:
        return or_gate_two_inputs(group, *wires)
    return or_gate_multiple_inputs(group, wires)


def or_gate_two_inputs(group: Group, wire_one: Wire, wire_two: Wire) -> Wire:
    """Evaluates an AND gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary or if there are as many input wires as the size of the
    group.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: Input wire one.
    :type wire_one: Wire
    :param wire_two: Input wire one.
    :type wire_two: Wire
    :return: A wire with value 1 if at least one of the input wires is
        of value 1. Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    if wire_one.value not in [0, 1]:
        log.warning('Warning: Value of input wire_one is not binary.')
    if wire_two.value not in [0, 1]:
        log.warning('Warning: Value of input wire_two is not binary.')
    return wire_one + wire_two - wire_one * wire_two


def or_gate_multiple_inputs(group: Group, wires: List[Wire]) -> Wire:
    """Evaluates an OR gate on the input wires.

    Warning: The output might be incorrect if the input wires are not binary or
    if there are as many input wires as the size of the group.

    :param group: The group used for the wires.
    :type group: Group
    :param wires: List of the input wires
    :type wires: List[Wire]
    :return: A wire with value 1 if at least one of the input wires int of value
        1. Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    for wire in wires:
        if wire.value not in [0, 1]:
            log.warning('Warning: Value of an input wire is not binary.')
    try:
        if len(wires) >= len(group):
                log.warning('Warning: Number of input wires is too large.')
    except OverflowError:
        if len(wires) >= 2**32-1:
                log.warning('Warning: Number of input wires is too large.')
    return 1 - comparison.eq_zero_multiple(group, wires)


def xor_gate_two_inputs(group: Group, wire_one: Wire, wire_two: Wire) -> Wire:
    """Evaluates an XOR gate on the input wires.

    Warning: The output might be incorrect if the input wires are not
    binary.

    :param group: The group used for the wires.
    :type group: Group
    :param wire_one: Input wire one.
    :type wire_one: Wire
    :param wire_two: Input wire one.
    :type wire_two: Wire
    :return: A wire with value 1 if all input wires are of value 1.
        Otherwise, the wire will have value 0.
    :rtype: Wire
    """
    if wire_one.value not in [0, 1]:
        log.warning('Warning: Value of input wire_one is not binary.')
    if wire_two.value not in [0, 1]:
        log.warning('Warning: Value of input wire_two is not binary.')
    or_val = or_gate(group, [wire_one, wire_two])
    and_val = and_gate(group, [wire_one, wire_two])
    return and_gate(group, [or_val, 1 - and_val])
