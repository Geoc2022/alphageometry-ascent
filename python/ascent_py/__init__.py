"""Python bindings for Ascent Datalog"""

from .ascent_py import GraphProgram as _GraphProgram
from typing import List, Tuple


class GraphProgram:
    """High-level Python wrapper for graph reachability queries"""

    def __init__(self):
        self._prog = _GraphProgram()

    def add_edge(self, from_node: int, to_node: int):
        """Add an edge to the graph"""
        self._prog.add_edge(from_node, to_node)

    def add_edges(self, edges: List[Tuple[int, int]]):
        """Add multiple edges at once"""
        for from_node, to_node in edges:
            self.add_edge(from_node, to_node)

    def run(self):
        """Execute the Datalog program"""
        self._prog.run()

    def get_paths(self) -> List[Tuple[int, int]]:
        """Get all computed paths"""
        return self._prog.get_paths()

    def get_edges(self) -> List[Tuple[int, int]]:
        """Get all edges"""
        return self._prog.get_edges()

    def __repr__(self):
        return f"GraphProgram(edges={len(self.get_edges())})"


__all__ = ["GraphProgram"]
