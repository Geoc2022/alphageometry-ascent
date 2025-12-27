"""Deduction module using Ascent datalog database."""

from python.ascent_py import DeductiveDatabase
from relations import Point, Predicate
import relations
import inspect


def _build_predicate_registry():
    """
    Automatically build a registry of predicate classes from relations.py.
    Returns a dict mapping lowercase predicate names to (class, arity, db_method) tuples.
    """
    registry = {}

    # Get all classes from the relations module
    for name, obj in inspect.getmembers(relations, inspect.isclass):
        # Only include classes that are subclasses of Predicate (but not Predicate itself or Point)
        if issubclass(obj, Predicate) and obj is not Predicate:
            # Get the __init__ signature to determine arity
            sig = inspect.signature(obj.__init__)
            # Count parameters excluding 'self'
            params = [p for p in sig.parameters.values() if p.name != "self"]
            arity = len(params)

            registry[name.lower()] = (obj, arity, name.lower())

    return registry


_PREDICATE_REGISTRY = _build_predicate_registry()


class DD:
    """
    Manages the Ascent datalog deductive database for geometric reasoning.
    Maintains correspondence between Point objects and their string names.
    """

    def __init__(self, points: set[Point], initial_predicates: set[Predicate]):
        """
        Initialize the deductive database with points and initial predicates.

        Args:
            points: Set of Point objects in the geometry
            initial_predicates: Set of initial Predicate facts
        """
        self.db = DeductiveDatabase()

        self.point_by_name: dict[str, Point] = {}
        self.name_by_point: dict[Point, str] = {}

        for point in points:
            self._add_point(point)

        for predicate in initial_predicates:
            self.add_predicate(predicate)

        self.db.run()

        self._extracted_predicates: set[Predicate] = set()

    def _add_point(self, point: Point):
        """Add a point to the database and maintain mappings."""
        if point not in self.name_by_point:
            x = int(point.x * 100)
            y = int(point.y * 100)
            self.db.add_point(x, y, point.name)
            self.point_by_name[point.name] = point
            self.name_by_point[point] = point.name

    def add_point(self, point: Point):
        """
        Add a new point to the database (for future extensibility).
        Must call run() after adding points to deduce new facts.
        """
        self._add_point(point)

    def add_predicate(self, predicate: Predicate):
        """
        Add a predicate to the deductive database.
        Must call run() after adding predicates to deduce new facts.
        """
        if not predicate._init_args:
            return

        pred_type = type(predicate).__name__.lower()

        if pred_type not in _PREDICATE_REGISTRY:
            return

        _, expected_arity, db_method = _PREDICATE_REGISTRY[pred_type]

        if len(predicate._init_args) == expected_arity:
            # Extract point names from the init args
            point_names = [pt.name for pt in predicate._init_args]
            # Get the database method (e.g., db.add_collinear)
            method = getattr(self.db, f"add_{db_method}")
            method(*point_names)

    def run(self):
        """Run the datalog deduction engine."""
        self.db.run()

    def get_new_deductions(self) -> set[Predicate]:
        """
        Extract newly deduced predicates from the database.
        Only returns predicates that haven't been extracted before.

        Returns:
            Set of newly deduced Predicate objects
        """
        new_predicates = set()

        # Build extractors dynamically from registry
        for pred_name, (pred_class, arity, db_method) in _PREDICATE_REGISTRY.items():
            # Get the database getter method (e.g., db.get_collinear)
            getter = getattr(self.db, f"get_{db_method}")
            data = getter()

            for item in data:
                pred = self._extract_predicate(pred_class, item)
                if pred not in self._extracted_predicates:
                    new_predicates.add(pred)
                    self._extracted_predicates.add(pred)

        return new_predicates

    def _extract_predicate(
        self, pred_class: type, point_names: tuple[str, ...]
    ) -> Predicate:
        """
        Extract a predicate from database results.

        Args:
            pred_class: The Predicate class to instantiate
            point_names: Tuple of point names from database

        Returns:
            Instantiated Predicate object
        """
        points = [self.point_by_name[name] for name in point_names]
        return pred_class(*points)


def deduce_from_datalog(problem) -> set[Predicate]:
    """
    Run the datalog deductive database and return all newly deduced predicates.

    This is the main deduction function called by the solver.

    Args:
        problem: Problem instance with a dd attribute

    Returns:
        Set of newly deduced Predicate objects
    """
    # Run the deduction engine
    problem.dd.run()

    # Extract and return new deductions
    return problem.dd.get_new_deductions()


# Export the deduction functions list for the solver
functions = [deduce_from_datalog]
