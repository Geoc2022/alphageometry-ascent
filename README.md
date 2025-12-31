# Alpha Geometry DDAR with Ascent

This repository contains an implementation of Alpha Geometry, a system for developing proofs in geometry using a deductive database, algebraic reasoning, and a LLM in order to prove geometric theorems.

This implementation uses [Ascent](https://github.com/s-arash/ascent/tree/master), a logic programming language (similar to Datalog) embedded in Rust, for the deductive database component.

To run all the problems in this repository use [`uv`](https://docs.astral.sh/uv/) to run:

```bash
find problems -mindepth 1 -maxdepth 1 -type d | sort | xargs -n1 -I{} bash -c 'echo -e "\n\n==> {}" && uv run solve.py "{}"'
```

## Deductive Database

Each geometric relation (`col`, `para`, etc.) is represented as a lattice in Ascent, containing the fact and provenance i.e. how it was derived. 

The Provenance struct stores all derivations for a fact:

- `axiom()` → a starting fact
- `from()` → a fact derived from other facts and a rule

Lattices allow combining multiple derivations so that we can keep track of all the ways a fact was derived. We only search for the actual derivation when we trace the proof in `problem.py`.

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
