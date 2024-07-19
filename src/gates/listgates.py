"""
This module provides access to operations over lists.
"""
from typing import List
import src.gates.comparison as comparison
from src.groups.group import Group
from src.groups.wiregroup import Wire

def get_n_occurences(group: Group, wires: List[Wire], wire: Wire) -> Wire:
    """
    Returns how often the value on the wire occurs in the list.

    :param group: The underlying group
    :type group: Group
    :param wires: List of wires
    :type wires: List[Wire]
    :param wire: The wire with the value to find in the list
    :type wire: Wire
    :return: Returns how many wires in the list have the same value as
        the given wire.
    :rtype: Wire
    """
    n_occurences = group.gen(0)
    for wire_in_list in wires:
        ind_eq = comparison.eq(group, wire_in_list, wire)
        n_occurences += ind_eq
    return n_occurences
