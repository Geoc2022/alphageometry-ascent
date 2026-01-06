# Alpha Geometry DDAR with Ascent

This repository contains an implementation of Alpha Geometry, a system for developing proofs in geometry using a deductive database, algebraic reasoning, and a LLM in order to prove geometric theorems.

This implementation uses [Ascent](https://github.com/s-arash/ascent/tree/master), a logic programming language (similar to Datalog) embedded in Rust, for the deductive database component.

## Example Problem

```bash
❯ uv run solve.py problems/contri_sas
Initial Predicates:
  cong C A I G
  eqangle C A B F D E
  cong A B G H
  cong C A F D
  eqangle C A B H G I
  cong A B D E

Goals:
  contri2 A B C G H I
  contri1 A B C D E F

=== Iteration 1 ===
Predicates known: 6 / Goals Known: 0 / Goals: 2
Missing Goals:  contri2 A B C G H I contri1 A B C D E F
Found: contri1 D E F A B C via sas_cong
Found: contri2 A B C G H I via sas_cong
Added 2020 new predicates

============================================================
[1] cong C A I G                | axiom
[2] eqangle C A B F D E         | axiom
[3] cong A B G H                | axiom
[4] cong C A F D                | axiom
[5] eqangle C A B H G I         | axiom
[6] cong A B D E                | axiom
[7] eqangle B A C E D F         | sym [2]
[8] eqangle B A C I G H         | sym [5]
[9] contri1 A C B D F E         | sas_cong [2],[4],[6]
[10] contri2 G H I A B C        | sas_cong [3],[5],[1]
[11] contri1 D E F A B C        | sas_cong [7],[4],[6]
[12] contri2 A B C G H I        | sas_cong [3],[1],[8]
Solved!
```

To run all the problems in this repository use [`uv`](https://docs.astral.sh/uv/) to run:

```bash
find problems -mindepth 1 -maxdepth 1 -type d | sort | xargs -n1 -I{} bash -c 'echo -e "\n\n==> {}" && uv run solve.py "{}"'
```

## Deductive Database

Each geometric fact (`col`, `para`, etc.) is represented as a relation in Ascent, containing the fact and provenance lattice i.e. how it was derived. 

The Provenance stores all derivations for a fact:

- `axiom()` → a starting fact
- `from()` → a fact derived from other facts and a rule

Lattices allow combining multiple derivations so that we can keep track of all the ways a fact was derived. We only search for the actual derivation used in the proof when we trace the proof in `problem.py`.

### Basic Rule

Here's the symmetry rule for collinearity. `col(c, b, a)` is derived from `col(a, b, c)` using the symmetry property which is recorded in the provenance `Provenance::from("sym", vec![fact_id("col", [a, b, c])])`. We don't care how `col(a, b, c)` was derived, so we have the notation `?_prov` to ignore its provenance.

```rust
col(c, b, a, Provenance::from("sym", vec![fact_id("col", [a, b, c])]))
    <-- col(a, b, c, ?_prov);
```

### Generating from Point Existence

The reflexivity of congruence is derived trivially from point existence, so this fact has no provenance other than the rule name.

```rust
cong(a, b, a, b, Provenance::from("rfl", vec![])) <--
    point(_, _, a), point(_, _, b),
    if a != b;
```

### More Complex Rule

Here's the rule for ASA congruence. For triangles `ABC` and `DEF` to be congruent by ASA by `contri1`, we also need to check that the two triangles have the same orientation. This means that we need to check the diagram formed by points `ABC` and `DEF` to see if they are oriented the same way (both clockwise or both counterclockwise). We can access the coordinates of the points using the `point` relation and use a helper function `same_orientation` to check the orientation.

```rust
// ASA Congruence
contri1(a, b, c, d, e, f, Provenance::from("asa_cong", vec![
    fact_id("eqangle", [b, a, c, e, d, f]),
    fact_id("eqangle", [c, b, a, f, e, d]),
    fact_id("cong", [a, b, d, e])
])) <--
    eqangle(b, a, c, e, d, f, ?_prov1),
    eqangle(c, b, a, f, e, d, ?_prov2),
    cong(a, b, d, e, ?_prov3),
    point(ax, ay, a), point(bx, by, b), point(cx, cy, c),
    point(dx, dy, d), point(ex, ey, e), point(fx, fy, f),
    if same_orientation(
        vec![(*ax, *ay), (*bx, *by), (*cx, *cy)],
        vec![(*dx, *dy), (*ex, *ey), (*fx, *fy)]
    );
```
