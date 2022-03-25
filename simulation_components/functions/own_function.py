import numpy as np

from typing import List

from simulation_components.agents.agent import Agent
from simulation_components.transaction import Transaction


def calc_own_transition(alpha, walker: 'Transaction',
                                walker_validators: List['Transaction'],
                                agent: 'Agent', walkers_weights) -> np.ndarray:
    # todo: add time checking
    dimension = len(walker_validators)
    walker_validators_array = np.ones(dimension)
    return np.divide(walker_validators_array,
                     dimension)