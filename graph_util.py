def get_roots(g):
    return [n for n, d in g.in_degree().items() if d == 0]
