# Alpha Geometry DDAR with Ascent

This repository contains an implementation of Alpha Geometry, a system for developing proofs in geometry using a deductive database, algebraic reasoning, and a LLM in order to prove geometric theorems.

This implementation uses [Ascent](https://github.com/s-arash/ascent/tree/master), a logic programming language (similar to Datalog) embedded in Rust, for the deductive database component.

To run all the problems in this repository use [`uv`](https://docs.astral.sh/uv/) to run:

```bash
find problems -mindepth 1 -maxdepth 1 -type d | sort | xargs -n1 -I{} bash -c 'echo -e "\n\n==> {}" && uv run solve.py "{}"'
```

## TODO

Some deductions are listed as axioms when they are derived by AR
