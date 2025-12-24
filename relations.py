from __future__ import annotations  # unneeded in python 3.11+
from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar, Callable
import functools
from math import atan2, pi, isclose


def str_init_args(init):
    """
    Decorator that captures initialization arguments for custom __str__ methods.

    This decorator wraps an __init__ method to store the original arguments
    passed during initialization. These stored arguments can later be used
    in the __str__ method to display predicates in a more readable format.
    """

    @functools.wraps(init)
    def wrapper(self, *args, **kwargs):
        self._init_args = args
        return init(self, *args, **kwargs)

    return wrapper


T = TypeVar("T")


@dataclass
class Point:
    x: float
    y: float
    name: str = ""

    def __hash__(self):
        return hash((self.x, self.y, self.name))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return (self.x, self.y, self.name) == (other.x, other.y, other.name)

    def __str__(self):
        # We only care about the name of the point when printing in a human-readable manner.
        return self.name


def distance(p: Point, q: Point) -> float:
    return ((q.x - p.x) ** 2 + (q.y - p.y) ** 2) ** 0.5


def angle_of_line(p: Point, q: Point) -> float:
    return atan2(q.y - p.y, q.x - p.x)


def angle_between(p: Point, q: Point, r: Point) -> float:
    angle1 = angle_of_line(p, q)
    angle2 = angle_of_line(q, r)
    angle = angle2 - angle1
    if angle < 0:
        angle += 2 * pi
    return angle


def same_orientation(l1: list[Point], l2: list[Point]) -> bool:
    assert len(l1) == len(l2), "must be same size"

    def edge_length(p, q):
        return (q.x - p.x) * (q.y + p.y)

    area1 = 0
    for i in range(len(l1)):
        area1 += edge_length(l1[i], (l1[(i + 1) % len(l1)]))

    area2 = 0
    for i in range(len(l1)):
        area2 += edge_length(l2[i], (l2[(i + 1) % len(l2)]))

    return (area1 * area2) > 0


Row = TypeVar("Row")


@dataclass
class AngleRow:
    predicate: Predicate
    constant: float = 0.0  # constant coefficient
    data: dict[frozenset[Point], float] = field(default_factory=dict)

    def __str__(self) -> str:
        res = []
        for line, value in self.data.items():
            if not value:
                continue
            line_str = "".join(sorted([str(p) for p in list(line)]))
            res.append(str(value) + " " + line_str)
        return str(self.constant) + " = " + "\t+ ".join(res)

    @property
    def is_zero_row(self) -> bool:
        return all(value == 0 for value in self.data.values()) and isclose(
            self.constant, 0.0
        )


@dataclass
class RatioRow:
    predicate: Predicate
    data: dict[frozenset[Point], float] = field(default_factory=dict)

    def __str__(self) -> str:
        res = []
        for line, value in self.data.items():
            if not value:
                continue
            line_str = "".join(sorted([str(p) for p in list(line)]))
            res.append(str(value) + " " + line_str)
        return "0 = " + "\t+ ".join(res)

    @property
    def is_zero_row(self) -> bool:
        return all(value == 0 for value in self.data.values())


def collect_rows(
    data: frozenset[Predicate],
    cls: type[Predicate],
    row_func: Callable[[Predicate], Optional[list[Row]]],
) -> list[Row]:
    """Collect and merge rows from subpredicates of a given class."""
    result: list[Row] = []
    for pred in data:
        if isinstance(pred, cls):
            if rows := row_func(pred):
                result.extend(rows)
    return result


@dataclass
class Deduction:
    predicate: Predicate
    parent_predicates: set[Predicate]

    def __hash__(self):
        return hash((self.predicate, frozenset(self.parent_predicates)))


class Predicate(Generic[T]):
    data: T
    _init_args: Optional[tuple] = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.data == other.data

    def __hash__(self):
        return hash((self.__class__.__name__, self.data))

    def __str__(self):
        predicate = self.__class__.__name__.lower()
        if self._init_args is not None:
            args_str = " ".join(str(arg) for arg in self._init_args)
            return f"{predicate} {args_str}"
        else:
            return f"{predicate}({self.data})"

    def to_sub_data(self) -> set[Deduction]:
        if not isinstance(self.data, frozenset):
            return set()

        deductions: set[Deduction] = set()

        for pred in self.data:
            if not isinstance(pred, Predicate):
                continue

            deductions.add(Deduction(pred, {self}))
            deductions |= pred.to_sub_data()

        return deductions

    def to_angle_rows(self) -> list[AngleRow]:
        return []

    def to_ratio_rows(self) -> list[RatioRow]:
        return []

    def is_valid(self) -> bool:
        if not isinstance(self.data, frozenset):
            return True

        for pred in self.data:
            if not isinstance(pred, Predicate):
                continue

            if not pred.is_valid():
                return False
        return True


class Col(Predicate):
    """A B C are collinear"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point):
        self.data = frozenset([Para(a, b, b, c), Para(a, b, a, c), Para(b, c, a, c)])

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Para, lambda p: p.to_angle_rows())


class Perp(Predicate):
    """A B ⊥ C D"""

    data: frozenset[frozenset[Point]]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.data = frozenset([frozenset({a, b}), frozenset({c, d})])

    def to_angle_rows(self) -> list[AngleRow]:
        return [
            AngleRow(
                predicate=self,
                data={list(self.data)[0]: 1, list(self.data)[1]: 1},
                constant=1 / 2,
            )
        ]

    def is_valid(self) -> bool:
        lines = list(self.data)
        if len(lines) != 2:
            return False
        line1, line2 = lines
        if line1 == line2:
            return False
        if len(set(line1)) == 1 or len(set(line2)) == 1:
            return False
        if not isclose(
            abs(angle_of_line(*line1) - angle_of_line(*line2)) % pi,
            pi / 2,
            abs_tol=1e-2,
        ):
            return False
        return True


class Cong(Predicate):
    """A B ≅ C D"""

    data: frozenset[frozenset[Point]]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.data = frozenset([frozenset({a, b}), frozenset({c, d})])

    def to_ratio_rows(self) -> list[RatioRow]:
        if len(self.data) != 2:
            return [RatioRow(predicate=self, data={})]
        return [
            RatioRow(
                predicate=self, data={list(self.data)[0]: 1, list(self.data)[1]: -1}
            )
        ]

    def is_valid(self) -> bool:
        lines = list(self.data)
        if len(lines) < 2:
            return True
        line1, line2 = lines
        if not isclose(distance(*line1), distance(*line2)):
            return False
        return True


class Simtri1(Predicate):
    """△ABC ~ △DEF"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset(
            [
                Eqangle(a, b, c, d, e, f),
                Eqangle(b, c, a, e, f, d),
                Eqangle(c, a, b, f, d, e),
                Eqratio(a, c, b, c, d, f, e, f),
                Eqratio(a, c, b, a, d, f, e, d),
                Eqratio(b, c, a, b, e, f, d, e),
                Eqratio(a, c, d, f, b, c, e, f),
                Eqratio(b, c, e, f, b, a, e, d),
                Eqratio(b, a, e, d, a, c, d, f),
            ]
        )

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Eqangle, lambda p: p.to_angle_rows())

    def to_ratio_rows(self) -> list[RatioRow]:
        return collect_rows(self.data, Eqratio, lambda p: p.to_ratio_rows())


class Simtri2(Predicate):
    """△ABC ~ △DEF with mirror symmetry"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset(
            [
                Eqangle(a, b, c, f, e, d),
                Eqangle(b, c, a, d, f, e),
                Eqangle(c, a, b, e, d, f),
                Eqratio(a, c, a, b, d, f, d, e),
                Eqratio(a, b, b, c, d, e, e, f),
            ]
        )

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Eqangle, lambda p: p.to_angle_rows())

    def to_ratio_rows(self) -> list[RatioRow]:
        return collect_rows(self.data, Eqratio, lambda p: p.to_ratio_rows())


class Eqangle(Predicate):
    """∠ABC = ∠DEF"""

    data: frozenset[tuple[Point, Point, Point]]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset([(a, b, c), (d, e, f)])

    def to_angle_rows(self) -> list[AngleRow]:
        if len(self.data) != 2:
            return [AngleRow(predicate=self, data={})]
        l0a = frozenset(list(self.data)[0][:2])
        l0b = frozenset(list(self.data)[0][1:])
        l1a = frozenset(list(self.data)[1][:2])
        l1b = frozenset(list(self.data)[1][1:])

        data = {}
        data[l0a] = data.get(l0a, 0) + 1
        data[l0b] = data.get(l0b, 0) - 1
        data[l1a] = data.get(l1a, 0) - 1
        data[l1b] = data.get(l1b, 0) + 1
        return [AngleRow(predicate=self, data=data)]

    def is_valid(self) -> bool:
        angles = list(self.data)
        if len(set(angles)) > 2:
            return False
        if len(set(angles)) == 1:
            if len(set(angles[0])) != 3:
                return False
            return True
        a1, b1, c1 = angles[0]
        a2, b2, c2 = angles[1]
        if len({a1, b1, c1}) != 3:
            return False
        if len({a2, b2, c2}) != 3:
            return False
        if not (
            isclose(
                ((angle_between(a1, b1, c1) % pi) - (angle_between(a2, b2, c2) % pi))
                % pi,
                0,
                abs_tol=1e-2,
            )
            or isclose(
                ((angle_between(a1, b1, c1) % pi) - (angle_between(a2, b2, c2) % pi))
                % pi,
                pi,
                abs_tol=1e-2,
            )
        ):
            return False
        return True


class Para(Predicate):
    """A B || C D"""

    data: frozenset[frozenset[Point]]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.data = frozenset([frozenset({a, b}), frozenset({c, d})])

    def to_angle_rows(self) -> list[AngleRow]:
        if len(self.data) != 2:
            return [AngleRow(predicate=self, data={})]
        return [
            AngleRow(
                predicate=self, data={list(self.data)[0]: 1, list(self.data)[1]: -1}
            )
        ]

    def is_valid(self) -> bool:
        lines = list(self.data)
        if len(lines) <= 2:
            return True
        line1, line2 = lines
        if line1 == line2:
            return False
        if len(set(line1)) == 1 or len(set(line2)) == 1:
            return False
        if not isclose(angle_of_line(*line1) % pi, angle_of_line(*line2) % pi):
            return False
        return True


class Contri1(Predicate):
    """△ABC ≅ △DEF"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset(
            [
                Eqangle(a, b, c, d, e, f),
                Eqangle(b, c, a, e, f, d),
                Eqangle(c, a, b, f, d, e),
                Cong(a, b, d, e),
                Cong(b, c, e, f),
                Cong(c, a, f, d),
            ]
        )

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Eqangle, lambda p: p.to_angle_rows())

    def to_ratio_rows(self) -> list[RatioRow]:
        return collect_rows(self.data, Cong, lambda p: p.to_ratio_rows())


class Contri2(Predicate):
    """△ABC ≅ △DEF with mirror symmetry"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset(
            [
                Eqangle(c, a, b, e, d, f),
                Eqangle(b, c, a, d, f, e),
                Eqangle(a, b, c, f, e, d),
                Cong(a, b, d, e),
                Cong(b, c, e, f),
                Cong(a, c, d, f),
            ]
        )

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Eqangle, lambda p: p.to_angle_rows())

    def to_ratio_rows(self) -> list[RatioRow]:
        return collect_rows(self.data, Cong, lambda p: p.to_ratio_rows())


class Cyclic(Predicate):
    """A B C D lie on a circle"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point):
        self.data = frozenset(
            [
                Eqangle(b, a, c, b, d, c),
                Eqangle(d, a, c, d, b, c),
                Eqangle(b, d, a, b, c, a),
                Eqangle(d, b, a, d, c, a),
            ]
        )

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Eqangle, lambda p: p.to_angle_rows())


class Sameclock(Predicate):
    """A B C D are in the same clockwise order"""

    data: frozenset[tuple[Point, Point, Point]]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point, f: Point):
        self.data = frozenset([(a, b, c), (d, e, f)])

    def is_valid(self) -> bool:
        angles = list(self.data)
        if len(angles) <= 2:
            return True
        l1 = angles[0]
        l2 = angles[1]
        return same_orientation(list(l1), list(l2))


class Midp(Predicate):
    """M is the midpoint of A B"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, m: Point, a: Point, b: Point):
        self.data = frozenset([Col(m, a, b), Cong(a, m, m, b)])

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Col, lambda p: p.to_angle_rows())

    def to_ratio_rows(self) -> list[RatioRow]:
        return collect_rows(self.data, Cong, lambda p: p.to_ratio_rows())


class Eqratio(Predicate):
    """AB/CD = EF/GH"""

    data: frozenset[tuple[frozenset[Point], frozenset[Point]]]

    @str_init_args
    def __init__(
        self,
        a: Point,
        b: Point,
        c: Point,
        d: Point,
        e: Point,
        f: Point,
        g: Point,
        h: Point,
    ):
        self.data = frozenset(
            [
                (frozenset({a, b}), frozenset({c, d})),
                (frozenset({e, f}), frozenset({g, h})),
            ]
        )

    def to_ratio_rows(self) -> list[RatioRow]:
        if len(self.data) != 2:
            return []
        l0a, l0b = list(self.data)[0]
        l1a, l1b = list(self.data)[1]
        return [
            RatioRow(
                predicate=self,
                data={
                    l0a: 1,
                    l0b: -1,
                    l1a: -1,
                    l1b: 1,
                },
            )
        ]

    def is_valid(self) -> bool:
        ratios = list(self.data)
        if len(ratios) <= 2:
            return True
        l0a, l0b = ratios[0]
        l1a, l1b = ratios[1]
        if (
            len(set(l0a)) != 2
            or len(set(l0b)) != 2
            or len(set(l1a)) != 2
            or len(set(l1b)) != 2
        ):
            return False
        if not isclose(
            distance(*l0a) / distance(*l0b), distance(*l1a) / distance(*l1b)
        ):
            return False
        return True


class Aconst(Predicate):
    """∠ABC = mπ/n"""

    data: tuple[Point, Point, Point, int, int]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, m: int, n: int):
        self.data = (a, b, c, m, n)

    def to_angle_rows(self) -> list[AngleRow]:
        lines = (
            frozenset({self.data[0], self.data[1]}),
            frozenset({self.data[1], self.data[2]}),
        )
        return [
            AngleRow(
                predicate=self,
                data={lines[0]: 1, lines[1]: -1},
                constant=self.data[3] / (self.data[4] * 2),
            )
        ]

    def is_valid(self) -> bool:
        a, b, c, m, n = self.data
        angle = angle_between(a, b, c)
        if not isclose(angle, (m * pi) / n):
            return False
        return True


## CUSTOM PREDICATES (not on the spreadsheet) ##
# intersect A B C D E
class Inter(Predicate):
    """A is the intersection of line BC and line DE"""

    data: frozenset[Predicate]

    @str_init_args
    def __init__(self, a: Point, b: Point, c: Point, d: Point, e: Point):
        self.data = frozenset([Col(a, b, c), Col(a, d, e)])

    def to_angle_rows(self) -> list[AngleRow]:
        return collect_rows(self.data, Col, lambda p: p.to_angle_rows())
