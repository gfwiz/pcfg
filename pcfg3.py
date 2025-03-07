from collections import defaultdict

def inside_algorithm(sentence, cfg, probabilities):
    n = len(sentence)
    alpha = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    non_terminals = list(cfg['N'])

    #Base case 
    for i in range(n):
        for A in non_terminals:
            rule = (A, sentence[i])
            if rule in probabilities:
                alpha[A][i][i] = probabilities[rule]

    #Recursive case
    for span in range(2, n+1):
        for i in range(n-span+1):
            j = i + span - 1
            for A in non_terminals:
                for (B, C) in cfg['NT'].get(A, []): 
                    for k in range(i, j):
                        rule = (A, B, C)
                        alpha[A][i][j] += probabilities.get(rule, 0) * alpha[B][i][k] * alpha[C][k+1][j]
                        print(f"Inside Prob for {A} to {(B,C)}: {alpha[A][i][j]}")
    return alpha

def outside_algorithm(sentence, cfg, probabilities, alpha):
    n = len(sentence)
    beta = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    non_terminals = list(cfg['N'])
    beta[cfg['S']][0][n-1] = 1.0

    #Recursive case
    for span in range(n, 0, -1):
        for i in range(n-span+1):
            j = i + span - 1
            for A in non_terminals:
                if span < n: 
                    for (B, C) in cfg['NT'].get(A, []): 
                        for k in range(i):
                            beta[A][i][j] += probabilities.get((B, C, A), 0) * beta[B][k][j] * alpha[C][i][k]
                        for k in range(j+1, n):
                            beta[A][i][j] += probabilities.get((B, A, C), 0) * beta[B][i][k] * alpha[C][j+1][k]
    return beta

def em(corpus, cfg, initial_probabilities, max_iterations=30):
    probabilities = initial_probabilities.copy()
    
    for iteration in range(max_iterations):
        expected_counts = defaultdict(float)
        total_counts = defaultdict(float)

        # Expectation step
        for sentence in corpus:
            alpha = inside_algorithm(sentence, cfg, probabilities)
            beta = outside_algorithm(sentence, cfg, probabilities, alpha)

            for A in cfg['NT']:  # Iterate over non-terminals
                for rhs in cfg['NT'][A]:  # Get expansions which are tuples (B, C)
                    B, C = rhs
                    rule = (A, B, C)  # Construct the rule tuple as expected
                    if rule in probabilities:  # Check if rule is in probabilities to handle both terminal and non-terminal
                        for i in range(len(sentence)):
                            for j in range(i, len(sentence)):
                                for k in range(i, j):
                                    rule_prob = probabilities.get(rule, 0)  # Safely get rule probability
                                    count = beta[A][i][j] * rule_prob * alpha[B][i][k] * alpha[C][k+1][j]
                                    expected_counts[rule] += count
                                    total_counts[A] += count
                        print(f"Rule: {rule}, Expected Count: {expected_counts[rule]}, Total Count: {total_counts[A]}")

        # Maximization step: Update rule probabilities
        for rule in probabilities.keys():  # Iterate over all rules
            if isinstance(rule, tuple) and len(rule) == 3:
                A, B, C = rule
                if total_counts[A] > 0:
                    probabilities[rule] = expected_counts[rule] / total_counts[A]
                    print(f"Updating Rule: {rule} to {probabilities[rule]}")  # Debugging output
            elif isinstance(rule, tuple) and len(rule) == 2:
                A, x = rule
                if total_counts[A] > 0:
                    probabilities[rule] = expected_counts[rule] / total_counts[A]
                    print(f"Updating Rule: {rule} to {probabilities[rule]}")  # Debugging output

    return probabilities

# Example grammar and potential functions initialization
cfg = {
    'N': {'S', 'VP', 'N', 'V'},  # Non-terminals
    'Σ': {'Mary', 'John', 'saw', 'him'},  # Terminals
    'NT': {  # Non-terminal rules organized in a dictionary
        'S': [('N', 'VP')],
        'VP': [('V', 'N')]
    },
    'T': {  # Terminal rules (these would be part of probability definitions normally)
        ('N', 'John'),
        ('N', 'Mary'),
        ('V', 'saw'),
        ('N', 'him')
    },
    'S': 'S'  # Start symbol
}

# Initial probabilities for each rule (corrected to match expanded structure)
rule_probabilities = {
    ('S', 'N', 'VP'): 0.5,
    ('VP', 'V', 'N'): 0.1,
    ('N', 'John'): 0.1,
    ('N', 'Mary'): 0.1,
    ('V', 'saw'): 0.1,
    ('N', 'him'): 0.1
}

# Example sentences
corpus = [
    ['Mary', 'saw', 'him'],
    ['John', 'saw', 'Mary']
]

# Run the EM algorithm to update rule probabilities
updated_probabilities = em(corpus, cfg, rule_probabilities)
print(updated_probabilities)
