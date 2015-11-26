# Algorithm for maximum coverage problem


def maximum_k_coverage(sets, k):
    covered = set()
    selected_sets = []
    if k >= len(sets):
        return sets
        
    for i in xrange(k):
        max_set = max(sets, key=lambda s: len(s - covered))
        selected_sets.append(max_set)
        covered |= max_set
    return selected_sets
        
