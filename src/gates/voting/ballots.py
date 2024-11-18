"""
Contains evaluation functions for ballot relations.
"""
import itertools
from typing import List

import src.gates.assertgates as assertgates
import src.gates.bits as bitgates
import src.gates.comparison as comparison
import src.gates.listgates as listgates
from src.groups.group import Group
from src.groups.wiregroup import Wire


def assert_single_vote(group: Group, ballot: List[Wire]) -> None:
    """
    Asserts that each entry is binary and that exactly one one occurs.

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[Wire]
    :raises ValueError: Raised if the ballot does not verify.
    """
    for wire in ballot:
        assertgates.assert_bit(wire)
    assertgates.assert_equal(group, ballot, [group.gen(1)])

def assert_multi_vote(group: Group, ballot: List[Wire], max_choices: Wire = None, bits: int = 1, max_votes_per_candidate: Wire = None, totalbits: int = None) -> None:
    """
    Asserts that each entry is at most max_votes_per_candidate and that the sum of all entries is at most max_choices. Bits should be at least log(max_votes_per_candidates*num_cand).

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[Wire]
    :param max_choices: maximum number of total choices, defaults to
        None (arbitrary number of total choices allowed)
    :type max_choices: int, optional
    :param bits: Maximum bit size of the entries in the ballot,
        defaults to 1.
    :type bits: int, optional
    :param max_votes_per_candidate: maximum number of votes per candidate, defaults to
        None (only 0 or 1 vote per candidate). Should not be large than 2^bits-1
    :type max_votes_per_candidate: int, optional
    :param totalbits: Maximum bit size of the sum of the ballot entries len(ballot)=numcand.
    :type bits: int, optional
    :raises ValueError: Raised if the ballot does not verify.
    """
    if max_votes_per_candidate is None:
        max_votes_per_candidate=group.gen(1)
    
    if totalbits is None:
        totalbits = len(ballot)

    for wire in ballot:
        assertgates.assert_gt(group,max_votes_per_candidate,wire,bits)
    
    if max_choices is not None:
        n_choices = sum(ballot)
        assertgates.assert_gt(group, max_choices, n_choices, totalbits)

def assert_multi_vote_with_rules(group: Group, ballot: List[Wire], max_choices: Wire = None, bits: int = 1, max_votes_per_candidate: Wire = None, totalbits: int = None) ->None:

    """
    Asserts that each entry is at most max_votes_per_candidate, that the sum of all entries is at most max_choices, and that the product of the second and the third ballot entry equals the first ballot entry. 

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[Wire]
    :param max_choices: maximum number of possibles ones, defaults to
        None (arbitrary number of ones allowed)
    :type max_choices: int, optional
    :param bits: Maximum bit size of the entries in the ballot,
        defaults to 1
    :type bits: int, optional
    :param max_votes_per_candidate: maximum number of votes per candidate, defaults to
        None (only 0 or 1 vote per candidate)
    :type max_votes_per_candidate: int, optional
    :param totalbits: Maximum bit size of the sum of the ballot entries len(ballot)=numcand.
    :type bits: int, optional
    :raises ValueError: Raised if the ballot does not verify.
    """
    assert_multi_vote(group,ballot,max_choices,bits,max_votes_per_candidate,totalbits)
    if len(ballot)>2:
        assertgates.assert_equal(group,[ballot[1]*ballot[2]],[ballot[0]])

def assert_line_vote_ballot(group: Group, ballot: List[Wire]) ->None:
    """
    Asserts a line vote ballot, i.e., a ballot with 1 or 0 votes
    for each candidate, where all 1-votes have to be assigned successively.
    A ballot consisting of only zeros is considered valid.

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[Wire]
    :raises ValueError: Raised if the ballot does not verify.
    """
    assertgates.assert_bit(ballot[0])
    indicator_bit_up=ballot[0]
    for idx in range(len(ballot)-1):
        assertgates.assert_bit(ballot[idx+1])
        indicator_bit_up+=(ballot[idx+1]-ballot[idx])*ballot[idx+1]
    assertgates.assert_bit(indicator_bit_up)


def assert_pointlist_borda_ballot(group: Group, ballot: List[Wire], ordered_points: List[Wire]) -> None:
    """
    Asserts a Borda ballot.  If n_cand>n_points, we assume that n_points is padded with (n_cand-n_points) zeros.

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[Wire]
    :param ordered_points: Ordered list of Borda points (descending), should be of same length als ballot, should not contain 0.
    :type ordered_points: List[Wire]
    :raises ValueError: Raised if the ballot does not verify.
    """
    expected_zeros=group.gen(len(ballot)-len(ordered_points))
    num_zeros=listgates.get_n_occurences(group,ballot,group.gen(0))
    assertgates.assert_equal(group,[expected_zeros],[num_zeros])
    for point in ordered_points:
        n_occ = listgates.get_n_occurences(group,ballot,point)
        assertgates.assert_equal(group,[n_occ],[group.gen(1)])

def compute_borda_tournament_style_ballot(group: Group, ranking: List[Wire], bits: int) -> List[Wire]:
    """
    Computes the BWT points based on the ranking of
    the choices.

    Important: Zero is interpreted as the highest rank.

    :param group: The underlying group
    :type group: Group
    :param ranking: Ranking of the choice. Greater value means higher
        rank
    :type ranking: List[Wire]
    :param bits: Maximum bit size of the entries in the ballot
    :type bits: int
    :return: List of points per choice
    :rtype: List[Wire]
    """
    points = []
    for i, ranking_val in enumerate(ranking):
        n_truely_greater = sum([comparison.gt(group, ranking_val - 1, comp_val, bits) for j, comp_val in enumerate(ranking) if j != i])
        n_eq = sum([comparison.eq(group, ranking_val, comp_val) for j, comp_val in enumerate(ranking) if j != i])
        points.append(2 * n_truely_greater + n_eq)
    return points

def assert_condorcet_ballot(group: Group, ballot: List[List[Wire]]) -> None:
    """
    Asserts a Condorcet ballot (a Comparison Matrix).

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[List[Wire]]
    :raises ValueError: Raised if the ballot does not verify.
    """
    for i, row in enumerate(ballot):
        for j, entry in enumerate(row):
            if i == j:
                continue
            assertgates.assert_bit(entry)

    for i, j, k in itertools.product(range(len(ballot)), range(len(ballot)), range(len(ballot))):
        if i == j or i == k or j == k:
            continue
        value_i_j = ballot[i][j]
        value_j_i = ballot[j][i]
        check_matrix_i_j = group.gen(1)-ballot[j][i]
        check_matrix_j_k=group.gen(1)-ballot[k][j]
        check_matrix_i_k=group.gen(1)-ballot[k][i]
        assertgates.assert_bit(sum([value_i_j,value_j_i]))
        ind_false = bitgates.and_gate(group,[check_matrix_i_j,check_matrix_j_k,1-check_matrix_i_k])
        assertgates.assert_equal(group, [ind_false], [group.gen(0)])

def assert_majority_judgment_ballot(group: Group, ballot: List[List[Wire]]) -> None:
    """
    Asserts a Majority Judgment ballot (a 0/1 matrix with exactly one 1 in each row).

    :param group: The underlying group
    :type group: Group
    :param ballot: The ballot
    :type ballot: List[List[Wire]]
    :raises ValueError: Raised if the ballot does not verify.
    """

    for row in ballot:
        assert_single_vote(group,row)