from typing import List, Tuple
import re
import inspect
import relations
from relations import Predicate, Point


def _build_predicate_registry():
    """
    Automatically build a registry of predicate classes from relations.py.
    Returns a dict mapping lowercase predicate names to (class, arity) tuples.
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

            # Register using lowercase class name
            key = name.lower()
            registry[key] = (obj, arity)

    return registry


_PREDICATE_REGISTRY = _build_predicate_registry()


def _normalize_predicate_name(name: str) -> str:
    key = name.strip().lower()
    return key


def _instantiate_predicate(name: str, args, points: dict) -> Predicate:
    """Create a Predicate instance from a name and a list of point-name args."""

    key = _normalize_predicate_name(name)
    if key not in _PREDICATE_REGISTRY:
        raise ValueError(
            f"Unknown predicate '{name}'. Supported: {sorted(_PREDICATE_REGISTRY.keys())}"
        )

    cls, arity = _PREDICATE_REGISTRY[key]
    arg_list = [a for a in args if a != ""]

    if len(arg_list) != arity:
        raise ValueError(
            f"Predicate '{name}' expects {arity} arguments, got {len(arg_list)}: {arg_list}"
        )

    try:
        pts = [Point(name=sym, x=points[sym][0], y=points[sym][1]) for sym in arg_list]
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(
            f"Point '{missing}' not found in provided points dictionary."
        ) from None

    return cls(*pts)


def parse_string(problem: str, points: dict) -> Tuple[List[Predicate], List[Predicate]]:
    # Do NOT collapse or strip out tabs/newlines/etc.
    text = problem

    # Split on ';' and drop empty segments
    segments = [seg.strip() for seg in text.split(";") if seg.strip() != ""]
    if not segments:
        raise ValueError("No predicate segments found.")

    premises: List[Predicate] = []
    goals: List[Predicate] = []

    for raw in segments:
        is_goal = raw.startswith("?")
        clause = raw[1:].strip() if is_goal else raw.strip()

        # Allow commas OR any whitespace (space/tab/newline) between tokens
        parts = re.split(r"[,\s]+", clause)
        if not parts:
            raise ValueError(f"Empty clause found: '{raw}'")

        name, *args = parts
        pred = _instantiate_predicate(name, args, points)

        if is_goal:
            goals.append(pred)
        else:
            premises.append(pred)

    return premises, goals
