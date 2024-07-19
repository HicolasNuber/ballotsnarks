"""
This module provides access to branching operations.
"""
from src.groups.wiregroup import Wire


def if_then_else(condition_wire: Wire, if_wire, else_wire: Wire) -> Wire:
    """
    Evaluates *if-then-else* statements.
    
    If *condition_wire* has value :math:`1` the output wire will have the value
    of wire *if_wire*, otherwise if *condition_wire* has value :math:`0`, the
    output wire will have the value of *else_wire*.

    :param condition_wire: The condition wire. Value on the wire hast to be
        :math:`0` or :math:`1`.
    :type condition_wire: Wire
    :param if_wire: The wire containing the value in case the condition holds.
    :type if_wire: Wire
    :param else_wire: The wire containing the value in case the condition does
        not hold.
    :type else_wire: Wire
    :return: Wire that is assigned the value of *input_wire* if *condition*
        holds and the value of *else_wire* otherwise.
    :rtype: Wire
    """
    return condition_wire * if_wire + (1 - condition_wire) * else_wire


def if_then_set_zero(condition_wire: Wire, input_wire: Wire) -> Wire:
    """
    Evaluates *if-then-set-zero* statements.

    If *condition_wire* has value :math:`1` the output wire will have value
    :math:`0`, otherwise if *condition_wire* has value :math:`0`, the output
    wire will have the value of *input_wire*.

    :param input_wire: The inpute wire
    :type input_wire: Wire
    :param condition_wire: The condition wire.
    :type condition_wire: Wire
    :return: Wire that is assigned the value of *input_wire* if *condition*
        holds and :math:`0` otherwise.
    :rtype: Wire
    """
    return (1 - condition_wire) * input_wire
