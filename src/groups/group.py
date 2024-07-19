"""
Contains the base class for groups.

Classes:

    Group
"""


class Group():
    """
    Base class for groups.
    """

    def __init__(self):
        pass

    @property
    def zero(self):
        """
        Returns the group element of value zero.

        :return: Group element of value zero.
        :rtype: GroupElement
        """
        return self.gen(0)

    @property
    def one(self):
        """
        Returns the group element of value one.

        :return: Group element of value one.
        :rtype: GroupElement
        """
        return self.gen(1)

    def gen(self, value):
        """
        Returns the group element of given value.

        :param value: Value of the group element.
        :type value: Numeric
        :return: Group element of given value.
        :rtype: GroupElement
        :raises NotImplementedError: Raises if function is not implemented.
        """
        raise NotImplementedError()

    def inv(self, elem):
        """
        Returns the inverse of given group element.

        :param elem: Group element to be inverted.
        :type elem: GroupElement
        :return: Inverse of given group element.
        :rtype: GroupElement
        :raises NotImplementedError: Raises if function is not implemented.
        """
        raise NotImplementedError()
