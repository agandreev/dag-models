import networkx as nx
import numpy as np
import warnings
from typing import List
from simulation_components.transaction import Transaction

warnings.filterwarnings("ignore")


class Tangle:
    def __init__(self, arrival_times: List[float]):
        self.tangle: 'nx.DiGraph' = nx.DiGraph()
        self.transactions: List['Transaction'] = list()
        self.init_root()
        self.generate_transactions(arrival_times)

    def init_root(self) -> None:
        root: 'Transaction' = Transaction(0, 0)
        root.is_mc = True
        self.transactions.append(root)
        self.tangle.add_node(root, pos=(0, 0), node_color="black")

    def generate_transactions(self, arrival_times: List[float]) -> None:
        transaction_counter = 1
        arrival_time = 0
        for time in arrival_times:
            arrival_time = time + arrival_time
            self.transactions.append(Transaction(transaction_counter, arrival_time))
            transaction_counter += 1

    def add_node(self, transaction: 'Transaction') -> None:
        self.tangle.add_node(transaction)

    def add_edges(self, tips: List['Transaction'], validator: Transaction) -> None:
        for tip in tips:
            self.tangle.add_edge(validator, tip)

    def count_final_weight(self, transaction: 'Transaction'):
        final_weight = 0

        if self.tangle.has_node(transaction):
            validators = \
                list(self.tangle.predecessors(transaction))
        else:
            validators = list()

        if len(validators) == 0:
            return 1

        for validator in validators:
            final_weight += self.count_final_weight(validator)

        return final_weight + 1

    def save_cumulative_weights(self):
        file = open("cumulative_weights.csv", "w")
        file.close()
        file = open("cumulative_weights.csv", "a")
        for transaction in self.transactions:
            transaction_info = f"{transaction.id};{self.count_final_weight(transaction)}\n"
            file.write(transaction_info)
        file.close()

    def save_time(self, final_time: float) -> None:
        file = open("result.txt", "w")
        file.write(str(round(final_time, 5)) + "\n")
        file.close()

    def save_attack_result(self, legitimate_transaction, fake_transaction) -> None:
        file = open("result.txt", "a")
        file.write(str(self.count_final_weight(legitimate_transaction)) + "\n")
        file.write(str(self.count_final_weight(fake_transaction)) + "\n")
        file.close()
