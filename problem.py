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
    predicates: dict[Predicate, list[Deduction]]
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
        self.dd = DD(points, set())
        self.ar = AR()
        self.deductions_buffer = []
        self.possible_relations = set()
        self.impossible_relations = set()

        for predicate in predicates:
            if predicate.is_valid():
                self._add_predicate(predicate, set(), "axiom")
            else:
                raise ValueError(f"Invalid initial predicate: {predicate}")

    def add_deduction(self, deduction: Deduction):
        """Add a predicate to the deductions buffer."""
        self.deductions_buffer.append(deduction)

    def flush_deductions(self):
        """Flush the deductions buffer and add predicates to the problem and DD."""
        for deduction in self.deductions_buffer:
            self._add_predicate(
                deduction.predicate, deduction.parent_predicates, deduction.rule_name
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

    def _add_predicate(
        self,
        predicate: Predicate,
        parent_predicates: set[Predicate],
        rule_name: str = "unknown",
    ):
        if predicate in self.goals:
            print(f"\x1b[34mFound: {predicate}\x1b[0m via {rule_name}")
        for sub in predicate.to_sub_data():
            if sub.predicate in self.goals:
                print(
                    f"\x1b[34mFound: {sub.predicate}\x1b[0m as part of {predicate} via {rule_name}"
                )
        if predicate not in self.predicates:
            self.predicates[predicate] = []

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

        # Store this derivation path
        deduction = Deduction(predicate, parent_predicates, rule_name)
        if deduction not in self.predicates[predicate]:
            self.predicates[predicate].append(deduction)
        self.dd.add_predicate(deduction.predicate)
        self.ar.add_predicate(deduction.predicate)

        # Handle sub-predicates
        for sub_deduction in predicate.to_sub_data():
            if sub_deduction.predicate not in self.predicates:
                self.predicates[sub_deduction.predicate] = []

            sub_ded = Deduction(
                sub_deduction.predicate,
                sub_deduction.parent_predicates,
                "sub_deduction",
            )
            if sub_ded not in self.predicates[sub_deduction.predicate]:
                self.predicates[sub_deduction.predicate].append(sub_ded)
            self.dd.add_predicate(sub_ded.predicate)

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
        Uses smart derivation selection during topological sort.
        """
        if not self.is_solved():
            return ""

        if not self.goals:
            return "No goals specified"

        RULE_PRIORITY = {
            "axiom": 0,
            "rfl": 1,
            "sub_deduction": 2,
            "AR": 10,
            "sym": 20,
        }

        def get_priority(rule_name: str) -> int:
            return RULE_PRIORITY.get(rule_name, 5)

        def find_reachable_predicates():
            """Find all predicates reachable from goals."""
            reachable = set()
            to_visit = set(self.goals)

            while to_visit:
                current = to_visit.pop()
                if current in reachable:
                    continue

                reachable.add(current)
                if current in self.predicates:
                    for deduction in self.predicates[current]:
                        new_parents = deduction.parent_predicates - reachable
                        to_visit.update(new_parents)

            return reachable

        goal_reachable_predicates = find_reachable_predicates()

        # Check for unreachable goals
        unreachable_goals = self.goals - goal_reachable_predicates
        if unreachable_goals:
            return f"Unreachable goals: {' '.join([str(goal) for goal in unreachable_goals])}"

        # Select best derivation for each predicate using topological sort
        selected_derivations: dict[Predicate, Deduction] = {}
        used_predicates = set()
        ordered_predicates: list[tuple[Predicate, Deduction]] = []

        # Start with axioms
        for pred, deductions in self.predicates.items():
            if pred not in goal_reachable_predicates:
                continue
            axiom_deductions = [d for d in deductions if len(d.parent_predicates) == 0]
            if axiom_deductions:
                best = min(axiom_deductions, key=lambda d: get_priority(d.rule_name))
                selected_derivations[pred] = best
                used_predicates.add(pred)
                ordered_predicates.append((pred, best))

        # Topological sort with smart derivation selection
        prev_used_count = -1
        while any(goal not in used_predicates for goal in self.goals):
            current_count = len(used_predicates)
            if current_count == prev_used_count:
                remaining_goals = [
                    goal for goal in self.goals if goal not in used_predicates
                ]
                raise RuntimeError(
                    f"Cannot complete proof - unreachable goals: {remaining_goals}"
                )
            prev_used_count = current_count

            for predicate, deductions in self.predicates.items():
                if predicate not in goal_reachable_predicates:
                    continue
                if predicate in used_predicates:
                    continue

                # Find all valid derivations (where all parents are already proven)
                valid_derivations = [
                    d
                    for d in deductions
                    if all(parent in used_predicates for parent in d.parent_predicates)
                ]

                if valid_derivations:
                    # Select best derivation by rule priority
                    best = min(
                        valid_derivations, key=lambda d: get_priority(d.rule_name)
                    )
                    selected_derivations[predicate] = best
                    used_predicates.add(predicate)
                    ordered_predicates.append((predicate, best))

        # Build output
        numbering: dict[Predicate, int] = {}
        for i, (predicate, _) in enumerate(ordered_predicates):
            numbering[predicate] = i + 1

        lines = []

        for predicate, deduction in ordered_predicates:
            num = numbering[predicate]
            padded_pred = f"{str(predicate):<25}"
            pred = (
                padded_pred
                if predicate not in self.goals
                else f"\x1b[32m{padded_pred}\x1b[0m"
            )
            parents = (
                ""
                if not deduction.parent_predicates
                else ",".join(f"[{numbering[p]}]" for p in deduction.parent_predicates)
            )

            rule = f"{deduction.rule_name}" if deduction.rule_name != "unknown" else ""
            line = f"[{num}] {pred}\t| {rule} {parents}"

            lines.append(line)

        return "\n".join(lines)
