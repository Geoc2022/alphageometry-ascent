from ascent_py import GraphProgram


def main():
    # Create a new graph program
    prog = GraphProgram()

    # Add edges
    prog.add_edges([(1, 2), (2, 3), (3, 4), (1, 5), (5, 6)])

    # Run the Datalog program
    prog.run()

    # Get results
    paths = prog.get_paths()
    print(f"Found {len(paths)} paths:")
    for from_node, to_node in sorted(paths):
        print(f"  {from_node} -> {to_node}")


if __name__ == "__main__":
    main()
