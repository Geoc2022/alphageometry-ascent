"""
Geometric Deduction Example using Ascent

This example demonstrates how Ascent can discover geometric relationships
through logical deduction rules. We'll prove properties of a parallelogram
and a cyclic quadrilateral.
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
    print("=" * 70)
    print("PARALLELOGRAM PROPERTY DEDUCTION")
    print("=" * 70)
    print()

    prog = GeometryProgram()

    # Define points
    for point in ["A", "B", "C", "D"]:
        prog.add_point(point)

    print("Given facts:")
    print("  • AB || CD (opposite sides parallel)")
    print("  • BC || DA (opposite sides parallel)")
    print()

    # Add parallelogram properties as facts
    prog.add_parallel("A", "B", "C", "D")  # AB || CD
    prog.add_parallel("B", "C", "D", "A")  # BC || DA

    # Run deduction engine
    prog.run()

    # Display deduced parallel relationships
    print("Deduced Parallel Relationships:")
    parallels = prog.get_parallel()
    shown = set()
    for a, b, c, d in parallels:
        key = tuple(sorted([tuple(sorted([a, b])), tuple(sorted([c, d]))]))
        if key not in shown:
            shown.add(key)
            print(f"  • {a}{b} || {c}{d}")
    print()

    # Display deduced equal angles
    print("Deduced Equal Angles:")
    angles = prog.get_equal_angles()
    shown = set()
    for a, b, c, d, e, f in angles:
        # Normalize representation
        key = tuple(sorted([f"{a}{b}{c}", f"{d}{e}{f}"]))
        if key not in shown:
            shown.add(key)
            print(f"  • ∠{a}{b}{c} = ∠{d}{e}{f}")
    print()


def cyclic_quadrilateral_example():
    """
    Demonstrate Cyclic Quadrilateral Properties:
    Given points A, B, C, D are cyclic (lie on a circle).

    The system should deduce "Angles Subtended by the Same Arc":
    - ∠ADB = ∠ACB (Subtended by arc AB)
    - ∠DAC = ∠DBC (Subtended by arc DC)
    """
    print("=" * 70)
    print("CYCLIC QUADRILATERAL DEDUCTION")
    print("=" * 70)
    print()

    prog = GeometryProgram()
    for point in ["A", "B", "C", "D"]:
        prog.add_point(point)

    print("Given facts:")
    print("  • Points A, B, C, D are cyclic")
    print()

    prog.add_cyclic("A", "B", "C", "D")
    prog.run()

    print("Deduced Equal Angles (Butterfly Theorem / Same Arc):")
    angles = prog.get_equal_angles()
    shown = set()
    for a, b, c, d, e, f in angles:
        key = tuple(sorted([f"{a}{b}{c}", f"{d}{e}{f}"]))
        if key not in shown:
            shown.add(key)
            print(f"  • ∠{a}{b}{c} = ∠{d}{e}{f}")


if __name__ == "__main__":
    parallelogram_example()
    print("\n\n")
    cyclic_quadrilateral_example()
