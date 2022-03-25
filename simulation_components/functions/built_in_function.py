import numpy as np

from typing import List

from simulation_components.agents.agent import Agent
from simulation_components.transaction import Transaction


def calc_exponential_transition(alpha, walker: 'Transaction',
                                walker_validators: List['Transaction'],
                                agent: 'Agent', walkers_weights) -> np.ndarray:
    # todo: add time checking
    walker_validators_weights = np.array([walker_validator.weight_for_each_agent[agent]
                                          for walker_validator in walker_validators])
    walker_validators_weights = walker_validators_weights - np.max(walker_validators_weights)
    return np.divide(np.exp(walker_validators_weights * alpha),
                     np.sum(np.exp(walker_validators_weights * alpha)))
