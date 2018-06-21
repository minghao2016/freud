# Copyright (c) 2010-2018 The Regents of the University of Michigan
# This file is part of the freud project, released under the BSD 3-Clause License.

from collections import namedtuple
import numpy as np
from ._freud import Box as _Box


class Box(_Box):
    """The freud Box class for simulation boxes.

    .. moduleauthor:: Richmond Newman <newmanrs@umich.edu>
    .. moduleauthor:: Carl Simon Adorf <csadorf@umich.edu>
    .. moduleauthor:: Bradley Dice <bdice@bradleydice.com>

    .. versionchanged:: 0.7.0
       Added box periodicity interface

    For more information about the definition of the simulation
    box, please see:

        http://hoomd-blue.readthedocs.io/en/stable/box.html

    :param float Lx: Length of side x
    :param float Ly: Length of side y
    :param float Lz: Length of side z
    :param float xy: Tilt of xy plane
    :param float xz: Tilt of xz plane
    :param float yz: Tilt of yz plane
    :param bool is2D: Specify that this box is 2-dimensional,
        default is 3-dimensional.
    """

    def to_dict(self):
        return {
            'Lx': self.Lx,
            'Ly': self.Ly,
            'Lz': self.Lz,
            'xy': self.xy,
            'xz': self.xz,
            'yz': self.yz,
            'dimensions': self.dimensions}

    def to_tuple(self):
        """Returns the box as named tuple.

        :return: box parameters
        :rtype: namedtuple
        """
        tuple_type = namedtuple(
            'BoxTuple', ['Lx', 'Ly', 'Lz', 'xy', 'xz', 'yz'])
        return tuple_type(Lx=self.Lx, Ly=self.Ly, Lz=self.Lz,
                          xy=self.xy, xz=self.xz, yz=self.yz)

    def to_matrix(self):
        """Returns the box matrix (3x3).

        :return: box matrix
        :rtype: list of lists, shape 3x3
        """
        return [[self.Lx, self.xy * self.Ly, self.xz * self.Lz],
                [0, self.Ly, self.yz * self.Lz],
                [0, 0, self.Lz]]

    def __str__(self):
        return ("{cls}(Lx={Lx}, Ly={Ly}, Lz={Lz}, xy={xy}, "
                "xz={xz}, yz={yz}, dimensions={dimensions})").format(
                    cls=type(self).__name__, **self.to_dict())

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    @classmethod
    def from_box(cls, box, dimensions=None):
        """Initialize a box instance from a box-like object.

        :param box: A box-like object
        :param int dimensions: Dimensionality of the box

        .. note:: Objects that can be converted to freud boxes include
                  lists like :code:`[Lx, Ly, Lz, xy, xz, yz]`,
                  dictionaries with keys
                  :code:`'Lx', 'Ly', 'Lz', 'xy', 'xz', 'yz', 'dimensions'`,
                  namedtuples with properties
                  :code:`Lx, Ly, Lz, xy, xz, yz, dimensions`,
                  3x3 matrices (see :py:meth:`~.from_matrix()`),
                  or existing :py:class:`freud.box.Box` objects.

                  If any of :code:`Lz, xy, xz, yz` are not provided, they will
                  be set to 0.

                  If all values are provided, a triclinic box will be
                  constructed. If only :code:`Lx, Ly, Lz` are provided, an
                  orthorhombic box will be constructed. If only :code:`Lx, Ly`
                  are provided, a rectangular (2D) box will be constructed.

                  If the optional :code:`dimensions` argument is given, this
                  will be used as the box dimensionality. Otherwise, the box
                  dimensionality will be detected from the :code:`dimensions`
                  of the provided box. If no dimensions can be detected, the
                  box will be 2D if :code:`Lz == 0`, and 3D otherwise.
        """
        if isinstance(box, np.ndarray) and box.shape == (3, 3):
            # Handles 3x3 matrices
            return cls.from_matrix(box)
        try:
            # Handles freud.box.Box and namedtuple
            Lx = box.Lx
            Ly = box.Ly
            Lz = getattr(box, 'Lz', 0)
            xy = getattr(box, 'xy', 0)
            xz = getattr(box, 'xz', 0)
            yz = getattr(box, 'yz', 0)
            if dimensions is None:
                dimensions = getattr(box, 'dimensions', None)
        except AttributeError:
            try:
                # Handle dictionary-like
                Lx = box['Lx']
                Ly = box['Ly']
                Lz = box.get('Lz', 0)
                xy = box.get('xy', 0)
                xz = box.get('xz', 0)
                yz = box.get('yz', 0)
                if dimensions is None:
                    dimensions = box.get('dimensions', None)
            except (KeyError, TypeError):
                # Handle list-like
                Lx = box[0]
                Ly = box[1]
                Lz = box[2] if len(box) > 2 else 0
                xy, xz, yz = box[3:6] if len(box) >= 6 else (0, 0, 0)
        except Exception:
            raise ValueError(
                'Supplied box cannot be converted to type freud.box.Box')

        # The dimensions argument should override the box settings
        if dimensions is None:
            dimensions = 2 if Lz == 0 else 3
        is2D = (dimensions == 2)
        return cls(Lx=Lx, Ly=Ly, Lz=Lz, xy=xy, xz=xz, yz=yz, is2D=is2D)

    @classmethod
    def from_matrix(cls, boxMatrix, dimensions=None):
        """Initialize a box instance from a box matrix.

        For more information and the source for this code,
        see: http://hoomd-blue.readthedocs.io/en/stable/box.html
        """
        boxMatrix = np.asarray(boxMatrix, dtype=np.float32)
        v0 = boxMatrix[:, 0]
        v1 = boxMatrix[:, 1]
        v2 = boxMatrix[:, 2]
        Lx = np.sqrt(np.dot(v0, v0))
        a2x = np.dot(v0, v1) / Lx
        Ly = np.sqrt(np.dot(v1, v1) - a2x * a2x)
        xy = a2x / Ly
        v0xv1 = np.cross(v0, v1)
        v0xv1mag = np.sqrt(np.dot(v0xv1, v0xv1))
        Lz = np.dot(v2, v0xv1) / v0xv1mag
        a3x = np.dot(v0, v2) / Lx
        xz = a3x / Lz
        yz = (np.dot(v1, v2) - a2x * a3x) / (Ly * Lz)
        if dimensions is None:
            dimensions = 2 if Lz == 0 else 3
        return cls(Lx=Lx, Ly=Ly, Lz=Lz,
                   xy=xy, xz=xz, yz=yz, is2D=dimensions == 2)

    @classmethod
    def cube(cls, L):
        """Construct a cubic box with equal lengths.

        :param float L: The edge length
        """
        return cls(Lx=L, Ly=L, Lz=L, xy=0, xz=0, yz=0, is2D=False)

    @classmethod
    def square(cls, L):
        """Construct a 2-dimensional (square) box with equal lengths.

        :param float L: The edge length
        """
        return cls(Lx=L, Ly=L, Lz=0, xy=0, xz=0, yz=0, is2D=True)

    @property
    def L(self):
        """Return the lengths of the box as a tuple (x, y, z)."""
        return self.getL()

    @L.setter
    def L(self, value):
        """Set all side lengths of box to L."""
        self.setL(value)

    @property
    def Lx(self):
        """Length of the x-dimension of the box.

        :getter: Returns this box's x-dimension length
        :setter: Sets this box's x-dimension length
        :type: float
        """
        return self.getLx()

    @Lx.setter
    def Lx(self, value):
        self.setL([value, self.Ly, self.Lz])

    @property
    def Ly(self):
        """Length of the y-dimension of the box.

        :getter: Returns this box's y-dimension length
        :setter: Sets this box's y-dimension length
        :type: float
        """
        return self.getLy()

    @Ly.setter
    def Ly(self, value):
        self.setL([self.Lx, value, self.Lz])

    @property
    def Lz(self):
        """Length of the z-dimension of the box.

        :getter: Returns this box's z-dimension length
        :setter: Sets this box's z-dimension length
        :type: float
        """
        return self.getLz()

    @Lz.setter
    def Lz(self, value):
        self.setL([self.Lx, self.Ly, value])

    @property
    def dimensions(self):
        """Number of dimensions of this box (only 2 or 3 are supported).

        :getter: Returns this box's number of dimensions
        :setter: Sets this box's number of dimensions
        :type: int
        """
        return 2 if self.is2D() else 3

    @dimensions.setter
    def dimensions(self, value):
        assert value == 2 or value == 3
        self.set2D(value == 2)

    @property
    def periodic(self):
        """Box periodicity in each dimension.

        :getter: Returns this box's periodicity in each dimension
                 (True if periodic, False if not)
        :setter: Set this box's periodicity in each dimension
        :type: list[bool, bool, bool]
        """
        return self.getPeriodic()

    @periodic.setter
    def periodic(self, periodic):
        self.setPeriodic(periodic[0], periodic[1], periodic[2])
