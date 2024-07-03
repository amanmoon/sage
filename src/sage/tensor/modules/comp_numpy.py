# Tensor Component Backend using numpy.ndarray

from sage.structure.sage_object import SageObject
from sage.rings.integer import Integer
from sage.tensor.modules.comp import Components
import numpy as np


class ComponentNumpy(SageObject):
    def __init__(self, ring, frame, nb_indices, shape=None, start_index=0,
                 output_formatter=None):
        r"""
        TESTS::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: ComponentNumpy(ZZ, [1,2,3], 2)
            2-indices numpy components w.r.t. (1, 2, 3)

        """
        self._ring = ring
        self._frame = tuple(frame) if all(isinstance(i, (list, tuple)) for i in frame) \
                                    else (tuple(frame),)
        self._nid = nb_indices
        self._shape = (len(self._frame[0]),) * nb_indices if shape is None else tuple(shape)
        self._sindex = tuple(start_index) if isinstance(start_index, (list, tuple)) \
                                            else (start_index,) * nb_indices
        self._output_formatter = output_formatter
        self._comp = np.zeros(shape=self._shape, dtype=np.float64)

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c._repr_()
            '2-indices numpy components w.r.t. (1, 2, 3)'

        """
        description = str()
        if not all(self._shape[0] == dim for dim in self._shape):
            description += "{}-shaped ".format(self._shape)
        description += str(self._nid)
        if self._nid == 1:
            description += "-index "
        else:
            description += "-indices "
        description += "numpy components w.r.t. "
        if len(self._frame) == 1:
            description += str(self._frame[0])
        else:
            description += str(self._frame)

        return description

    def _new_instance(self):
        r"""
        Creates a :class:`ComponentNumpy` instance of the same number of indices
        and w.r.t. the same frame.

        This method must be redefined by derived classes of
        :class:`ComponentsNumpy`.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c._new_instance()
            2-indices numpy components w.r.t. (1, 2, 3)

        """
        return self.__class__(self._ring, self._frame, self._nid, self._shape,
                          self._sindex, self._output_formatter)

    def copy(self):
        r"""
        Return an exact copy of ``self``.

        EXAMPLES:

        Copy of a set of components with a single index::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: V = VectorSpace(QQ,3)
            sage: a = ComponentNumpy(QQ, V.basis(), 1)
            sage: a[:] = -2, 1, 5
            sage: b = a.copy() ; b
            1-index numpy components w.r.t. ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            sage: b[:]
            array([-2.,  1.,  5.])
            sage: b == a
            True
            sage: b is a  # b is a distinct object
            False

        """
        result = self._new_instance()
        result._comp = np.copy(self._comp)
        return result

    def _check_indices(self, indices):
        r"""
        Check the validity of a list of indices and returns a tuple from it

        INPUT:

        - ``indices`` -- list of indices (possibly a single integer if
          self is a 1-index object)

        OUTPUT:

        - a tuple containing valid indices

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c._check_indices((0,1))
            (0, 1)
            sage: c._check_indices([0,1])
            (0, 1)
            sage: c._check_indices([2,1])
            (2, 1)
            sage: c._check_indices([2,3])
            Traceback (most recent call last):
            ...
            IndexError: index out of range: 3 not in [0, 2]
            sage: c._check_indices(1)
            Traceback (most recent call last):
            ...
            ValueError: wrong number of indices: 2 expected, while 1 are provided
            sage: c._check_indices([1,2,3])
            Traceback (most recent call last):
            ...
            ValueError: wrong number of indices: 2 expected, while 3 are provided
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2, start_index=[2,3])
            sage: c._check_indices((2,3))
            (0, 0)
            sage: c._check_indices((2,5))
            (0, 2)
            sage: c._check_indices((1,3))
            Traceback (most recent call last):
            ...
            IndexError: index out of range: 1 not in [2, 4]

        """
        if isinstance(indices, (int, Integer)):
            ind = (indices,)
        else:
            ind = tuple(indices)
        shape = self._shape
        if len(ind) != len(shape):
            raise ValueError(("wrong number of indices: {} expected,"
                             " while {} are provided").format(self._nid, len(ind)))
        start_index = self._sindex
        np_ind = tuple()
        for i in range(len(shape)):
            si = start_index[i]
            np_ind += (indices[i] - si,)
            imax = shape[i] + si - 1
            if ind[i] < si or ind[i] > imax:
                raise IndexError("index out of range: " +
                                 "{} not in [{}, {}]".format(ind[i], si, imax))
        return np_ind

    def __getitem__(self, args):
        r"""
        Returns the component corresponding to the given indices.

        INPUT:

        - ``args`` -- list of indices (possibly a single integer if
          self is a 1-index object) or the character ``:`` for the full list
          of components

        OUTPUT:

        - the component corresponding to ``args`` or, if ``args`` = ``:``,
          the full list of components, in the form ``T[i][j]...`` for the
          components `T_{ij...}` (for a 2-indices object, a matrix is returned)

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2, start_index=[1,2])
            sage: c[1,2]    # unset components are zero
            0.0
            sage: c.__getitem__((1,2))
            0.0
            sage: c.__getitem__([1,2])
            0.0
            sage: c[1,2] = -4
            sage: c[1,2]
            -4.0
            sage: c.__getitem__((1,2))
            -4.0
            sage: c[:]
            array([[-4.,  0.,  0.],
                   [ 0.,  0.,  0.],
                   [ 0.,  0.,  0.]])
            sage: c.__getitem__(slice(None))
            array([[-4.,  0.,  0.],
                   [ 0.,  0.,  0.],
                   [ 0.,  0.,  0.]])
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2, start_index=[1,2])
            sage: c[1,2] = 4; c[3,2] = 2
            sage: c[:]
            array([[4., 0., 0.],
                  [0., 0., 0.],
                  [2., 0., 0.]])
            sage: c[1:4:2]
            array([[4., 0., 0.],
                  [2., 0., 0.]])
            sage: c[1:5]
            Traceback (most recent call last):
            ...
            IndexError: [start:stop] not in range [1,4]

        """
        no_format = self._output_formatter is None
        format_type = None # default value, possibly redefined below
        if isinstance(args, list):  # case of [[...]] syntax
            no_format = True
            if isinstance(args[0], slice):
                indices = args[0]
            elif isinstance(args[0], (tuple, list)): # to ensure equivalence between
                indices = args[0]           # [[(i,j,...)]] or [[[i,j,...]]] and [[i,j,...]]
            else:
                indices = tuple(args)
        else:
            # Determining from the input the list of indices and the format
            if isinstance(args, (int, Integer, slice)):
                indices = args
            elif isinstance(args[0], slice):
                indices = args[0]
            elif len(args) == self._nid:
                indices = args
            else:
                format_type = args[-1]
                indices = args[:-1]
        if isinstance(indices, slice):
            start, stop = indices.start, indices.stop
            range_start, range_end = self._sindex[0], self._sindex[0] + self._shape[0]

            if indices.start is not None:
                start = indices.start - range_start
            else:
                start = 0
            if indices.stop is not None:
                stop = indices.stop - range_start
            else:
                stop = range_end - range_start
            if not ((0 <= start <= range_end - range_start - 1) and
                    (0 <= stop <= range_end - range_start)):
                raise IndexError("[start:stop] not in range [{},{}]"
                                 .format(range_start, range_end))

            return self._comp[slice(start, stop, indices.step)]
        else:
            ind = self._check_indices(indices)
            elem = self._comp[ind]
            from sage.rings.real_mpfr import RR
            if no_format:
                return elem
            elif format_type is None:
                return self._output_formatter(RR(elem))
            else:
                return self._output_formatter(RR(elem), format_type)

    def __setitem__(self, args, value):
        r"""
        Sets the component corresponding to the given indices.

        INPUT:

        - ``args`` -- list of indices (possibly a single integer if
          self is a 1-index object); if ``[:]`` is provided, all the
          components are set
        - ``value`` -- the value to be set or a list of values if
          ``args = [:]`` (``slice(None)``)

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c.__setitem__((0,1), -4)
            sage: c[:]
            array([[ 0., -4.,  0.],
                   [ 0.,  0.,  0.],
                   [ 0.,  0.,  0.]])
            sage: c[0,1] = -4
            sage: c[:]
            array([[ 0., -4.,  0.],
                   [ 0.,  0.,  0.],
                   [ 0.,  0.,  0.]])
            sage: c.__setitem__(slice(None), [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
            sage: c[:]
            array([[0., 1., 2.],
                  [3., 4., 5.],
                  [6., 7., 8.]])
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2, start_index=[1,2])
            sage: c.__setitem__(slice(None), [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
            sage: c[1:4:2] = [[2, 1, 0], [5, 4, 3]]
            sage: c[:]
            array([[2., 1., 0.],
                   [3., 4., 5.],
                   [5., 4., 3.]])
            sage: c[2:5] = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
            Traceback (most recent call last):
            ...
            IndexError: [start:stop] not in range [1,4]
        """
        if isinstance(args, list):  # case of [[...]] syntax
            if isinstance(args[0], slice):
                indices = args[0]
            elif isinstance(args[0], (tuple, list)): # to ensure equivalence between
                indices = args[0]           # [[(i,j,...)]] or [[[i,j,...]]] and [[i,j,...]]
            else:
                indices = tuple(args)
        else:
            # Determining from the input the list of indices and the format
            if isinstance(args, (int, Integer, slice)):
                indices = args
            elif isinstance(args[0], slice):
                indices = args[0]
            elif len(args) == self._nid:
                indices = args

        if isinstance(indices, slice):
            start, stop = indices.start, indices.stop
            range_start, range_end = self._sindex[0], self._sindex[0] + self._shape[0]

            if indices.start is not None:
                start = indices.start - range_start
            else:
                start = 0
            if indices.stop is not None:
                stop = indices.stop - range_start
            else:
                stop = range_end - range_start
            if not ((0 <= start <= range_end - range_start - 1) and
                    (0 <= stop <= range_end - range_start)):
                raise IndexError("[start:stop] not in range [{},{}]"
                    .format(range_start, range_end))

            self._comp[start:stop:indices.step] = value
        else:
            ind = self._check_indices(indices)
            self._comp[ind] = value

    def _broadcast(self, other):
        r"""
        broadcast self with other

        INPUT:

        - ``other`` -- components, on the same frame as ``self``

        OUTPUT:

        - the broadcasted component of ``self`` by ``other``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c_1 = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c_2 = ComponentNumpy(ZZ, [1,2,3], 3, (1,3,3))
            sage: c_1._broadcast(c_2)
            (1, 3, 3)-shaped 3-indices numpy components w.r.t. (1, 2, 3)
            sage: c_2._broadcast(c_1)
            (1, 3, 3)-shaped 3-indices numpy components w.r.t. (1, 2, 3)
            sage: c_2 = ComponentNumpy(ZZ, [1,2,3], 3, (1,2,3))
            sage: c_1._broadcast(c_2)
            Traceback (most recent call last):
            ...
            ValueError: Shapes (3, 3), (1, 2, 3) cannot be broadcasted
        """
        s_shape = self._shape
        o_shape = other._shape
        N1 = len(s_shape)
        N2 = len(o_shape)
        N = max(N1, N2)
        shape = [0] * N

        i = N - 1
        while i >= 0:
            n1 = N1 - N + i
            d1 = s_shape[n1] if n1 >= 0 else 1
            n2 = N2 - N + i
            d2 = o_shape[n2] if n2 >= 0 else 1
            if d1 == 1:
                shape[i] = d2
            elif d2 == 1:
                shape[i] = d1
            elif d1 == d2:
                shape[i] = d1
            else:
                raise ValueError("Shapes {}, {} cannot be broadcasted"
                                 .format(self._shape, other._shape))
            i -= 1

        frame = tuple(set(self._frame + other._frame))
        output_formatter = None
        if self._output_formatter == other._output_formatter: # output formatter is None if self and other had diff output formatter
            output_formatter = self._output_formatter

        return ComponentNumpy(self._ring, frame, len(shape), shape, output_formatter=output_formatter)

## Arithmetic Operators

    def __pos__(self):
        r"""
        Unary plus operator.

        OUTPUT:

        - an exact copy of ``self``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: c[:] = 5, 0, -4
            sage: a = c.__pos__() ; a
            1-index numpy components w.r.t. (1, 2, 3)
            sage: a[:]
            array([ 5.,  0., -4.])
            sage: a == +c
            True
            sage: a == c
            True

        """
        return self.copy()

    def __neg__(self):
        r"""
        Unary minus operator.

        OUTPUT:

        - the opposite of the components represented by ``self``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: c[:] = 5, 0, -4
            sage: a = c.__neg__() ; a
            1-index numpy components w.r.t. (1, 2, 3)
            sage: a[:]
            array([-5., -0.,  4.])
            sage: a == -c
            True

        """
        neg_com = self._new_instance()
        neg_com._comp = (- np.copy(self._comp))
        return neg_com

    def __add__(self, other):
        r"""
        Component addition.

        INPUT:

        - ``other`` -- components of the same number of indices and defined
          on the same frame as ``self``

        OUTPUT:

        - components resulting from the addition of ``self`` and ``other``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: b = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: b[:] = 4, 5, 6
            sage: s = a.__add__(b) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([5., 5., 3.])
            sage: s == a+b
            True
        """
        if isinstance(other, (int, Integer)) and other == 0:
            return +self
        if not isinstance(other, (Components, ComponentNumpy)):
            raise TypeError("the second argument for the addition must be a " +
                            "an instance of Components")
        # if isinstance(other, CompWithSymNumpy):
        #     return other + self     # to deal properly with symmetries
        if self._shape != other._shape: # use tensor broadcasting
            ret = self._broadcast(other)
        else:
            ret = self.copy()
        ret._comp = self._comp + other._comp
        return ret

    def __radd__(self, other):
        r"""
        Reflected addition (addition on the right to `other``)

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: b = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: b[:] = 4, 5, 6
            sage: s = a.__radd__(b) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([5., 5., 3.])
            sage: s == a+b
            True
            sage: s = 0 + a ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s == a
            True

        """
        return self + other

    def __sub__(self, other):
        r"""
        Component subtraction.

        INPUT:

        - ``other`` -- components, of the same type as ``self``

        OUTPUT:

        - components resulting from the subtraction of ``other`` from ``self``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: b = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: b[:] = 4, 5, 6
            sage: s = a.__sub__(b) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([-3., -5., -9.])
            sage: s == a - b
            True

        """
        if isinstance(other, (int, Integer)) and other == 0:
            return +self
        return self + (-other)

    def __rsub__(self, other):
        r"""
        Reflected subtraction (subtraction from ``other``).

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: b = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: b[:] = 4, 5, 6
            sage: s = a.__rsub__(b) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([3., 5., 9.])
            sage: s == b - a
            True
            sage: s = 0 - a ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([-1., -0.,  3.])
            sage: s == -a
            True

        """
        return (-self) + other

    def __mul__(self, other):
        r"""
        Component tensor product.

        INPUT:

        - ``other`` -- components, on the same frame as ``self``

        OUTPUT:

        - the tensor product of ``self`` by ``other``

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: s = a.__mul__(3); s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([  3.,   0., -9.])
            sage: b = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: b[:] = 4, 5, 6
            sage: s = a.__mul__(b) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([  4.,   0., -18.])
            sage: s == a*b
            True
            sage: t = b*a
            sage: t == s
            True

        """
        if isinstance(other, (int, Integer)):
            ret = self.copy()
            ret._comp = self._comp * other
        else:
            if self._shape == other._shape:
                ret = self.copy()
            else:
                ret = self._broadcast(other)
            ret._comp = self._comp * other._comp
        return ret

    def __rmul__(self, other):
        r"""
        Reflected multiplication (multiplication on the left by ``other``).

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: s = a.__rmul__(2) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([ 2.,  0., -6.])
            sage: s == 2*a
            True
            sage: a.__rmul__(0) == 0
            True

        """
        return self * other

    def __truediv__(self, other):
        r"""
        Division (by a scalar).

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(QQ, [1,2,3], 1)
            sage: a[:] = 1, 0, -3
            sage: s = a.__truediv__(3) ; s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([ 0.33333333,  0.        , -1.        ])
            sage: s == a/3
            True
            sage: 3*s == a
            True

        """
        if isinstance(other, (int, Integer)):
            ret = self.copy()
            ret._comp = self._comp / other
        else:
            if self._shape == other._shape:
                ret = self.copy()
            else:
                ret = self._broadcast(other)
            ret._comp = self._comp / other._comp
        return ret

    def __floordiv__(self, other):
        r"""
        Evaluates self_i // other_i for each element of Component
        ``self`` with the respective element of ``other``.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(QQ, [1,2,3], 1)
            sage: a[:] = 2, 0, -3
            sage: s = a.__floordiv__(2); s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([ 1.,  0., -2.])
            sage: b = ComponentNumpy(QQ, [1,2,3], 1)
            sage: b[:] = 1, 4, -2
            sage: s = a.__floordiv__(b); s[:]
            array([2., 0., 1.])

        """
        if isinstance(other, (int, Integer)):
            ret = self.copy()
            ret._comp = self._comp // other
        else:
            if self._shape == other._shape:
                ret = self.copy()
            else:
                ret = self._broadcast(other)
            ret._comp = self._comp // other._comp
        return ret

    def __mod__(self, other):
        r"""
        Evaluates self_i % other_i for each element of Component
        ``self`` with the respective element of ``other``.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(QQ, [1,2,3], 1)
            sage: a[:] = 1, 2, -3
            sage: s = a.__mod__(2); s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([1., 0., 1.])
            sage: b = ComponentNumpy(QQ, [1,2,3], 1)
            sage: b[:] = 1, 4, -2
            sage: s = a.__mod__(b); s[:]
            array([ 0.,  2., -1.])

        """
        if isinstance(other, (int, Integer)):
            ret = self.copy()
            ret._comp = self._comp % other
        else:
            if self._shape == other._shape:
                ret = self.copy()
            else:
                ret = self._broadcast(other)
            ret._comp = self._comp % other._comp
        return ret

    def __pow__(self, other):
        r"""
        Evaluates self_i ^ other_i for each element of Component
        ``self`` with the respective element of ``other``.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(QQ, [1,2,3], 1)
            sage: a[:] = 3, 0, -3
            sage: s = a.__pow__(2); s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([9., 0., 9.])
            sage: b = ComponentNumpy(QQ, [1,2,3], 1)
            sage: b[:] = -1, 4, -2
            sage: s = a.__pow__(b); s[:]
            array([0.33333333, 0.        , 0.11111111])

        """
        if isinstance(other, (int, Integer)):
            ret = self.copy()
            ret._comp = self._comp ** other
        else:
            if self._shape == other._shape:
                ret = self.copy()
            else:
                ret = self._broadcast(other)
            ret._comp = self._comp ** other._comp
        return ret

    def __abs__(self):
        r"""
        Evaluates |self_i| for each element of Component ``self``.

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: a = ComponentNumpy(QQ, [1,2,3], 1)
            sage: a[:] = 3, 0, -3
            sage: s = a.__abs__(); s
            1-index numpy components w.r.t. (1, 2, 3)
            sage: s[:]
            array([3., 0., 3.])

        """
        if np.all(self._comp >= 0):
            return self.copy()
        else:
            ret = self.copy()
            ret._comp = np.absolute(ret._comp)
            return ret

# Comparison Operators

    def __eq__(self, other):
        r"""
        Comparison (equality) operator.

        INPUT:

        - ``other`` -- a set of components or 0

        OUTPUT:

        - ``True`` if ``self`` is equal to ``other``,  or ``False`` otherwise

        EXAMPLES::

            sage: from sage.tensor.modules.comp_numpy import ComponentNumpy
            sage: c = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c.__eq__(0)  # uninitialized components are zero
            True
            sage: c[0,1], c[1,2] = 5, -4
            sage: c.__eq__(0)
            False
            sage: c1 = ComponentNumpy(ZZ, [1,2,3], 2)
            sage: c1[0,1] = 5
            sage: c.__eq__(c1)
            False
            sage: c1[1,2] = -4
            sage: c.__eq__(c1)
            True
            sage: v = ComponentNumpy(ZZ, [1,2,3], 1)
            sage: c.__eq__(v)
            False

        """
        if isinstance(other, (int, Integer)): # other is 0
            if other == 0:
                return np.all(self._comp == 0)
            else:
                raise TypeError("cannot compare a set of components to a number")
        else: # other is another Components
            if set(other._frame) != set(self._frame):
                return False
            if other._nid != self._nid:
                return False
            if other._sindex != self._sindex:
                return False
            if other._output_formatter != self._output_formatter:
                return False
            return np.all(other._comp == self._comp)

## In-place Operators

    def __iadd__(self, other):
        return self + other
    def __isub__(self, other):
        return self - other
    def __imul__(self, other):
        return self * other
    def __itruediv__(self, other):
        return self / other
    def __ifloordiv__(self, other):
        return self // other
    def __ipow__(self, other):
        return self ** other
    def __imod__(self, other):
        return self % other
    def __imatmul__(self, other):
        return self @ other

    # This function can be implemented after the product of basis is implemented
    # def khatri_rao_product(self, *args):
    #     if not all(isinstance(args, ComponentNumpy)):
    #         raise TypeError('arguments for khatri_rao_product must be an instance of ComponentNumpy')
    #     if self._nid != 2 or any(args._nid != 2):
    #         raise ValueError('invalid dimension, dimension of input component must be 2 given')
    #     col = self._shape[1]
    #     if any(args._shape[1] != col):
    #         raise ValueError('given component must have the same number of columns as self')

    #     from functools import reduce
    #     import operator
    #     array = [arg._comp for arg in args]
    #     rows = reduce(operator.mul, [arg._shape[0] for arg in args], self._shape[0])
    #     ret = self._new_instance(self._ring, , 2, (rows, self._shape[1]))
    #     matrix = ComponentNumpy._khatri_rao_product(self._comp, *array)
    #     ret._comp = matrix
    #     return ret
    
    def _khatri_rao_product(*args):
        cols = args[0].shape[1]
        rows = np.prod([arg.shape[0] for arg in args])
        ret = np.zeros((rows, cols))
        for i in range(cols):
            temp = args[0][:, i]
            for matrix in args[1:]:
                temp = np.einsum('i,j->ij', temp, matrix[:, i]).ravel()
            ret[:, i] = temp
        return ret

    def _svd(self, matrix, rank=None):
        import scipy
        dim_1, dim_2 = self._shape
        if dim_1 <= dim_2:
            mdim = dim_1
        else:
            mdim = dim_2
        if rank is None or rank >= mdim:
            U, S, V = scipy.linalg.svd(matrix)
            U, S, V = U[:, :rank], S[:rank], V[:rank, :]
            return U, S, V
        else:
            if dim_1 < dim_2:
                S, U = scipy.sparse.linalg.eigsh(np.dot(matrix, matrix.T), k=rank, which='LM')
                S = np.sqrt(S)
                V = np.dot(matrix.T, U * 1 / S[None, :])
            else:
                S, V = scipy.sparse.linalg.eigsh(np.dot(matrix.T, matrix), k=rank, which='LM')
                S = np.sqrt(S)
                U = np.dot(matrix, V) * 1 / S[None, :]

            U, S, V = U[:, ::-1], S[::-1], V[:, ::-1]
            return U, S, V.T
    
