import logging
from typing import List

from simulation_components.tangle import Tangle
from simulation_components.transaction import Transaction
from simulations.simulation import Simulation
import numpy as np
import time

BLACK = "#000000"
RED = "#FF0000"


class GhostSimulation(Simulation):
    def __init__(self,
                 transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_delay: float,
                 ghost_rate: int,
                 validation_quantity: int):
        if ghost_rate > transaction_rate:
            raise Exception("Ghost rate should be > than transaction rate")
        super().__init__(transactions_quantity, agents_quantity, transaction_rate, network_delay, validation_quantity)
        self.free_tips: List['Transaction'] = list()
        self.ghost_rate = 1 / ghost_rate
        self.update_mc_time = self.ghost_rate

    def setup(self) -> None:
        self.generate_agents()
        self.generate_arrival_times()
        self.dag = Tangle(self.arrival_times)

        # Initializing weights for each agent
        for agent in self.agents:
            for transaction in self.dag.transactions:
                transaction.weight_for_each_agent[agent] = 1

        # Initializing owner for each transaction except genesis
        for transaction in self.dag.transactions[1:]:
            transaction.owner = np.random.choice(self.agents)

    def run(self) -> None:
        print(self.arrival_times)
        print(self.update_mc_time)
        current_time = time.process_time()

        for transaction in self.dag.transactions[1:]:
            print(f"transaction {transaction.id} is running")
            if transaction.time > self.update_mc_time:
                self.update_mc_time += self.ghost_rate
                self._update_main_chain(self.dag.transactions[0])

            # plot transaction
            color = transaction.owner.color
            y_axis = np.random.uniform(0, 1) - transaction.owner.id * 1.3
            self.dag.tangle.add_node(transaction,
                                     pos=(transaction.time, y_axis),
                                     node_color=color)

            self._urtc_selection(transaction)

        self.final_time = time.process_time() - current_time
        print(self.final_time)

    # todo: maybe add quantity of relations
    def _urtc_selection(self, transaction: 'Transaction') -> None:
        tips = self._get_existing_transactions_for_agent(self.dag.transactions[0])

        validated_tips = set()
        validated_tips.add(np.random.choice(tips, 1)[0])

        self.dag.add_edges(validated_tips, transaction)
        self.edge_colors.append(BLACK)

    # _get_existing_transactions_for_agent searchs for free tips. append the last mc and it's predecessors
    def _get_existing_transactions_for_agent(self, current_transaction) -> List['Transaction']:
        predecessors = list(self.dag.tangle.predecessors(current_transaction))
        for predecessor in predecessors:
            if predecessor.is_mc:
                return self._get_existing_transactions_for_agent(predecessor)
        free_tips = list()
        free_tips.append(current_transaction)
        for predecessor in predecessors:
            if predecessor.owner == current_transaction.owner:
                continue
            free_tips.extend(self._get_existing_transactions_for_agent(predecessor))
        return free_tips

    def _update_main_chain(self, start_transaction):
        logging.info("start main chain updating")
        predecessors = list(self.dag.tangle.predecessors(start_transaction))
        if len(predecessors) != 0:
            for predecessor in predecessors:
                if predecessor.is_mc:
                    return self._update_main_chain(predecessor)
            weights = list()
            for predecessor in predecessors:
                weights.append(self.dag.count_final_weight(predecessor))
            mc_transaction = predecessors[weights.index(max(weights))]
            mc_transaction.is_mc = True
            self.edge_colors[mc_transaction.id - 1] = RED
            print(f"main chain is updated by {mc_transaction.id}")
