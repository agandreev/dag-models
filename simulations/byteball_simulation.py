from typing import List

from simulation_components.agents.agent import Agent
from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.tangle import Tangle
from simulation_components.transaction import Transaction
from simulations.simulation import Simulation
import numpy as np
import time
import networkx as nx

BLACK = "#000000"
RED = "#FF0000"
YELLOW = "#FFFF00"

DOUBLE = "double"
CHAIN = "chain"


class Byteball(Simulation):
    def __init__(self,
                 transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_delay: float,
                 witness_quantity: int,
                 validation_quantity: int,
                 attack: 'Byteball_attack'):
        super().__init__(transactions_quantity, agents_quantity + 1, transaction_rate, network_delay,
                         validation_quantity)
        if witness_quantity > agents_quantity:
            raise Exception("witness quantity should be less than agents quantity")
        self.witness_quantity = witness_quantity
        self.attack = attack
        self.malicious_agent = None

    def setup(self) -> None:
        self.generate_agents()
        for i in range(self.witness_quantity):
            self.agents[i].is_witness = True
        self.generate_arrival_times()
        self.dag = Tangle(self.arrival_times)
        self.dag.transactions[0].owner = self.agents[len(self.agents) - 1]

        # Initializing weights for each agent
        for agent in self.agents:
            for transaction in self.dag.transactions:
                transaction.weight_for_each_agent[agent] = 1

        # Initializing owner for each transaction except genesis
        for transaction in self.dag.transactions[1:]:
            transaction.owner = np.random.choice(self.agents)

        if self.attack is not None:
            print("here")
            self.malicious_agent = Agent(len(self.agents))
            self.agents.append(self.malicious_agent)
            self.malicious_agent.color = YELLOW
            if self.attack.attack_type == DOUBLE:
                time = 0
                for transaction in self.dag.transactions:
                    if transaction.id / self.transactions_quantity > self.attack.attack_time_perc:
                        time = transaction.time
                        break
                arrival_times = np.random.exponential(1 / self.attack.transaction_rate, 2)
                for i in range(2):
                    time += arrival_times[i]
                    tx = Transaction(len(self.dag.transactions), time)
                    tx.owner = self.malicious_agent
                    self.dag.transactions.append(tx)
            self.dag.transactions.sort(key=lambda tx: tx.time)

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
        self._build_mc()
        self._set_mci()
        self._review()
        self.edge_colors = self._get_edge_colors()

    def _urtc_selection(self, transaction: 'Transaction', n: int) -> None:
        self._get_existing_transactions_for_agent(transaction)
        tips = self._get_not_approved_transactions(transaction)

        validated_tips = set()
        for i in range(n):
            validated_tips.add(np.random.choice(tips, 1)[0])

        self.dag.add_edges(validated_tips, transaction)

        # bp = self._define_best_parent(validated_tips)
        # self.dag.add_edges([bp], transaction)
        # self.edge_colors.append(RED)
        #
        # self.dag.add_edges(set(validated_tips) - set([bp]), transaction)
        # self.edge_colors.append(BLACK)

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

    def _define_best_parent(self, validated_tips: List['Transaction']) -> Transaction:
        validated_tips = list(validated_tips)
        validated_tips.sort(key=sort_by_id)
        witness_counters = list()
        for tip in validated_tips:
            descs = nx.descendants(self.dag.tangle, tip)
            witness_counter = 0
            for desc in descs:
                if desc.owner.is_witness:
                    witness_counter += 1
            witness_counters.append(witness_counter)
        max_witness = validated_tips[witness_counters.index(max(witness_counters))]
        return max_witness

    def _build_mc(self):
        tips = list()
        for t in self.dag.transactions:
            if len(nx.ancestors(self.dag.tangle, t)) == 0:
                tips.append(t)
        for t in tips:
            self._recursive_bp(t)

    def _recursive_bp(self, t: 'Transaction'):
        # get parents
        succ = list(self.dag.tangle.successors(t))
        if len(list(succ)) == 0:
            return
        bp = self._define_best_parent(succ)
        bp.is_mc = True
        bp.last_mc.add(t)
        self._recursive_bp(bp)

    def _get_edge_colors(self):
        edges = self.dag.tangle.edges
        return [RED if u.is_mc and v.is_mc and u in v.last_mc else BLACK for u, v in edges]

    def _drop_mc(self):
        for transacion in self.dag.transactions:
            transacion.is_mc = False
            transacion.last_mc = set()
            transacion.mci = 0

    # def _setup_attack(self):
    #     if self.attack.attack_type == DOUBLE:

    def _set_mci(self):
        if len(self.dag.transactions) == 0:
            return
        preds = self.dag.tangle.predecessors(self.dag.transactions[0])
        self.dag.transactions[0].mci = 0
        self._mci_rec(preds, 0)

        self._set_mci_rec(self.dag.transactions[0])

    def _mci_rec(self, txs, index):
        for tx in txs:
            if tx.is_mc:
                tx.mci = index
                self._mci_rec(self.dag.tangle.predecessors(tx), index + 1)

    def _set_mci_rec(self, tx: 'Transaction'):
        if not tx.is_mc:
            return
        for anc in nx.descendants(self.dag.tangle, tx):
            if anc.mci == -1:
                anc.mci = tx.mci
        if len(tx.last_mc) == 0:
            return
        if len(tx.last_mc) > 1:
            return
        for mc in tx.last_mc:
            self._set_mci_rec(mc)
        # self._set_mci_rec(tx.last_mc[0])

    def _review(self):
        file = open("review.csv", "w")
        file.close()
        file = open("review.csv", "a")
        file.write("id;is_mc;is_witness;mci;\n")
        txs = self.dag.transactions.copy()
        txs.sort(key=lambda x: x.id)
        for transaction in txs:
            transaction_info = f"{transaction.id};{transaction.is_mc};" \
                               f"{transaction.owner.is_witness};{transaction.mci};{transaction.last_mc};\n"
            file.write(transaction_info)
        file.close()


def sort_by_id(tx: 'Transaction'):
    return tx.id


class Byteball_attack:
    def __init__(self, attack_type: str, attack_time_perc: float, transaction_rate: float):
        # todo: add checking
        self.attack_type: str = attack_type
        self.attack_time_perc: float = attack_time_perc
        self.transaction_rate: float = transaction_rate
