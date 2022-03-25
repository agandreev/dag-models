import numpy as np

from simulation_components.agents.agent import Agent
from simulation_components.transaction import Transaction

from typing import List


class MaliciousAgent(Agent):
    def __init__(self, id: int, transactions_quantity: int, start_time: int, rate: int):
        super().__init__(id)
        self.transactions_quantity = transactions_quantity
        self.transactions: List['Transaction'] = list()
        self.start_time = start_time
        self.rate = rate
        self.color = "#FFFF00"
        self.arrival_times = self._generate_exponential_arrival_times()

    def _generate_exponential_arrival_times(self):
        return np.random.exponential(1 / self.rate, self.transactions_quantity)



