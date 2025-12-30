from typing import Optional, TypeVar
from relations import Eqratio, Predicate, Deduction, AngleRow, RatioRow, Point
import numpy as np

ColName = TypeVar("ColName")

TOLERANCE = 1e-9


def is_in_row_span(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
    """
    Check if b is in the row span of A.
    Return coefficients x such that x @ A = b if possible, else None.
    """
    # Check rank condition first (more exact than least squares residuals)
    try:
        if np.linalg.matrix_rank(A) < np.linalg.matrix_rank(np.vstack([A, b])):
            return None  # rank increased → not in span
    except:
        return None

    # Solve exactly (using least squares now that we know it's consistent)
    x, *_ = np.linalg.lstsq(A.T, b, rcond=None)
    return x


class AngleMatrix:
    rows: list[AngleRow]

    def __init__(self) -> None:
        self.rows = []

    def add_predicate(self, predicate: Predicate) -> None:
        self.rows.extend(predicate.to_angle_rows())

    # try_deduce will return a set of deductions that may be helpful to deduce the given predicate in DD
    def try_deduce(self, predicate: Predicate) -> set[Deduction]:
        b_rows: list[AngleRow] = predicate.to_angle_rows()
        if not b_rows:
            return set()

        implicit_deducitons = set()
        for row in b_rows:
            if not row.data:
                implicit_deducitons.add(Deduction(row.predicate, set(), "AR_trivial"))
        if implicit_deducitons:
            return implicit_deducitons

        pred_to_index: dict[Predicate, int] = {
            pred: i
            for i, pred in enumerate(set([row.predicate for row in self.rows + b_rows]))
        }
        index_to_pred: dict[int, Predicate] = {
            i: pred for pred, i in pred_to_index.items()
        }
        line_to_index: dict[frozenset[Point], int] = {
            line: i
            for i, line in enumerate(
                set(
                    [line for row in self.rows for line in row.data.keys()]
                    + [line for row in b_rows for line in row.data.keys()]
                )
            )
        }

        A = np.zeros(
            (len(pred_to_index), len(line_to_index) + 1)
        )  # plus one to take care of constants

        seen_predicates: set[Predicate] = set()

        for row in self.rows:
            if row.predicate in seen_predicates:
                continue
            seen_predicates.add(row.predicate)

            row_idx = pred_to_index[row.predicate]
            for line, value in row.data.items():
                col_idx = line_to_index[line]
                if A[row_idx, col_idx] != 0:
                    print(row.data)
                    for i in range(len(line_to_index) + 1):
                        print(A[row_idx, i])
                    assert False
                A[row_idx, col_idx] = value
            A[row_idx, -1] += row.constant

        deductions = set()

        for b_row in b_rows:
            b = np.zeros(
                (len(line_to_index) + 1),
            )
            row_idx = pred_to_index[b_row.predicate]
            for line, value in b_row.data.items():
                col_idx = line_to_index[line]
                b[col_idx] = value
            b[-1] += b_row.constant
            x = is_in_row_span(A, b)
            if x is None:
                continue
            parent_predicates: set[Predicate] = set()
            for i in range(x.shape[0]):
                # Check if any column has a non-zero entry for this row
                if np.abs(x[i]) > TOLERANCE:
                    assert i in index_to_pred
                    parent_predicates.add(index_to_pred[i])
            if not parent_predicates:
                continue
            deductions.add(Deduction(b_row.predicate, parent_predicates, "AR"))
        return deductions

    def __str__(self) -> str:
        return "\n<AngleMatrix>\n" + "\n".join(
            str(row) for row in self.rows if not row.is_zero_row
        )


class RatioMatrix:
    rows: list[RatioRow]

    def __init__(self) -> None:
        self.rows = []

    def add_predicate(self, predicate: Predicate) -> None:
        self.rows.extend(predicate.to_ratio_rows())

    def try_deduce(self, predicate: Predicate) -> set[Deduction]:
        b_rows: list[RatioRow] = predicate.to_ratio_rows()
        if not b_rows:
            return set()

        implicit_deducitons = set()
        for row in b_rows:
            if not row.data:
                implicit_deducitons.add(Deduction(row.predicate, set(), "AR_implicit"))
        if implicit_deducitons:
            return implicit_deducitons

        pred_to_index: dict[Predicate, int] = {
            pred: i
            for i, pred in enumerate(set([row.predicate for row in self.rows + b_rows]))
        }
        index_to_pred: dict[int, Predicate] = {
            i: pred for pred, i in pred_to_index.items()
        }
        line_to_index: dict[frozenset[Point], int] = {
            line: i
            for i, line in enumerate(
                set(
                    [line for row in self.rows for line in row.data.keys()]
                    + [line for row in b_rows for line in row.data.keys()]
                )
            )
        }

        A = np.zeros((len(pred_to_index), len(line_to_index)))

        seen_predicates: set[Predicate] = set()

        for row in self.rows:
            if row.predicate in seen_predicates:
                continue
            seen_predicates.add(row.predicate)
            row_idx = pred_to_index[row.predicate]
            for line, value in row.data.items():
                col_idx = line_to_index[line]
                assert A[row_idx, col_idx] == 0.0
                A[row_idx, col_idx] = value

        deductions = set()

        for b_row in b_rows:
            b = np.zeros(
                (len(line_to_index)),
            )
            row_idx = pred_to_index[b_row.predicate]
            for line, value in b_row.data.items():
                col_idx = line_to_index[line]
                b[col_idx] = value
            x = is_in_row_span(A, b)
            if x is None:
                continue
            parent_predicates: set[Predicate] = set()
            for i in range(x.shape[0]):
                # Check if any column has a non-zero entry for this row
                if np.abs(x[i]) > TOLERANCE:
                    assert i in index_to_pred
                    parent_predicates.add(index_to_pred[i])
            if not parent_predicates:
                continue
            deductions.add(Deduction(b_row.predicate, parent_predicates, "AR"))
        return deductions

    def __str__(self) -> str:
        return "\n<RatioMatrix>\n" + "\n".join(
            str(row) for row in self.rows if not row.is_zero_row
        )


class AR:
    angle_matrix: AngleMatrix
    ratio_matrix: RatioMatrix

    def __init__(self) -> None:
        self.angle_matrix = AngleMatrix()
        self.ratio_matrix = RatioMatrix()

    def add_predicate(self, predicate: Predicate) -> None:
        self.angle_matrix.add_predicate(predicate)
        self.ratio_matrix.add_predicate(predicate)

    def try_deduce(self, predicate: Predicate) -> set[Deduction]:
        return self.angle_matrix.try_deduce(predicate).union(
            self.ratio_matrix.try_deduce(predicate)
        )
