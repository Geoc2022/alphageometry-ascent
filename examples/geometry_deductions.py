"""
Geometric Deduction Example using Ascent

This example demonstrates how Ascent can discover geometric relationships
through logical deduction rules. We'll prove properties of a parallelogram.
"""

from ascent_py import GeometryProgram


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

    prog = GeometryProgram()

    prog.add_point("A", 0, 0)
    prog.add_point("B", 4, 0)
    prog.add_point("C", 5, 3)
    prog.add_point("D", 1, 3)

    print("Given facts:")
    print(" - AB || CD (opposite sides parallel)")
    print(" - BC || DA (opposite sides parallel)")
    print()

    # Add parallelogram properties as facts
    prog.add_parallel("A", "B", "C", "D")  # AB || CD
    prog.add_parallel("B", "C", "D", "A")  # BC || DA

    # Run deduction engine
    prog.run()

    # Display deduced parallel relationships
    print("Deduced Parallel Relationships:")
    parallels = prog.get_parallel()
    unique_parallels = set()
    for a, b, c, d in parallels:
        # Normalize to avoid duplicates
        pair1 = tuple(sorted([a + b, c + d]))
        if pair1 not in unique_parallels:
            unique_parallels.add(pair1)
            print(f" - {a}{b} || {c}{d}")
    print()

    # Display deduced congruent segments
    print("Deduced Congruent Segments:")
    congruents = prog.get_congruent()
    unique_congs = set()
    for a, b, c, d in congruents:
        # Normalize to avoid duplicates
        seg1 = tuple(sorted([a, b]))
        seg2 = tuple(sorted([c, d]))
        pair = tuple(sorted([seg1, seg2]))
        if pair not in unique_congs:
            unique_congs.add(pair)
            print(f" - {a}{b} ≅ {c}{d}")
    print()

    # Display deduced equal angles
    print("Deduced Equal Angles:")
    angles = prog.get_equal_angles()
    unique_angles = set()
    for a, b, c, d, e, f in angles:
        angle_pair = (f"{a}{b}{c}", f"{d}{e}{f}")
        norm_pair = tuple(sorted(angle_pair))
        if norm_pair not in unique_angles:
            unique_angles.add(norm_pair)
            print(f" - ∠{a}{b}{c} = ∠{d}{e}{f}")
    print()

    # Display congruent triangles if any
    print("Deduced Congruent Triangles:")
    congruent_triangles = prog.get_congruent_triangles()
    for a, b, c, d, e, f in congruent_triangles:
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

    prog = GeometryProgram()

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

    # Add equal angles (AA criterion)
    prog.add_equal_angle("C", "A", "B", "F", "D", "E")  # ∠CAB = ∠FDE
    prog.add_equal_angle("B", "C", "A", "E", "F", "D")  # ∠BCA = ∠EFD

    # Run deduction engine
    prog.run()

    # Display similar triangles
    print("Deduced Similar Triangles:")
    similar = prog.get_similar_triangles()
    for a, b, c, d, e, f in similar:
        print(f" - △{a}{b}{c} ~ △{d}{e}{f}")
    print()

    # Display congruent triangles if any
    print("Deduced Congruent Triangles:")
    congruent = prog.get_congruent_triangles()
    for a, b, c, d, e, f in congruent:
        print(f" - △{a}{b}{c} ≅ △{d}{e}{f}")
    print()

    # Display all deduced equal angles (including symmetric ones)
    print("All Deduced Equal Angles:")
    angles = prog.get_equal_angles()
    shown = set()
    for a, b, c, d, e, f in angles:
        key = tuple(sorted([f"{a}{b}{c}", f"{d}{e}{f}"]))
        if key not in shown:
            shown.add(key)
            print(f" - ∠{a}{b}{c} = ∠{d}{e}{f}")
    print()


def transitive_parallel_example():
    """
    Demonstrate parallel line transitivity:
    If AB || CD and AB || EF, then CD || EF
    """
    print("=" * 50)
    print("PARALLEL LINE TRANSITIVITY")
    print("=" * 50)
    print()

    prog = GeometryProgram()

    # Define points
    for point in ["A", "B", "C", "D", "E", "F"]:
        prog.add_point(point)

    print("Given facts:")
    print(" - AB || CD")
    print(" - AB || EF")
    print()

    # Add parallel facts
    prog.add_parallel("A", "B", "C", "D")
    prog.add_parallel("A", "B", "E", "F")

    # Run deduction engine
    prog.run()

    # Display all deduced parallels
    print("Deduced Parallel Relationships:")
    parallels = prog.get_parallel()
    shown = set()
    for a, b, c, d in parallels:
        key = tuple(sorted([tuple(sorted([a, b])), tuple(sorted([c, d]))]))
        if key not in shown:
            shown.add(key)
            print(f" - {a}{b} || {c}{d}")

    print()
    print("✓ Successfully deduced: CD || EF (by transitivity)")
    print()


def main():
    """Run all geometry deduction examples"""
    parallelogram_example()
    triangle_similarity_example()
    transitive_parallel_example()

    print("=" * 50)
    print("All geometric deductions completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
