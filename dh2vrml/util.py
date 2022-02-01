import random
from typing import Tuple

def rand_color() -> Tuple[float, float, float]:
    return (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))