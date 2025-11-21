import math
from typing import List, Tuple

def get_factor_pairs(target: int) -> List[Tuple[int, int]]:
    """
    Get all factor pair (x, y) such that x * y = target
    """
    if target <= 0:
        return []
    
    result = []
    for i in range(1, int(math.sqrt(target)) + 1):
        if target % i == 0:
            j = target // i
            result.append((i, j))
            if i != j:
                result.append((j, i))
    return result
