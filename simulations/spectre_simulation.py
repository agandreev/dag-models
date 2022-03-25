import logging
from typing import List

from simulation_components.tangle import Tangle
from simulation_components.transaction import Transaction
from simulations.simulation import Simulation
import numpy as np
import time
import networkx as nx

BLACK = "#000000"
RED = "#FF0000"

class Spectre(Simulation):
    def __init__(self,
                 transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_delay: float,
                 spectre_rate: int,
                 validation_quantity: int):
        if spectre_rate > transaction_rate:
            raise Exception("Ghost rate should be > than transaction rate")
        super().__init__(transactions_quantity, agents_quantity, transaction_rate, network_delay, validation_quantity)
        self.free_tips: List['Transaction'] = list()

        self.spectre_rate = 1 / spectre_rate
        self.voting_time = self.spectre_rate
        self.voices = None

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
        current_time = time.process_time()

        for transaction in self.dag.transactions[1:]:
            print(f"transaction {transaction.id} is running")
            # if transaction.time > self.voting_time:
            #     self.voting_time += self.spectre_rate
            #     self._update_main_chain(self.dag.transactions[0])

            # plot transaction
            color = transaction.owner.color
            y_axis = np.random.uniform(0, 1) - transaction.owner.id * 1.3
            self.dag.tangle.add_node(transaction,
                                     pos=(transaction.time, y_axis),
                                     node_color=color)

            self._urtc_selection(transaction, self.validation_quantity)

        self.final_time = time.process_time() - current_time
        print(self.final_time)
        # self.voices = self._voting()
        # print(self.voices)
        # print(len(self.voices))

    def _urtc_selection(self, transaction: 'Transaction', n: int) -> None:
        self._get_existing_transactions_for_agent(transaction)
        tips = self._get_not_approved_transactions(transaction)

        validated_tips = set()
        for i in range(n):
            validated_tips.add(np.random.choice(tips, 1)[0])

        self.dag.add_edges(validated_tips, transaction)
        self.edge_colors.append(BLACK)

    def _get_not_approved_transactions(self, current_transaction: 'Transaction') \
            -> List['Transaction']:
        not_approved_transactions = list()

        agent = current_transaction.owner

        # Add to valid tips if transaction has no approvers at all
        for transaction in agent.existing_transactions:
            if len(list(self.dag.tangle.predecessors(transaction))) == 0:
                not_approved_transactions.append(transaction)
            # Add to valid tips if all approvers not visible yet
            elif (set(list(self.dag.tangle.predecessors(transaction))).
                    issubset(set(agent.not_existing_transaction))):
                not_approved_transactions.append(transaction)

        return not_approved_transactions

    def _get_existing_transactions_for_agent(self, current_transaction: 'Transaction') \
            -> None:
        # Clear transaction's lists
        for agent in self.agents:
            agent.clear_transactions_lists()
        # Loop through all transactions in DAG
        for transaction in self.dag.tangle.nodes:
            if transaction.owner is None and transaction.id != 0:
                continue
            # For EACH agent record the currently visible and not visible transactions
            for agent in self.agents:
                # Genesis always visible
                if transaction.time == 0:
                    agent.existing_transactions.append(transaction)
                else:
                    # Get distance from agent to agent of transaction from distance matrix
                    if transaction.time + \
                            self.network_delay <= current_transaction.time:
                        agent.existing_transactions.append(transaction)

                    elif current_transaction.owner == agent:
                        current_transaction.owner.not_existing_transaction.append(transaction)

    def _voting(self):
        voices = dict()
        # for i in range(len(self.dag.transactions)):
        #     for j in range(len(self.dag.transactions)):
        #         # unique voter's pairs
        #         if i > j:
        #             x_transaction = self.dag.transactions[i]
        #             y_transaction = self.dag.transactions[j]
        #
        #             self._init_voting(voices, x_transaction, y_transaction)

        x_transaction = self.dag.transactions[3]
        y_transaction = self.dag.transactions[30]

        self._init_voting(voices, x_transaction, y_transaction)

        return voices

    def _init_voting(self, voices, x, y):
        # x_parents = list(self.dag.tangle.predecessors(x))
        # for z in x_parents:
        #     self._easy_vote(voices, z, x, y)
        # y_parents = list(self.dag.tangle.predecessors(y))
        # for z in y_parents:
        #     self._easy_vote(voices, z, x, y)

        voices[x.id] = {(x.id, y.id): 1}
        voices[y.id] = {(x.id, y.id): -1}
        self._rec_easy_vote(voices, x, x, y)
        self._rec_easy_vote(voices, y, x, y)

        print(voices)
        tips = list()
        for t in list(nx.ancestors(self.dag.tangle, self.dag.transactions[0])):
            if len(list(self.dag.tangle.predecessors(t))) == 0:
                tips.append(t)
        for t in tips:
            self._rec_middle_vote(voices, t, x, y, list([]))

    def _rec_easy_vote(self, voices, z, x, y):
        parents = list(self.dag.tangle.predecessors(z))
        for z in parents:
            self._easy_vote(voices, z, x, y)
            self._rec_easy_vote(voices, z, x, y)

    def _easy_vote(self, voices, z, x, y):
        if z.id in voices:
            if (x.id, y.id) in voices[z.id]:
                return
        if len(list(self.dag.tangle.predecessors(z))) == 0:
            voices[z.id] = {(x.id, y.id): 0}
            return
        if z in nx.ancestors(self.dag.tangle, x):
            if z not in nx.ancestors(self.dag.tangle, y):
                voices[z.id] = {(x.id, y.id): -1}
                return
            return
        if z in nx.ancestors(self.dag.tangle, y):
            if z not in nx.ancestors(self.dag.tangle, x):
                voices[z.id] = {(x.id, y.id): 1}
                return
            return

    def _rec_middle_vote(self, voices, z, x, y, rec_id):
        parents = list(self.dag.tangle.successors(z))
        for z in parents:
            self._middle_vote(voices, z, x, y, rec_id)
            self._rec_middle_vote(voices, z, x, y, rec_id)

    def _middle_vote(self, voices, z, x, y, rec_id):
        if z == x or z == y:
            return
        if z.id in voices:
            if (x.id, y.id) in voices[z.id]:
                return
        if z in nx.ancestors(self.dag.tangle, x) and z in nx.ancestors(self.dag.tangle, y):
            succ = list(self.dag.tangle.successors(z))
            if len(succ) == 0:
                voices[z.id] = {(x.id, y.id): 0}
                return
            for s in succ:
                preds = list(self.dag.tangle.predecessors(s))
                if len(preds) <= 1:
                    continue
                for p in preds:
                    if p == z or (z not in nx.ancestors(self.dag.tangle, x) and z not in nx.ancestors(self.dag.tangle, y)):
                        continue
                    if p in rec_id:
                        break
                    rec_id.append(p)
                    if p.id in voices:
                        if (x.id, y.id) in voices[p.id]:
                            voices[z.id] = {(x.id, y.id): voices[p.id][(x.id, y.id)]}
                            return
                        else:
                            self._middle_vote(voices, p, x, y, rec_id)
                            voices[z.id] = {(x.id, y.id): voices[p.id][(x.id, y.id)]}
                            return
                    else:
                        self._middle_vote(voices, p, x, y, rec_id)
                        voices[z.id] = {(x.id, y.id): voices[p.id][(x.id, y.id)]}
                        return
                continue
            voices[z.id] = {(x.id, y.id): 0}
        voices[z.id] = {(x.id, y.id): 0}