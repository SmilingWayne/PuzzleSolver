import math
from typing import List, Tuple

def check_square_num(target: int):
    val = int(math.sqrt(target))
    if  val * val == target:
        return True
    return False
    

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


def convert_str_to_int(s):
    if isinstance(s, int):
        return s
    elif isinstance(s, str):
        if s.isdigit() and len(s) == 1:
            return int(s)
        elif s.isalpha() and len(s) == 1:
            s = s.lower()
            return ord(s) - ord('a') + 1
        else:
            return -1
    else:
        return -1
    