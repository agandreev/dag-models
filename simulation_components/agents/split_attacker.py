from typing import List

import numpy as np

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.transaction import Transaction


class SplitAttacker(MaliciousAgent):
    def __init__(self, id: int, transactions_quantity: int, start_time: int, rate: int,
                 splitting_transactions_quantity: int):
        if splitting_transactions_quantity >= transactions_quantity:
            raise Exception("You should add more malicious transactions!")
        self.splitting_transactions_quantity = splitting_transactions_quantity
        simple_transactions_quantity = transactions_quantity - splitting_transactions_quantity + 1
        super(SplitAttacker, self).__init__(id, simple_transactions_quantity, start_time, rate)
        self._generate_transactions()

        self.double_spending_transactions: List['Transaction'] = list()


    def _generate_transactions(self):
        counter = 0
        cumulative_time = self.start_time
        for arrival_time in self.arrival_times:
            cumulative_time += arrival_time
            # Add splitting transactions
            if counter == 0:
                for i in range(self.splitting_transactions_quantity):
                    transaction = Transaction(self.id * 100 + counter, cumulative_time)
                    counter += 1
                    transaction.owner = self
                    self.transactions.append(transaction)
                continue
            transaction = Transaction(self.id * 100 + counter, cumulative_time)
            counter += 1
            transaction.owner = self
            self.transactions.append(transaction)
