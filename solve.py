import sys
import read_in_relations
import geogebra
import constructions
import dd
from problem import Problem
from relations import Point


def construct_problem(
    ggb_file: str = "",
    problem_file: str = "",
    problem_str: str = "",
    plot: bool = False,
) -> Problem:
    """
    Construct a geometry problem either from:
      - manual mode (problem_str provided), or
      - file mode (ggb_file + problem_file).
    """
    if problem_str:
        points = {}
        for section in problem_str.split(";"):
            section = section.strip()
            if not section:
                continue
            tokens = section.split()
            for token in tokens[1:]:
                if token.isalpha():
                    points[token] = (0.0, 0.0)  # dummy coords

        predicates, goals = read_in_relations.parse_string(problem_str, points)

    else:
        points, lines, circles = geogebra.parse_picture(ggb_file)

        if plot:
            constructions.plot(points, lines, circles)

        with open(problem_file, "r") as f:
            predicates, goals = read_in_relations.parse_string(f.read(), points)

    points = {Point(name=k, x=v[0], y=v[1]) for k, v in points.items()}

    return Problem(set(predicates), set(goals), points)


def prove(problem: Problem):
    if problem.is_solved():
        print("Already solved!")
        return

    changed = True
    iteration = 0
    max_iterations = 3

    print("Initial Predicates:")
    for pred in problem.predicates:
        print(f"  {pred}")
    print("\nGoals:")
    for goal in problem.goals:
        print(f"  {goal}")

    while changed and not problem.is_solved() and iteration < max_iterations:
        iteration += 1
        print(f"\n=== Iteration {iteration} ===")
        missing_goals = [
            goal for goal in problem.goals if goal not in problem.predicates
        ]
        print(
            f"Predicates known: {len(problem.predicates)} / Goals Known: {len(problem.goals) - len(missing_goals)} / Goals: {len(problem.goals)}"
        )
        print("Missing Goals: ", " ".join(str(goal) for goal in missing_goals))

        previous_count = len(problem.predicates)

        for deduction_fn in dd.functions:
            deduction_fn(problem)

        if not problem.is_solved():
            problem.search_ar()

        problem.flush_deductions()

        changed = len(problem.predicates) > previous_count

        if changed:
            print(f"Added {len(problem.predicates) - previous_count} new predicates")

    print("\n" + "=" * 60)
    if iteration >= max_iterations:
        print(f"Stopped after {max_iterations} iterations")

    print(problem)
    if problem.is_solved():
        print("\x1b[32mSolved!\x1b[0m")
    else:
        print("\x1b[31mCould not solve the problem.\x1b[0m")
        exit(1)


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python solve.py <problem_directory> [--plot]")
        print('  python solve.py -manual "<problem_string>"')
        sys.exit(1)

    plot_flag = "--plot" in args

    if "-manual" in args:
        try:
            idx = args.index("-manual")
            problem_str = args[idx + 1]
        except IndexError:
            print("Error: You must provide a problem string after -manual.")
            sys.exit(1)

        problem = construct_problem(problem_str=problem_str, plot=False)

    else:
        problem_dir = args[0]
        ggb_file = f"{problem_dir}/problem.ggb"
        problem_file = f"{problem_dir}/problem.txt"

        problem = construct_problem(
            ggb_file=ggb_file, problem_file=problem_file, plot=plot_flag
        )

    prove(problem)


if __name__ == "__main__":
    main()
