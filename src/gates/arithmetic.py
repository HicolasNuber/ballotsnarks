"""
This module provides access to arithmetic operations on wires.
"""
from typing import List, Tuple
import src.gates.branching as branching
import src.gates.comparison as comparison
from src.groups.group import Group
from src.groups.wiregroup import Wire


def division(dividend: Wire, divisor: Wire) -> Wire:
    """
    Computes the quotient of given parameters.

    This function is unsafe, that is, if the divisor is zero, a
    ValueError will be raised.

    :param dividend: The dividend of the division.
    :type dividend: Wire
    :param divisor: The divisor of the division.
    :type divisor: Wire
    :raises ValueError: Raised if divisor is zero.
    :return: Quotient: *dividend* / *divisor*
    :rtype: Wire
    """
    if int(divisor) == 0:
        raise ValueError('Divisor is zero.')
    return dividend * divisor.invert()


def division_safe(group: Group, divididend: Wire, divisor: Wire) -> Wire:
    """
    Computes the quotient of given parameters in a safe way.

    That is, if the divisor is zero, the function will not raise an exception
    but rather output *some* value. When calling this function one has to take
    care of this behavior accordingly.

    :param group: The group used for the wires.
    :type group: Group
    :param dividend: The dividend of the division.
    :type dividend: Wire
    :param divisor: The divisor of the division.
    :type divisor: Wire
    :return: Quotient: *dividend* / *divisor*
    :rtype: Wire
    """
    condition_wire = comparison.eq_zero(group, divisor)
    divisor_safe = branching.if_then_else(condition_wire, 1, divisor)
    return division(divididend, divisor_safe)


def division_safe_multiple(group: Group, divididends: List[Wire], divisor: Wire) -> List[Wire]:
    """
    Computes the quotient of given parameters in a safe way for each
    dividend.

    That is, if the divisor is zero, the function will not raise an
    exception but rather output *some* value. When calling this
    function one has to take care of this behavior accordingly.

    :param group: The group used for the wires.
    :type group: Group
    :param dividends: The list of dividends of the division.
    :type dividends: List[Wire]
    :param divisor: The divisor of the division.
    :type divisor: Wire
    :return: Quotient: *dividend* / *divisor* for each dividend.
    :rtype: List[Wire]
    """
    condition_wire = comparison.eq_zero(group, divisor)
    divisor_safe = branching.if_then_else(condition_wire, 1, divisor)
    results = []
    for dividend in divididends:
        results.append(division(dividend, divisor_safe))
    return results


def r1cs_constraint_single_output(group: Group, wires_a: List[Tuple[int, Wire]], wires_b: List[Tuple[int, Wire]]) -> Wire:
    """
    Evaluates a single R1CS constraint with one output wire.


    :param group: The group used for the wires.
    :type group: Group
    :param wires_a: Wire set a (with factors).
    :type wires_a: List[Tuple[int, Wire]]
    :param wires_b: Wire set b (with factors).
    :type wires_b: List[Tuple[int, Wire]]
    :return: The result of the multiplication.
    :rtype: Wire
    """
    value_a = group.gen(0, is_const=True)
    for factor, value in wires_a:
        value_a += factor * value.value
    value_b = group.gen(0, is_const=True)
    for factor, value in wires_b:
        value_b += factor * value.value
    value_result = value_a * value_b
    value_result.is_const = False
    Wire.n_mul += 1
    return value_result
