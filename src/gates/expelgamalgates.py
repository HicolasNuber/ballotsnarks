"""
This module provides access to exponential ElGamal Encryption.
"""
from typing import List, Tuple

import src.gates.bits as bitgates
import src.gates.ecsmontgomery as montgomery
from src.groups.group import Group
from src.groups.wiregroup import Wire

def exponential_elgamal_over_montgomery_curve_bit_randomness(group: Group, A: Wire, B: Wire, g: montgomery.HomogeneousPoint, pk: montgomery.HomogeneousPoint, x: Wire, r_bits: Tuple[Wire], n_max_bits_x: int = None) -> tuple[montgomery.HomogeneousPoint]:
    """
    Computes an exponential ElGamal ciphertext over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: HomogeneousPoint g.
    :type g: HomogeneousPoint
    :param pk: public key.
    :type pk: HomogeneousPoint
    :param x: Value to commit to.
    :type x: Wire
    :param r_bits: Randomness of the encryption in binary
        representation (MSB ordering).
    :param n_max_bits_x: Max bit size of the plaintext x (default: group
        size).
    :type n_max_bits_x: int
    :type r_bits: [Wire]
    :return: ciphertext encrypting x with randomness r, both entries in homogeneous coordinates (x, y,
        z).
    :rtype: HomogeneousPoint
    """
    x_bits = bitgates.split(group, x, bit_length=n_max_bits_x)
    gx = montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, g, x_bits)
    pkr = montgomery.exponent_homogeneous_point_bit_exponent(group, A, B, pk, r_bits)
    gr = montgomery.exponent_homogeneous_point_bit_exponent(group,A,B,g,r_bits)
    c = (gr,montgomery.add_homogeneous_points(group, A, B, gx, pkr))
    return c

def exponential_elgamal_over_montgomery_curve(group: Group, A: Wire, B: Wire, g: montgomery.HomogeneousPoint, pk: montgomery.HomogeneousPoint, x: Wire, r: Wire) -> tuple[montgomery.HomogeneousPoint,montgomery.HomogeneousPoint]:
    """
    Computes an exponential ElGamal ciphertext over a Montgomery curve.

    :param group: The underlying group.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param g: HomogeneousPoint g.
    :type g: HomogeneousPoint
    :param pk: public key.
    :type pk: HomogeneousPoint
    :param x: Plaintext
    :type x: Wire
    :param r: Randomness of the encryption
    :type r: Wire
    :return: ciphertext encrypting x with randomness r, both entries in homogeneous coordinates (x, y,
        z).
    :rtype: tuple[HomogeneousPoint, HomogeneousPoint]
    """
    gx = montgomery.exponent_homogeneous_point(group, A, B, g, x)
    pkr = montgomery.exponent_homogeneous_point(group, A, B, pk, r)
    gr = montgomery.exponent_homogeneous_point(group,A,B,g,r)
    c = (gr,montgomery.add_homogeneous_points(group, A, B, gx, pkr))
    return c
