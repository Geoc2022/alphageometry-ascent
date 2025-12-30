from relations import (
    Deduction,
    Predicate,
    Point,
    Cong,
    Para,
    Perp,
    Eqangle,
)
import itertools
from dd import DD
from ar import AR


class Problem:
    predicates: dict[Predicate, set[Predicate]]
    goals: set[Predicate]
    points: set[Point]
    ar: AR
    dd: DD
    deductions_buffer: list[Deduction]
    possible_relations: set[Predicate]
    impossible_relations: set[Predicate]

    def __init__(
        self, predicates: set[Predicate], goals: set[Predicate], points: set[Point]
    ):
        self.predicates = {}
        self.goals = goals
        self.points = points
        self.dd = DD(points, predicates)
        self.ar = AR()
        self.deductions_buffer = []
        self.possible_relations = set()
        self.impossible_relations = set()

        for predicate in predicates:
            if predicate.is_valid():
                self._add_predicate(predicate, set())
                self.ar.add_predicate(predicate)
            else:
                raise ValueError(f"Invalid initial predicate: {predicate}")

    def add_deduction(self, deduction: Deduction):
        """Add a predicate to the deductions buffer."""
        self.deductions_buffer.append(deduction)

    def flush_deductions(self):
        """Flush the deductions buffer and add predicates to the problem and DD."""
        for deduction in self.deductions_buffer:
            if deduction.predicate in self.predicates:
                continue

            # Add to DD
            self.dd.add_predicate(deduction.predicate)
            for subpredicate in deduction.predicate.to_sub_data():
                self.dd.add_predicate(subpredicate.predicate)

            # Add to AR
            self.ar.add_predicate(deduction.predicate)

            # Add to problem predicates
            self._add_predicate(deduction.predicate, deduction.parent_predicates)
            for subpredicate in deduction.predicate.to_sub_data():
                if subpredicate.predicate in self.predicates:
                    continue
                self._add_predicate(
                    subpredicate.predicate, subpredicate.parent_predicates
                )

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
            self.add_deduction(deduction)
        return False

    def _add_predicate(self, predicate: Predicate, parent_predicates: set[Predicate]):
        if predicate in self.predicates:
            # If the predicate is already in self.predicates, just ignore it...
            return

        if predicate in self.impossible_relations:
            print(f"Predicate {predicate} is marked impossible, cannot add.")
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
            if sub_deduction.predicate not in self.predicates:
                self.predicates[sub_deduction.predicate] = (
                    sub_deduction.parent_predicates
                )

    def is_solved(self) -> bool:
        # We have solved the problem if all goals are in self.predicates
        return all(goal in self.predicates for goal in self.goals)

    def search_ar(self):
        """
        Scans through all predicate types with all point combinations.
        """

        def check_possible(predicate: Predicate):
            if predicate in self.impossible_relations:
                return False
            if predicate in self.possible_relations:
                return True
            else:
                if predicate.is_valid():
                    self.possible_relations.add(predicate)
                    return True
                else:
                    self.impossible_relations.add(predicate)
                    return False

        # Search Cong
        for line1, line2 in itertools.product(
            itertools.combinations(self.points, 2), repeat=2
        ):
            cong = Cong(*line1, *line2)
            if check_possible(cong) and cong not in self.predicates:
                self.can_deduce(cong)

        # Search Para
        for line1, line2 in itertools.product(
            itertools.combinations(self.points, 2), repeat=2
        ):
            para = Para(*line1, *line2)
            if check_possible(para) and para not in self.predicates:
                self.can_deduce(para)

        # Search Perp
        for line1, line2 in itertools.product(
            itertools.combinations(self.points, 2), repeat=2
        ):
            perp = Perp(*line1, *line2)
            if check_possible(perp) and perp not in self.predicates:
                self.can_deduce(perp)

        # Search Eqangle
        for angle1, angle2 in itertools.product(
            itertools.permutations(self.points, 3), repeat=2
        ):
            eqangle = Eqangle(*angle1, *angle2)
            if check_possible(eqangle) and eqangle not in self.predicates:
                self.can_deduce(eqangle)

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
