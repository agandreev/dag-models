from typing import List

import networkx as nx

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.transaction import Transaction


class OutpaceAttacker(MaliciousAgent):
    def __init__(self, id: int, transactions_quantity: int, start_time: int, rate: int,
                 confirmation_delay: int):
        super(OutpaceAttacker, self).__init__(
            id, transactions_quantity, start_time, rate)
        self.confirmation_delay = confirmation_delay
        self.connected_transaction: 'Transaction' = None
        self.outpace_graph: 'nx.DiGraph' = nx.DiGraph()
        self._generate_transactions()
        self.confirmation_value = confirmation_delay + self.transactions[0].time
        self.is_composed = False
        self.is_legitimate_sended = False
        self.sended_malicious_transactions: List['Transaction'] = list()

    def _generate_transactions(self):
        counter = 0
        cumulative_time = self.start_time
        for arrival_time in self.arrival_times:
            # Add legitimate transaction
            cumulative_time += arrival_time
            transaction = Transaction(self.id * 100 + counter, cumulative_time)
            counter += 1
            transaction.owner = self
            self.transactions.append(transaction)
