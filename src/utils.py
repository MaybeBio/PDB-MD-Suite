# some utility functions defined

from click import Tuple


def consolidate_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Description
    -----------
    Consolidate a list of tuple ranges into a list of non-overlapping ranges, and sort in ascending order

    Args
    ----
    ranges: list[tuple[int, int]]
        A list of tuple ranges, e.g. [(1, 5), (3, 7), (10, 12)]

    Returns
    -------
    list[tuple[int, int]]: A list of non-overlapping ranges, sorted in ascending order
    
    """
    if not ranges:
        return []
    # first sort the ranges by the start value in ascending order
    ranges.sort(key=lambda x: x[0])
    # start with the first range
    consolidated = [ranges[0]]
    # start comparison
    for current in ranges[1:]:
        previous = consolidated[-1]
        if current[0] <= previous[1] + 1:
            previous[1] = max(previous[1], current[1])
        else:
            consolidated.append(current)
    return consolidated

    
