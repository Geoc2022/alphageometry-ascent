from ascent_py import DeductiveDatabase


def flatten(data):
    result = []
    for item in data:
        if isinstance(item, tuple):
            result.extend(flatten(item))
        else:
            result.append(item)
    return tuple(result)


def unique_para(parallels):
    unique = set()
    for a, b, c, d in parallels:
        seg1 = tuple(sorted([a, b]))
        seg2 = tuple(sorted([c, d]))
        if seg1 == seg2:
            continue
        pair = tuple(sorted([seg1, seg2]))
        unique.add(flatten(pair))
    return unique


def unique_cong(congruents):
    unique = set()
    for a, b, c, d in congruents:
        seg1 = tuple(sorted([a, b]))
        seg2 = tuple(sorted([c, d]))
        if seg1 == seg2:
            continue
        pair = tuple(sorted([seg1, seg2]))
        unique.add(flatten(pair))
    return unique


def unique_angles(angles):
    unique = set()
    for a, b, c, d, e, f in angles:
        if (a, b, c) == (d, e, f):
            continue
        norm_pair = tuple(sorted([(a, b, c), (d, e, f)]))
        unique.add(flatten(norm_pair))
    return unique


def unique_triangles(triangles):
    unique = set()
    for a, b, c, d, e, f in triangles:
        if (a, b, c) == (d, e, f):
            continue
        norm_pair = tuple(sorted([(a, b, c), (d, e, f)]))
        unique.add(flatten(norm_pair))
    return unique


def parallelogram_example():
    """
    Prove properties of parallelogram ABCD where:
    - AB || CD (opposite sides parallel)
    - BC || DA (opposite sides parallel)

    The system should deduce:
    - AB ≅ CD (opposite sides congruent)
    - BC ≅ DA (opposite sides congruent)
    - Various equal angles
    """
    print("=" * 50)
    print("PARALLELOGRAM PROPERTY DEDUCTION")
    print("=" * 50)
    print()

    prog = DeductiveDatabase()

    prog.add_point("A", 0, 0)
    prog.add_point("B", 4, 0)
    prog.add_point("C", 5, 3)
    prog.add_point("D", 1, 3)

    print("Given facts:")
    print(" - AB || CD (opposite sides parallel)")
    print(" - BC || DA (opposite sides parallel)")
    print()

    prog.add_parallel("A", "B", "C", "D")
    prog.add_parallel("B", "C", "D", "A")

    prog.run()

    print("Deduced Parallel Relationships:")
    parallels = prog.get_parallel()
    for a, b, c, d in unique_para(parallels):
        print(f" - {a}{b} || {c}{d}")
    print()

    print("Deduced Congruent Segments:")
    congruents = prog.get_congruent()
    for a, b, c, d in unique_cong(congruents):
        print(f" - {a}{b} ≅ {c}{d}")
    print()

    print("Deduced Equal Angles:")
    angles = prog.get_equal_angle()
    for a, b, c, d, e, f in unique_angles(angles):
        print(f" - ∠{a}{b}{c} = ∠{d}{e}{f}")
    print()

    print("Deduced Congruent Triangles:")
    congruent_triangles = prog.get_congruent_triangles()
    for a, b, c, d, e, f in unique_triangles(congruent_triangles):
        print(f" - △{a}{b}{c} ≅ △{d}{e}{f}")
    print()


def triangle_similarity_example():
    """
    Demonstrate AA similarity criterion:
    If two angles of triangle ABC equal two angles of triangle DEF,
    then the triangles are similar.
    """
    print("=" * 50)
    print("TRIANGLE SIMILARITY (AA CRITERION)")
    print("=" * 50)
    print()

    prog = DeductiveDatabase()

    prog.add_point("A", 0, 0)
    prog.add_point("B", 1, 0)
    prog.add_point("C", 0, 1)
    prog.add_point("D", 0, 0)
    prog.add_point("E", 2, 0)
    prog.add_point("F", 0, 2)

    print("Given facts:")
    print(" - ∠CAB = ∠FDE (angle at A equals angle at D)")
    print(" - ∠BCA = ∠EFD (angle at C equals angle at F)")
    print()

    prog.add_equal_angle("C", "A", "B", "F", "D", "E")
    prog.add_equal_angle("B", "C", "A", "E", "F", "D")

    prog.run()

    print("Deduced Similar Triangles:")
    similar = prog.get_similar_triangles()
    for a, b, c, d, e, f in unique_triangles(similar):
        print(f" - △{a}{b}{c} ~ △{d}{e}{f}")
    print()

    print("Deduced Congruent Triangles:")
    congruent = prog.get_congruent_triangles()
    for a, b, c, d, e, f in unique_triangles(congruent):
        print(f" - △{a}{b}{c} ≅ △{d}{e}{f}")
    print()

    print("All Deduced Equal Angles:")
    angles = prog.get_equal_angle()
    for a, b, c, d, e, f in unique_angles(angles):
        print(f" - ∠{a}{b}{c} = ∠{d}{e}{f}")
    print()


def transitive_parallel_example():
    """
    Demonstrate parallel line transitivity:
    If AB || CD and AB || EF, then CD || EFF
    """
    print("=" * 50)
    print("PARALLEL LINE TRANSITIVITY")
    print("=" * 50)
    print()

    prog = DeductiveDatabase()

    for point in ["A", "B", "C", "D", "E", "F"]:
        prog.add_point(point)

    print("Given facts:")
    print(" - AB || CD")
    print(" - AB || EF")
    print()

    prog.add_parallel("A", "B", "C", "D")
    prog.add_parallel("A", "B", "E", "F")

    prog.run()

    print("Deduced Parallel Relationships:")
    parallels = prog.get_parallel()
    for a, b, c, d in unique_para(parallels):
        print(f" - {a}{b} || {c}{d}")
    print()


def main():
    """Run all geometry deduction examples"""
    parallelogram_example()
    triangle_similarity_example()
    transitive_parallel_example()


if __name__ == "__main__":
    main()
