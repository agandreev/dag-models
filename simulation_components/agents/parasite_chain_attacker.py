import numpy as np

from typing import List

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.transaction import Transaction


class ParasiteChainAttacker(MaliciousAgent):
    def __init__(self, id: int, transaction_quantity: int, start_time: int, reference_quantity: int,
                 rate: int, confirmation_delay: int):
        super(ParasiteChainAttacker, self).__init__(id, transaction_quantity,
                                                    start_time, rate)
        self.reference_quantity = reference_quantity
        self.confirmation_delay = confirmation_delay

        self._generate_transactions()
        self.r_transaction = None

    def _generate_transactions(self):
        counter = 0
        self.arrival_times += self.confirmation_delay
        self.arrival_times = np.insert(self.arrival_times,
                                       0,
                                       self.arrival_times[0] - self.confirmation_delay)
        cumulative_time = self.start_time
        for arrival_time in self.arrival_times:
            cumulative_time += arrival_time
            transaction = Transaction(self.id * 100 + counter, cumulative_time)
            counter += 1
            transaction.owner = self
            self.transactions.append(transaction)
