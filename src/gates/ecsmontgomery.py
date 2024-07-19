"""
This module provides access to elliptic curve operations over
Montgomery curves.
"""
from typing import Tuple

import src.gates.arithmetic as arithmetic
import src.gates.bits as bitgates
import src.gates.branching as branching
import src.gates.comparison as comparison
from src.groups.group import Group
from src.groups.wiregroup import Wire


class Point():
    """
    Represents a point.
    """

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def __str__(self):
        return f'Point<x={self.x}, y={self.y}, z={self.z}>'

    @property
    def x(self) -> Wire:
        """
        Returns the x-coordinate.

        :return: x-coordinate
        :rtype: Wire
        """
        return self._x

    @x.setter
    def x(self, x: Wire) -> None:
        """
        Sets the x-coordinate.

        :param x: x-coordinate
        :type x: Wire
        """
        self._x = x

    @property
    def y(self) -> Wire:
        """
        Returns the y-coordinate.

        :return: y-coordinate
        :rtype: Wire
        """
        return self._y

    @y.setter
    def y(self, y):
        """
        Sets the y-coordinate.

        :param y: y-coordinate
        :type y: Wire
        """
        self._y = y

    @property
    def z(self) -> Wire:
        """
        Returns the z-coordinate.

        :return: z-coordinate
        :rtype: Wire
        """
        return self._z

    @z.setter
    def z(self, z):
        """
        Sets the z-coordinate.

        :param z: z-coordinate
        :type z: Wire
        """
        self._z = z


class AffinePoint(Point):
    """
    Represents an affine point. The z coordinate will either be 0
    (point at infinity) or 1 (any other point).
    """
    pass


class HomogeneousPoint(Point):
    """
    Represents an homogeneous point.
    """
    pass


def xadd(p: HomogeneousPoint, q: HomogeneousPoint, m: HomogeneousPoint) -> HomogeneousPoint:
    """
    Performs a xadd operation as defined over Montgomery curves.

    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param q: HomogeneousPoint q.
    :type q: HomogeneousPoint
    :param m: HomogeneousPoint :math:`p \ominus q`.
    :type m: HomogeneousPoint
    :return: The x-coordinate of the sum of p and q, in homogeneous
        coordinates (x, y=None, z).
    :rtype: HomogeneousPoint
    """
    v0 = p.x + p.z
    v1 = q.x - q.z
    v1 = v1 * v0
    v0 = p.x - p.z
    v2 = q.x + q.z
    v2 = v2 * v0
    v3 = v1 + v2
    v3 = v3 * v3
    v4 = v1 - v2
    v4 = v4 * v4
    xp = m.z * v3
    zp = m.x * v4
    return HomogeneousPoint(xp, None, zp)


def xdbl(p: HomogeneousPoint, A: Wire) -> HomogeneousPoint:
    """
    Performs a xdbl operation as defined over Montgomery curves.

    :param p: HomogeneousPoint p.
    :type xp: HomogeneousPoint
    :param A: Parameter of the Mongtomery curve.
    :type A: Wire
    :return: The x-coordinate of the sum of p and p, in homogeneous
        coordinates (x, y=None, z).
    :rtype: HomogeneousPoint
    """
    v1 = p.x + p.z
    v1 = v1 * v1
    v2 = p.x - p.z
    v2 = v2 * v2
    xd = v1 * v2
    v1 = v1 - v2
    v3 = ((A + 2) / 4) * v1
    v3 = v3 + v2
    zd = v1 * v3
    return HomogeneousPoint(xd, None, zd)


def ladder(k_bits: int, p: HomogeneousPoint, A: Wire) -> Tuple[HomogeneousPoint, HomogeneousPoint]:
    """
    The Montgomery ladder.

    :param k_bits: bits of k as list, MSB, first bit is assumed to be
        1.
    :type k_bits: int
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param A: curve parameter A.
    :type A: Wire
    :return: :math:`[k]\cdot P` in homogeneous coordinates: (x, None,
           z), (x+1, None, z+1)
    :rtype: Tuple[HomogeneousPoint, HomogeneousPoint]
    """
    r0 = HomogeneousPoint(p.x, None, p.z)
    r1 = xdbl(p, A)
    for i in k_bits[1:]:
        padd = xadd(r1, r0, p)
        r0_0 = xdbl(r0, A)
        r1_1 = xdbl(r1, A)

        ipaddx = i * padd.x
        ipaddz = i * padd.z
        r0.x = ipaddx + (1 - i) * r0_0.x
        r0.z = ipaddz + (1 - i) * r0_0.z
        r1.x = i * r1_1.x + padd.x - ipaddx
        r1.z = i * r1_1.z + padd.z - ipaddz

    return r0, r1


def xadd_affine(p: AffinePoint, q: AffinePoint, m: AffinePoint) -> AffinePoint:
    """
    Performs a xadd operation as defined over Montgomery curves.

    :param p: AffinePoint p.
    :type p: AffinePoint
    :param q: AffinePoint q.
    :type q: AffinePoint
    :param m: AffinePoint :math:`p \ominus q`.
    :type m: AffinePoint
    :return: The x-coordinate of the sum of p and q, in affine coordinates (x,
        y=None, z=1).
    :rtype: AffinePoint
    """
    numerator = p.x * q.x - 1
    numerator_square = numerator * numerator
    denom_paren = p.x - q.x
    denom = m.x * denom_paren * denom_paren
    x_add = arithmetic.division(numerator_square, denom)
    return AffinePoint(x_add, None, 1)


def xdbl_affine(p: AffinePoint, A: Wire) -> AffinePoint:
    """
    Performs a xdbl operation as defined over Montgomery curves.

    :param p: AffinePoint p.
    :type xp: AffinePoint
    :param A: Parameter of the Mongtomery curve.
    :type A: Wire
    :return: The x-coordinate of the sum of p and p, in affine coordinates (x,
        y=None, z=1).
    :rtype: AffinePoint
    """
    x_square = p.x * p.x
    x_squarem = x_square - 1
    x_squarem_square = x_squarem * x_squarem
    denom = 4 * p.x * (x_square + A * p.x + 1)
    x_dbl = arithmetic.division(x_squarem_square, denom)
    return AffinePoint(x_dbl, None, 1)


def ladder_affine(k_bits: int, p: AffinePoint, A: Wire) -> Tuple[AffinePoint, AffinePoint]:
    """
    The Montgomery ladder.

    :param k_bits: bits of k as list, MSB, first bit is assumed to be
        1.
    :type k_bits: int
    :param p: AffinePoint p.
    :type p: AffinePoint
    :param A: curve parameter A.
    :type A: Wire
    :return: :math:`[k]\cdot P` in affine coordinates: (x, None,
           z), (x+1, None, z+1)
    :rtype: Tuple[AffinePoint, AffinePoint]
    """
    r0 = AffinePoint(p.x, None, 1)
    r1 = xdbl_affine(p, A)
    for i in k_bits[1:]:
        padd = xadd_affine(r1, r0, p)
        r0_0 = xdbl_affine(r0, A)
        r1_1 = xdbl_affine(r1, A)
        ixpadd = i * padd.x
        r0.x = ixpadd + (1 - i) * r0_0.x
        r1.x = i * r1_1.x + padd.x - ixpadd

    return r0, r1


def okeya_sakurai_y_recovery(A: Wire, B: Wire, p: AffinePoint, q: HomogeneousPoint, pq: HomogeneousPoint) -> HomogeneousPoint:
    """
    Reconstructs the y coordinate of point q using the Okeya-Sakurai
    y-recovery algorithm.

    The function assumes that :math:`p \oplus q = (pq)`. The algorithm
    only works if :math:`q \\notin \{p, -p, O\}` where :math:`O` is
    the point at infinity.

    :param A: Curve parameter.
    :type A: Wire
    :param B: Curve parameter.
    :type B: Wire
    :param p: AffinePoint p.
    :type p: AffinePoint
    :param q: HomogeneousPoint q.
    :type q: HomogeneousPoint
    :param pq: HomogeneousPoint pq.
    :type pq: HomogeneousPoint
    :return: HomogeneousPoint (q.x, y, q.z) on the curve.
    :rtype: HomogeneousPoint
    """
    v1 = p.x * q.z
    v2 = q.x + v1
    v3 = q.x - v1
    v3 = v3 * v3
    v3 = v3 * pq.x
    v1 = 2 * A * q.z
    v2 = v2 + v1
    v4 = p.x * q.x
    v4 = v4 + q.z
    v2 = v2 * v4
    v1 = v1 * q.z
    v2 = v2 - v1
    v2 = v2 * pq.z
    y = v2 - v3
    v1 = 2 * B * p.y
    v1 = v1 * q.z
    v1 = v1 * pq.z
    x = v1 * q.x
    z = v1 * q.z
    return HomogeneousPoint(x, y, z)


def y_recovery(g: Group, A: Wire, B: Wire, p: AffinePoint, q: HomogeneousPoint, pq: HomogeneousPoint) -> HomogeneousPoint:
    """
    Recovery of the :math:`y`-coordinate based on the Okeya-Sakurai
    algorithm.

    :param g: The underlying (SNARK) group.
    :type g: Group
    :param A: Curve parameter.
    :type A: Wire
    :param B: Curve parameter.
    :type B: Wire
    :param p: Point p in affine coordinates.
    :type p: AffinePoint
    :param q: HomogeneousPoint q.
    :type q: HomogeneousPoint
    :param pq: HomogeneousPoint pq.
    :type pq: HomogeneousPoint
    :return: HomogeneousPoint of q (q.x, y, q.z).
    :rtype: HomogeneousPoint
    """
    q_recovered = okeya_sakurai_y_recovery(A, B, p, q, pq)
    # const 0 in case of x and z and const 1 in case of y.
    cond_wire = comparison.eq_zero(g, q.z)
    q_recovered.x = branching.if_then_set_zero(cond_wire, q_recovered.x)
    q_recovered.y = branching.if_then_else(cond_wire, 1, q_recovered.y)
    q_recovered.z = branching.if_then_set_zero(cond_wire, q_recovered.z)

    cond_minus_p = bitgates.and_gate(g, [comparison.eq_zero(g, pq.z), comparison.eq(g, p.x, arithmetic.division_safe(g, q.x, q.z))])
    q_recovered.x = branching.if_then_else(cond_minus_p, p.x, q_recovered.x)
    q_recovered.y = branching.if_then_else(cond_minus_p, -p.y, q_recovered.y)
    q_recovered.z = branching.if_then_else(cond_minus_p, 1, q_recovered.z)

    return q_recovered


def add_affine_points(group: Group, A: Wire, B: Wire, p: AffinePoint, q: AffinePoint) -> HomogeneousPoint:
    """
    Computes the homogeneous coordinates of the sum of the points p
    and q using the addition given by the Montgomery curve.

    :param group: The group used for the wires.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param p: AffinePoint p.
    :type p: AffinePoint
    :param q: AffinePoint q.
    :type q: AffinePoint
    :return: HomogeneousPoints (x, y, z) of point P+Q.
    :rtype: HomogeneousPoint
    """
    lambda_case_p_eq_q_numerator = 3 * p.x * p.x + 2 * A * p.x + 1
    lambda_case_p_eq_q_denomiantor = 2 * B * p.y
    lambda_case_p_eq_q = arithmetic.division_safe(group, lambda_case_p_eq_q_numerator, lambda_case_p_eq_q_denomiantor)

    lambda_case_other_numerator = q.y - p.y
    lambda_case_other_denominator = q.x - p.x
    lambda_case_other = arithmetic.division_safe(group, lambda_case_other_numerator, lambda_case_other_denominator)

    indicator_x_eq = comparison.eq(group, p.x, q.x)

    lambda_wire = branching.if_then_else(indicator_x_eq, lambda_case_p_eq_q, lambda_case_other)

    x = B * lambda_wire * lambda_wire - (p.x + q.x) - A

    indicator_p_eq_minus_q = bitgates.and_gate(group, [indicator_x_eq, comparison.eq(group, -p.y, q.y)])

    y = lambda_wire * (p.x - x) - p.y

    indicator_zero = comparison.eq_zero(group, p.x)
    indicator_zero_plus_zero = bitgates.and_gate(group, [indicator_x_eq, indicator_zero])

    indicator_point_infty = branching.if_then_else(indicator_p_eq_minus_q, 1, indicator_zero_plus_zero)

    # If point at infty hide coordinates
    x = branching.if_then_set_zero(indicator_point_infty, x)
    y = branching.if_then_else(indicator_point_infty, 1, y)

    return HomogeneousPoint(x, y, 1 - indicator_point_infty)


def add_homogeneous_points(group: Group, A: Wire, B: Wire, p: HomogeneousPoint, q: HomogeneousPoint) -> HomogeneousPoint:
    """
    Computes the x-coordinate of the sum of the points P and Q.

    :param group: The group used for the wires.
    :type group: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param q: HomogeneousPoint q.
    :type q: HomogeneousPoint
    :return: HomogeneousPoint (x, y, z) of point P+Q.
    :rtype: HomogeneousPoint
    """
    p_affine = convert_homogeneous_to_affine_coordinates(group, p)
    q_affine = convert_homogeneous_to_affine_coordinates(group, q)
    pq = add_affine_points(group, A, B, p_affine, q_affine)

    # Check if first param is the point at infinity
    indicator_first_param_infty = comparison.eq_zero(group, p.z)
    pq.x = branching.if_then_else(indicator_first_param_infty, q.x, pq.x)
    pq.y = branching.if_then_else(indicator_first_param_infty, q.y, pq.y)
    pq.z = branching.if_then_else(indicator_first_param_infty, q.z, pq.z)

    # Check if second param is the point at infinity
    indicator_second_param_infty = comparison.eq_zero(group, q.z)
    pq.x = branching.if_then_else(indicator_second_param_infty, p.x, pq.x)
    pq.y = branching.if_then_else(indicator_second_param_infty, p.y, pq.y)
    pq.z = branching.if_then_else(indicator_second_param_infty, p.z, pq.z)

    return pq


def convert_homogeneous_to_affine_coordinates(group: Group, p: HomogeneousPoint) -> AffinePoint:
    """
    Converts homogeneous coordinates to affine coordinates.

    :param group: The group used for the wires.
    :type group: Group
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :return: Affine coordinates (x, y) of the sum.
    :rtype: AffinePoint
    """
    quotients = arithmetic.division_safe_multiple(group, [p.x, p.y], p.z)
    x_affine = quotients[0]
    y_affine = quotients[1]
    indicator_infty = comparison.eq_zero(group, p.z)
    x = branching.if_then_set_zero(indicator_infty, p.x)
    y = branching.if_then_else(indicator_infty, 1, p.y)
    return AffinePoint(x_affine, y_affine, 1 - indicator_infty)


def exponent_affine_point(g: Group, A: Wire, B: Wire, p: AffinePoint, exponent: Wire) -> AffinePoint:
    """
    Computes the exponentation of an affine curve point.

    :param g: The underlying group.
    :type g: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param p: AffinePoint p.
    :type p: AffinePoint
    :param exponent: The exponent.
    :type exponent: Wire
    :return: AffinePoint of the result of the exponentation (x, y).
    :rtype: AffinePoint
    """
    exponent_bits = bitgates.split(g, exponent)

    pe0, pe1 = ladder(exponent_bits, HomogeneousPoint(p.x, None, g.gen(1)), A)
    pe = y_recovery(g, A, B, p, pe0, pe1)
    pe_affine = convert_homogeneous_to_affine_coordinates(g, pe)
    return pe_affine


def exponent_homogeneous_point_bit_exponent(g: Group, A: Wire, B: Wire, p: HomogeneousPoint, exponent_bits: Tuple[Wire]) -> HomogeneousPoint:
    """
    Computes the exponentation of an homogeneous curve point.

    :param g: The underlying group.
    :type g: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param exponent_bits: Wires of the bit representation of the exponent (MSB
        ordering).
    :type exponent: [Wire]
    :return: Wire of the exponentation (x, y, z).
    :rtype: Wire

    """
    pe0, pe1 = ladder(exponent_bits, p, A)
    pe = y_recovery(g, A, B, p, pe0, pe1)

    # check point at infinity
    indicator_infty = comparison.eq_zero(g, pe0.z)
    pe.x = branching.if_then_set_zero(indicator_infty, pe.x)
    pe.y = branching.if_then_else(indicator_infty, 1, pe.y)
    pe.z = branching.if_then_set_zero(indicator_infty, pe.z)

    # check if zero point
    indicator_zero = bitgates.and_gate(g, [comparison.eq_zero(g, p.x), comparison.eq_zero(g, p.y), (1 - comparison.eq_zero(g, p.z))])
    indicator_odd = comparison.eq_zero(g, exponent_bits[-1] - 1)
    indicator_zero_odd = indicator_zero * indicator_odd
    indicator_zero_even = indicator_zero * (1 - indicator_odd)
    pe.x = branching.if_then_else(indicator_zero_odd, 0, pe.x)
    pe.y = branching.if_then_else(indicator_zero_odd, 0, pe.y)
    pe.z = branching.if_then_else(indicator_zero_odd, 1, pe.z)
    pe.x = branching.if_then_else(indicator_zero_even, 0, pe.x)
    pe.y = branching.if_then_else(indicator_zero_even, 1, pe.y)
    pe.z = branching.if_then_else(indicator_zero_even, 0, pe.z)

    return pe

def exponent_homogeneous_point_bit_exponent_without_y_recovery(A: Wire, p: HomogeneousPoint, exponent_bits: Tuple[Wire]) -> HomogeneousPoint:
    """
    Computes the exponentation of an homogeneous curve point (no y-recovery is done here). This is only for debugging purposes.

    :param A: Montgomery curve parameter.
    :type A: Wire
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param exponent_bits: Wires of the bit representation of the exponent (MSB
        ordering).
    :type exponent: [Wire]
    :return: Homogeneous coordinates x,z of the exponentiation p^exponent_bits
    :rtype: Tuple[HomogeneousPoint]

    """
    pe0, pe1 = ladder(exponent_bits, p, A)
    return pe0,pe1


def exponent_homogeneous_point(g: Group, A: Wire, B: Wire, p: HomogeneousPoint, exponent: Wire) -> HomogeneousPoint:
    """
    Computes the exponentation of an homogeneous curve point.

    :param g: The underlying group.
    :type g: Group
    :param A: Montgomery curve parameter.
    :type A: Wire
    :param B: Montgomery curve parameter.
    :type B: Wire
    :param p: HomogeneousPoint p.
    :type p: HomogeneousPoint
    :param exponent: The exponent.
    :type exponent: Wire
    :return: Wire of the exponentation (x, y, z).
    :rtype: Wire

    """
    exponent_bits = bitgates.split(g, exponent)
    return exponent_homogeneous_point_bit_exponent(g, A, B, p, exponent_bits)
