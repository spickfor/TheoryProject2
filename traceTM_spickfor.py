import csv

def parse_csv(file_path):
    """Parse the NTM definition from a CSV file."""
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        name = next(reader)[0]                  # Name of machine
        states = next(reader)[0].split(',')     # List of our States
        sigma = next(reader)[0].split(',')      # The input alphabet
        gamma = next(reader)[0].split(',')      # Tape alphabet
        start_state = next(reader)[0]
        accept_state = next(reader)[0]
        reject_state = next(reader)[0]
        
        # Read the transition rules
        transitions = []
        for row in reader:
            if row:
                transitions.append(tuple(row))
        
    return name, states, sigma, gamma, start_state, accept_state, reject_state, transitions


def simulate_ntm(file_path, input_string, max_depth=20, output_file="trace_output.txt"):
    """Simulate the NTM on the given input and write trace to a file."""
    name, states, sigma, gamma, start_state, accept_state, reject_state, transitions = parse_csv(file_path)
    
    # Prepare output file
    with open(output_file, 'w') as file:
        file.write(f"Machine: {name}\n")
        file.write(f"Input String: {input_string}\n\n")
    
    print(f"Machine: {name}")
    print(f"Input String: {input_string}")

    # Init configurations: a list of (left, current state, right)
    configurations = [[("", start_state, input_string)]]
    transition_count = 0  # Initialize transition count
    non_leaf_count = 0  # Initialize non-leaf count

    # Create a set of explicitly defined (state, head) pairs
    explicit_transitions = {(t[0], t[1]) for t in transitions}

    for depth in range(max_depth):
        new_configurations = []
        for config in configurations[-1]:
            left, state, right = config

            if state == accept_state:
                # Prepare accept message
                msg = (
                    f"Depth of Tree of configurations: {depth}\n"
                    f"Accepted in {depth} transitions.\n\n"
                )
                # Print and write to file
                print(msg)
                write_to_file(output_file, msg)
                print_trace(configurations, transition_count, non_leaf_count, output_file)
                return
            if state == reject_state:
                transition_count += 1  # Count transitions leading to a reject state
                continue  # Skip rejected branches

            head = right[0] if right else "_"  # Read the current symbol (default to blank)
            branch_has_transitions = False  # Track if this config has outgoing transitions

            # Check for explicit transitions for this (state, head)
            for t in transitions:
                t_state, t_head, t_new_state, t_write, t_move = t
                if t_state == state and t_head == head:
                    branch_has_transitions = True  # Mark this as a non-leaf node
                    if t_move == "R":  # Move right
                        new_left = left + t_write  # Append current head symbol to left tape
                        new_right = right[1:] if len(right) > 1 else "_"  # Remove first character from right
                    elif t_move == "L":  # Move left
                        # Apply write operation to the current head position
                        new_right = t_write + (right[1:] if len(right) > 1 else "")
                        if len(left) > 0:
                            new_left = left[:-1]  # Remove last character of left
                            new_right = left[-1] + new_right  # Prepend last character of left to right
                        else:
                            new_left = ""  # If left is empty, keep it empty
                    else:  # Stay in place
                        new_left = left
                        new_right = t_write + (right[1:] if len(right) > 1 else "")  # Update first symbol of right

                    # Save new configuration for the next depth
                    new_configurations.append((new_left, t_new_state, new_right))
                    transition_count += 1  # Increment transition count

            # Handle implicit transitions to the reject state
            if (state, head) not in explicit_transitions:
                transition_count += 1  # Count the implicit transition to the reject state
                branch_has_transitions = True  # Implicit reject transitions also count for non-leaf determination

            # Increment non-leaf count if there are outgoing transitions
            if branch_has_transitions:
                non_leaf_count += 1

        # If no new configurations generated, halt machine w/o accepting
        if not new_configurations:
            msg = (
                f"Rejected in {depth} transitions.\n"
                f"Depth of Tree of configurations: {depth}\n\n"
            )
            # Print and write to file
            print(msg)
            write_to_file(output_file, msg)
            print_trace(configurations, transition_count, non_leaf_count, output_file)
            return

        configurations.append(new_configurations)

    print("Max depth reached. Halting simulation.")
    write_trace(configurations, transition_count, non_leaf_count, output_file)


def write_trace(configurations, transition_count, non_leaf_count, output_file):
    """Write the trace of configurations to a file."""
    trace_output = "Trace:\n"
    for depth, configs in enumerate(configurations):
        trace_output += f"Depth {depth}:\n"
        for config in configs:
            trace_output += f"  {config}\n"
    trace_output += f"Total transitions: {transition_count}\n"
    trace_output += f"Total non-leaf nodes: {non_leaf_count}\n"
    if non_leaf_count > 0:
        nondeterminism = transition_count / non_leaf_count
        trace_output += f"Nondeterminism: {nondeterminism:.2f}\n"
    else:
        trace_output += "Nondeterminism: Undefined (no non-leaf nodes)\n"
    trace_output += "==============================================\n"

    print(trace_output)  # Ensure the trace is printed to the console
    write_to_file(output_file, trace_output)


def write_to_file(output_file, content):
    """Write content to the specified output file."""
    with open(output_file, 'a') as file:
        file.write(content)


def print_trace(configurations, transition_count, non_leaf_count, output_file=None):
    """Print the trace of configurations, total transitions, and nondeterminism."""
    trace_output = "Trace:\n"
    for depth, configs in enumerate(configurations):
        trace_output += f"Depth {depth}:\n"
        for config in configs:
            trace_output += f"  {config}\n"
    trace_output += f"Total transitions: {transition_count}\n"
    trace_output += f"Total non-leaf nodes: {non_leaf_count}\n"
    if non_leaf_count > 0:
        nondeterminism = transition_count / non_leaf_count
        trace_output += f"Nondeterminism: {nondeterminism:.2f}\n"
    else:
        trace_output += "Nondeterminism: Undefined (no non-leaf nodes)\n"
    trace_output += "==============================================\n"

    print(trace_output)
    if output_file:
        write_to_file(output_file, trace_output)


if __name__ == "__main__":
    simulate_ntm("check_a_plus_spickfor.csv", "aaa", output_file="output_a_plus_spickfor.txt")


    simulate_ntm("check_a_plus_DTM_spickfor.csv","aaa", output_file= "output_a_plus_DTM_spickfor.txt")
    simulate_ntm("check_palindrome_DTM_spickfor.csv","aaabbbaaa", output_file="output_palindrome_DTM_spickfor.txt")
    simulate_ntm("check_palindrome_spickfor.csv","aaabbbaaa", output_file="output_palindrome_spickfor.txt")
    # simulate_ntm("check_palindrome_spickfor.csv","abbaabbaabbaabba", output_file="output_palindrome_spickfor.txt")
    simulate_ntm("check_2x0_DTM_spickfor.csv","000011", output_file="output_2x0_DTM_spickfor.txt")


    # simulate_ntm("check_abc_star_spickfor.csv", "abc", output_file="output_abc_star_spickfor.txt")
    simulate_ntm("check_abc_star_spickfor.csv", "abbbcccccc", output_file="output_abc_star_spickfor.txt")
    # simulate_ntm("check_abc_star_spickfor.csv", "acb", output_file="output_abc_star_spickfor.txt")
