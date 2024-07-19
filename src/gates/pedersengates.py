"""
This module provides access to Pedersen commitments.
"""
from typing import List, Tuple

import src.gates.bits as bitgates
import src.gates.ecsmontgomery as montgomery
from src.groups.group import Group
from src.groups.wiregroup import Wire


def pedersen_commitment_over_montgomery_curve_bit_randomness(group: Group, A: Wire, B: Wire, g: montgomery.HomogeneousPoint, h: montgomery.HomogeneousPoint, m: Wire, r_bits: Tuple[Wire], n_max_bits_m: int = None) -> montgomery.HomogeneousPoint:
    """
    Computes a Pedersen commitment over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: HomogeneousPoint g.
    :type g: HomogeneousPoint
    :param h: HomogeneousPoint h.
    :type h: HomogeneousPoint
    :param m: Value to commit to.
    :type m: Wire
    :param r_bits: Randomness of the commitment in binary
        representation (MSB ordering).
    :param n_max_bits_m: Max bit size of the message m (default: group
        size).
    :type n_max_bits_m: int
    :type r_bits: [Wire]
    :return: Commitment of m with randomness r in homogeneous
        coordinates (x, y, z).
    :rtype: HomogeneousPoint
    """
    m_bits = bitgates.split(group, m, bit_length=n_max_bits_m)
    gm = montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, g, m_bits)
    hr = montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, h, r_bits)

    c = montgomery.add_homogeneous_points(group, A, B, gm, hr)
    return c


def pedersen_commitment_over_montgomery_curve(group: Group, A: Wire, B: Wire, g: montgomery.HomogeneousPoint, h: montgomery.HomogeneousPoint, m: Wire, r: Wire) -> montgomery.HomogeneousPoint:
    """
    Computes a Pedersen commitment over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: HomogeneousPoint g.
    :type g: HomogeneousPoint
    :param h: HomogeneousPoint h.
    :type h: HomogeneousPoint
    :param m: Value to commit to.
    :type m: Wire
    :param r: Randomness of the commitment
    :type r: Wire
    :return: Commitment of m with randomness r in homogeneous coordinates (x, y,
        z).
    :rtype: HomogeneousPoint
    """
    gm = montgomery.exponent_homogeneous_point(group, A, B, g, m)
    hr = montgomery.exponent_homogeneous_point(group, A, B, h, r)

    c = montgomery.add_homogeneous_points(group, A, B, gm, hr)
    return c


def vector_pedersen_commitment_over_montgomery_curve_bit_randomness(group: Group, A: Wire, B: Wire, gs: List[montgomery.HomogeneousPoint], h: montgomery.HomogeneousPoint, ms: List[Wire], r_bits: Tuple[Wire], n_max_bits_m: int = None) -> montgomery.HomogeneousPoint:
    """
    Computes a Pedersen commitment over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: List of HomogeneousPoint g.
    :type g: List[HomogeneousPoint]
    :param h: HomogeneousPoint h.
    :type h: HomogeneousPoint
    :param m: Values to commit to.
    :type m: List[Wire]
    :param r_bits: Randomness of the commitment in binary
        representation (MSB ordering).
    :type r_bits: [Wire]
    :param n_max_bits_m: Max bit size of the message m (default: group
        size).
    :type n_max_bits_m: int
    :return: Commitment of ms with randomness r in homogeneous
        coordinates (x, y, z).
    :rtype: HomogeneousPoint
    """
    m_bitss = [bitgates.split(group, m, bit_length=n_max_bits_m) for m in ms]
    gms = [montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, g, m_bits) for g, m_bits in zip(gs, m_bitss)]
    hr = montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, h, r_bits)

    point_sum = hr
    for gm in gms:
        point_sum = montgomery.add_homogeneous_points(group, A, B, gm, point_sum)

    return point_sum


def vector_pedersen_commitment_over_montgomery_curve(group: Group, A: Wire, B: Wire, gs: List[montgomery.HomogeneousPoint], h: montgomery.HomogeneousPoint, ms: List[Wire], r: Wire, n_max_bits_m: int = None) -> montgomery.HomogeneousPoint:
    """
    Computes a Pedersen commitment over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: List of HomogeneousPoint g.
    :type g: List[HomogeneousPoint]
    :param h: HomogeneousPoint h.
    :type h: HomogeneousPoint
    :param m: Values to commit to.
    :type m: List[Wire]
    :param r: Randomness of the commitment
    :type r: Wire
    :return: Commitment of ms with randomness r in homogeneous
        coordinates (x, y, z).
    :rtype: HomogeneousPoint
    """
    gms = [montgomery.exponent_homogeneous_point(group, A, B, g, m) for g, m in zip(gs, ms)]
    hr = montgomery.exponent_homogeneous_point(group, A, B, h, r)

    point_sum = hr
    for gm in gms:
        point_sum = montgomery.add_homogeneous_points(group, A, B, gm, point_sum)

    return point_sum
