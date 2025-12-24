from relations import Predicate, Point, Cong, Para, Perp, Eqangle, Deduction
import itertools
from dd import DD
from ar import AR


class Problem:
    predicates: dict[Predicate, set[Predicate]]
    goals: set[Predicate]
    points: set[Point]
    ar: AR
    dd: DD
    possible_relations: set[Predicate]
    impossible_relations: set[Predicate]

    # Maintain an auxiliary buffer of deductions that can be flushed at a later time.
    deductions_buffer: list[Predicate]

    def __init__(
        self, predicates: set[Predicate], goals: set[Predicate], points: set[Point]
    ):
        # Import here to avoid circular dependency

        self.predicates = {}
        self.goals = goals
        self.points = points
        self.ar = AR()
        self.deductions_buffer = []
        self.possible_relations = set()
        self.impossible_relations = set()

        # Initialize the deductive database with points and initial predicates
        self.dd = DD(points, predicates)

        # Add initial predicates to problem
        for predicate in predicates:
            self._add_predicate(predicate, set())

    def add_deduction(self, predicate: Predicate):
        """Add a predicate to the deductions buffer."""
        self.deductions_buffer.append(predicate)

    def flush_deductions(self):
        """Flush the deductions buffer and add predicates to the problem and DD."""
        for predicate in self.deductions_buffer:
            # Add to AR
            self.ar.add_predicate(predicate)

            # Add to DD
            self.dd.add_predicate(predicate)

            # Add to problem predicates (no parent tracking)
            self._add_predicate(predicate, set())

        self.deductions_buffer.clear()

    def can_deduce(self, predicate: Predicate) -> bool:
        if predicate in self.predicates:
            return True

        if predicate in self.impossible_relations:
            return False
        if predicate not in self.possible_relations:
            if predicate.is_valid():
                self.possible_relations.add(predicate)
            else:
                self.impossible_relations.add(predicate)
                return False

        # AR deduction
        ar_deductions = self.ar.try_deduce(predicate)
        for deduction in ar_deductions:
            self.add_deduction(deduction.predicate)
        return False

    def _add_predicate(self, predicate: Predicate, parent_predicates: set[Predicate]):
        if predicate in self.predicates:
            # If the predicate is already in self.predicates, just ignore it...
            return

        if predicate in self.impossible_relations:
            return
        if predicate not in self.possible_relations:
            if predicate.is_valid():
                self.possible_relations.add(predicate)
            else:
                print(f"Predicate {predicate} is invalid, marking as impossible.")
                self.impossible_relations.add(predicate)
                return

        # Assert the invariant that all parent_predicates are already in self.predicates
        for p in parent_predicates:
            # if p not in self.predicates:
            #     raise RuntimeError(
            #         f"Parent predicate {p} not in predicates when adding {predicate}"
            #     )
            # assert p in self.predicates
            pass

        self.predicates[predicate] = parent_predicates
        for sub_deduction in predicate.to_sub_data():
            self.predicates[sub_deduction.predicate] = sub_deduction.parent_predicates

    def is_solved(self) -> bool:
        # We have solved the problem if all goals are in self.predicates
        return all(goal in self.predicates for goal in self.goals)

    def search_ar(self):
        """
        Scans through all predicate types with all point combinations.
        """

        predicates_by_arity = {
            4: [Cong, Para, Perp],  # Para, Perp
            6: [Eqangle],
            # 8: [Eqratio],
        }

        for arity, pred_classes in predicates_by_arity.items():
            distinct_points = 2
            if arity % 3 == 0:
                distinct_points = 3

            def canonical_block(block):
                rotated = block[-1:] + block[:-1]
                names_block = [x.name for x in block]
                names_rotated = [x.name for x in rotated]
                return tuple(block) if names_block <= names_rotated else tuple(rotated)

            def permissible_combos(items, n, m):
                assert n % m == 0
                k = n // m
                base_blocks = set()
                for block in itertools.product(items, repeat=m):
                    names = [x.name for x in block]
                    if len(set(names)) != m:
                        continue
                    canon = canonical_block(list(block))
                    base_blocks.add(canon)
                for chosen in itertools.product(base_blocks, repeat=k):
                    flat = [x for block in chosen for x in block]
                    yield flat

            combos = permissible_combos(self.points, arity, distinct_points)
            for pred_class in pred_classes:
                for point_tuple in combos:
                    pred = pred_class(*point_tuple)
                    if pred in self.predicates:
                        continue
                    try:
                        if is_degenerate(pred):
                            continue
                        ar_deductions = self.can_deduce(pred)
                        parent = {}
                        if ar_deductions and flag:
                            self.add_deduction(Deduction(pred, parent))
                    except Exception as e:
                        pass

    def __str__(self) -> str:
        """
        Generate a string version of the solved problem.

        Returns a numbered list of predicates showing the logical derivation
        from assumptions to goals, including parent predicate references.

        Returns:
            str: Formatted proof steps or error message if unsolved/invalid
        """
        if not self.is_solved():
            return "Unsolved"

        # Validate goals
        if not self.goals:
            return "No goals specified"
        # First, we want to get a list of all predicates that were used in some way or another to reach the goals
        # We'll use backward traversal from goals to find only predicates in the derivation chain

        def find_reachable_predicates():
            """Find all predicates that are reachable from the goals by backward traversal."""
            reachable = set()
            to_visit = set(self.goals)

            while to_visit:
                current = to_visit.pop()
                if current in reachable:
                    continue

                reachable.add(current)
                if current in self.predicates:
                    # Only add unvisited parents to avoid redundant work
                    new_parents = self.predicates[current] - reachable
                    to_visit.update(new_parents)

            return reachable

        goal_reachable_predicates = find_reachable_predicates()

        # Check for unreachable goals
        unreachable_goals = self.goals - goal_reachable_predicates
        if unreachable_goals:
            return f"Unreachable goals: {unreachable_goals}"

        # Filter self.predicates to only include goal-reachable predicates
        filtered_predicates = {
            p: parents
            for p, parents in self.predicates.items()
            if p in goal_reachable_predicates
        }

        # Start with the predicates that were assumed true from the start (and are goal-reachable)
        used_predicates = {
            p for p, parents in filtered_predicates.items() if len(parents) == 0
        }
        ordered_predicates: list[tuple[Predicate, set[Predicate]]] = [
            (p, set()) for p in used_predicates
        ]

        # Topological sort with infinite loop protection
        prev_used_count = -1
        while any(goal not in used_predicates for goal in self.goals):
            current_count = len(used_predicates)
            if current_count == prev_used_count:
                # No progress made - potential infinite loop or missing predicates
                remaining_goals = [
                    goal for goal in self.goals if goal not in used_predicates
                ]
                full_tree = "\n".join(
                    [
                        f"{str(k):<20} | {', '.join([str(vi) for vi in list(v)])}"
                        for k, v in self.predicates.items()
                    ]
                )
                raise RuntimeError(
                    f"Cannot complete proof - unreachable goals: {'\n'.join([str(goal) for goal in remaining_goals])}\n{full_tree}"
                )
            prev_used_count = current_count

            for predicate, parent_predicates in filtered_predicates.items():
                if predicate in used_predicates:
                    continue
                if all(parent in used_predicates for parent in parent_predicates):
                    used_predicates.add(predicate)
                    ordered_predicates.append((predicate, parent_predicates))

        numbering: dict[Predicate, int] = {}
        for i, (predicate, _) in enumerate(ordered_predicates):
            numbering[predicate] = i + 1

        # Build result efficiently using list join
        lines = []
        for predicate, parents in ordered_predicates:
            parent_refs = (
                ""
                if not parents
                else " (" + ",".join(f"[{numbering[p]}]" for p in parents) + ")"
            )
            lines.append(f"[{numbering[predicate]}] {predicate}{parent_refs}")

        return "\n".join(lines)


# Helpers for constructing minimal predicate list


def get_canonical_form(pred_class, point_tuple):
    """
    Returns a canonical form of the predicate to eliminate duplicates.
    This exploits symmetries in the predicate definitions.
    """
    if pred_class.__name__ == "Cong":
        # Cong(A,B,C,D) is symmetric in (A,B) <-> (C,D) and within each pair
        # Canonical: sorted pairs, then sort the two pairs
        seg1 = tuple(sorted([point_tuple[0].name, point_tuple[1].name]))
        seg2 = tuple(sorted([point_tuple[2].name, point_tuple[3].name]))
        return tuple(sorted([seg1, seg2]))

    elif pred_class.__name__ == "Perp":
        # Perp(A,B,C,D) is symmetric: AB ⊥ CD = CD ⊥ AB
        # Also symmetric within each line: AB = BA
        seg1 = tuple(sorted([point_tuple[0].name, point_tuple[1].name]))
        seg2 = tuple(sorted([point_tuple[2].name, point_tuple[3].name]))
        return tuple(sorted([seg1, seg2]))

    elif pred_class.__name__ == "Eqangle":
        # Eqangle(A,B,C,D,E,F): angle ABC = angle DEF
        # Symmetries: swap the two angles, reverse each angle
        angle1 = (point_tuple[0].name, point_tuple[1].name, point_tuple[2].name)
        angle2 = (point_tuple[3].name, point_tuple[4].name, point_tuple[5].name)
        angle1_rev = (angle1[2], angle1[1], angle1[0])
        angle2_rev = (angle2[2], angle2[1], angle2[0])

        # Try all 4 combinations and return the lexicographically smallest
        options = [
            tuple(sorted([angle1, angle2])),
            tuple(sorted([angle1, angle2_rev])),
            tuple(sorted([angle1_rev, angle2])),
            tuple(sorted([angle1_rev, angle2_rev])),
        ]
        return min(options)

    elif pred_class.__name__ == "Eqratio":
        # Eqratio(A,B,C,D,E,F,G,H): AB/CD = EF/GH
        # Symmetries: swap ratios, flip each ratio, swap within segments
        seg1 = tuple(sorted([point_tuple[0].name, point_tuple[1].name]))
        seg2 = tuple(sorted([point_tuple[2].name, point_tuple[3].name]))
        seg3 = tuple(sorted([point_tuple[4].name, point_tuple[5].name]))
        seg4 = tuple(sorted([point_tuple[6].name, point_tuple[7].name]))

        ratio1 = tuple(sorted([seg1, seg2]))
        ratio2 = tuple(sorted([seg3, seg4]))
        return tuple(sorted([ratio1, ratio2]))

    # Default: use point names as-is
    return tuple(p.name for p in point_tuple)


def process_predicate_batch(args):
    """
    Process a batch of predicates. This function will be called in parallel.
    Returns list of (pred, ar_deductions) tuples for successful attempts.
    """
    pred_class, point_tuples, ar_instance = args
    results = []

    for point_tuple in point_tuples:
        try:
            pred = pred_class(*point_tuple)
            ar_deductions = ar_instance.try_deduce(pred)
            # if len(ar_deductions) == 0:
            # print(f"Yo something is up {pred}")
            # Return both the predicate and its deductions
            results.append((pred, ar_deductions))
        except Exception:
            pass

    return results


def permissible_combos_optimized(items, n, m, pred_class):
    """
    Generates permissible combinations with early deduplication.
    Uses canonical forms to avoid generating equivalent predicates.
    """
    assert n % m == 0
    k = n // m

    def canonical_block(block):
        rotated = block[-1:] + block[:-1]
        names_block = [x.name for x in block]
        names_rotated = [x.name for x in rotated]
        return tuple(block) if names_block <= names_rotated else tuple(rotated)

    # Generate base blocks
    base_blocks = set()
    for block in itertools.product(items, repeat=m):
        names = [x.name for x in block]
        if len(set(names)) != m:
            continue
        canon = canonical_block(list(block))
        base_blocks.add(canon)

    # Generate combinations and deduplicate using canonical forms
    seen_canonical = set()

    for chosen in itertools.product(base_blocks, repeat=k):
        flat = [x for block in chosen for x in block]

        # Get canonical form for this predicate
        canonical = get_canonical_form(pred_class, flat)

        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            yield flat


def is_degenerate(pred: Predicate) -> bool:
    if isinstance(pred, Eqangle):
        if len(pred.data) == 2:
            angles = list(pred.data)
            if isclose(angle_between(*angles[0]) % math.pi, 0) or isclose(
                angle_between(*angles[1]) % math.pi, 0
            ):
                return True
    return False
