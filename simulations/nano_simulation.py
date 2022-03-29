from typing import List

from simulation_components.agents.agent import Agent
from simulation_components.tangle import Tangle
from simulation_components.transaction import Transaction, NanoTX, SEND, RECEIVE
from simulations.simulation import Simulation
from operator import add
import numpy as np
import time
import networkx as nx

BLACK = "#000000"
RED = "#FF0000"
BLUE = "#00ff00"
GREEN = "#008000"
YELLOW = "#FFFF00"


class Nano(Simulation):
    def __init__(self,
                 transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_delay: float,
                 validation_quantity: int,
                 rec_threshold: float,
                 repr_quantity: int,
                 attack_time_percentage: float,
                 rounds_quantity,
                 rounds_duration,
                 agent_delay):
        super().__init__(transactions_quantity,
                         agents_quantity,
                         transaction_rate,
                         network_delay,
                         validation_quantity)
        self.rec_threshold = rec_threshold
        if repr_quantity > agents_quantity:
            raise Exception("quantity of representatives should be less or equals to agents quantity")
        if 0 > attack_time_percentage > 1:
            raise Exception("attack time should be in borders [0; 1]")
        if rounds_quantity < 0:
            raise Exception("rounds quantity should be more than zero")
        self.attack_time_percentage = attack_time_percentage
        self.repr_quantity = repr_quantity
        self.rounds_quantity = rounds_quantity
        self.round = Round(rounds_quantity, rounds_duration, network_delay, agent_delay)

        self._fork_counter = 0

    def setup(self) -> None:
        self.generate_agents()
        self.generate_arrival_times()
        self.dag = Tangle(self.arrival_times)
        self.dag.tangle = nx.DiGraph()
        self.dag.transactions = self.dag.transactions[1:]
        receive_TXs = list()
        last_tx_time = self.dag.transactions[len(self.dag.transactions) - 1].time
        is_malicious = False
        for transaction in self.dag.transactions:
            transaction.owner = np.random.choice(self.agents)
            transaction.owner.balance /= 2
            transaction.balance = -transaction.owner.balance
            transaction.__class__ = NanoTX
            transaction.type = SEND
            if transaction.time / last_tx_time > self.attack_time_percentage and not is_malicious:
                transaction.is_malicious = True
                is_malicious = True
            receive_TXs.append(transaction)
        for tx in self.dag.transactions:
            new_tx = NanoTX(tx.id + self.transactions_quantity, tx.time + np.random.random() * self.rec_threshold)
            new_tx.owner = np.random.choice(self.agents)
            new_tx.balance = -tx.balance
            new_tx.type = RECEIVE
            new_tx.parent = tx
            receive_TXs.append(new_tx)
            if tx.is_malicious:
                new_tx.is_fork = True
                new_tx.balance = -tx.balance
                new_tx = NanoTX(tx.id + self.transactions_quantity, tx.time + np.random.random() * self.rec_threshold)
                if receive_TXs[len(receive_TXs) - 1].owner == tx.owner:
                    new_tx.owner = np.random.choice(self.agents)
                else:
                    new_tx.owner = tx.owner
                new_tx.type = RECEIVE
                new_tx.parent = tx
                new_tx.is_fork = True
                receive_TXs.append(new_tx)
        self.dag.transactions = receive_TXs
        self.dag.transactions.sort(key=sort_by_time)

        for i in range(len(self.agents)):
            if i < self.repr_quantity:
                self.agents[i].is_repr = True
                self.agents[i].repr = self.agents[i]
            else:
                self.agents[i].repr = np.random.choice(self.agents[:self.repr_quantity])

        self.round.generate_representative_delay_matrix(self.repr_quantity)

        file = open("review.csv", "w")
        file.write("agent_id;agent_repr_id;\n")
        for agent in self.agents:
            if agent.is_repr:
                continue
            file.write(f"{agent.id};{agent.repr.id};\n")
            print(f"agent {agent.id} repr's: {agent.repr.id}")
        print()
        file.close()

    def run(self) -> None:
        current_time = time.process_time()

        for transaction in self.dag.transactions:
            print(f"transaction {transaction.id} is running")
            # if transaction.time > self.voting_time:
            #     self.voting_time += self.spectre_rate
            #     self._update_main_chain(self.dag.transactions[0])

            # plot transaction
            color = ""
            if transaction.type == SEND:
                color = BLUE
            if transaction.type == RECEIVE:
                color = GREEN
            if transaction.is_malicious:
                color = YELLOW
            y_axis = 1 - transaction.owner.id * 1.3
            self.dag.tangle.add_node(transaction,
                                     pos=(transaction.time, y_axis),
                                     node_color=color)

            self._urtc_selection(transaction, self.validation_quantity)

        self.final_time = time.process_time() - current_time
        print(self.final_time)

        # print(self.get_balance(self.dag.transactions[len(self.dag.transactions) - 1].owner, self.dag.transactions[len(self.dag.transactions) - 1]))
        # for tx in self.dag.transactions[len(self.dag.transactions) - 1].owner.recent_txs:
        #     print(f"{tx.id} : {tx.balance}")
        # print(self.dag.transactions[len(self.dag.transactions) - 1].owner.balance)

        print("balances")
        total = 0
        for agent in self.agents:
            tx = None
            if len(agent.recent_txs) != 0:
                tx = agent.recent_txs[len(agent.recent_txs) - 1]
            total += self.get_balance(agent, tx)
            print(f"agent {agent.id} balance is {self.get_balance(agent, tx)}")
        print(f"total: {total}")
        total = 0
        for agent in self.agents:
            nt = 0
            for tx in agent.recent_txs:
                if tx.type == RECEIVE:
                    nt += tx.balance
            nt += agent.balance
            total += nt
            print(f"agent {agent.id} balance is {nt}")
        print(f"total: {total}")

    def _urtc_selection(self, transaction: 'Transaction', n: int) -> None:
        if transaction.type == RECEIVE:
            self.dag.add_edges([transaction], transaction.parent)
        if len(transaction.owner.recent_txs) != 0:
            self.dag.add_edges([transaction.owner.recent_txs[len(transaction.owner.recent_txs) - 1]], transaction)
        transaction.owner.recent_txs.append(transaction)

        if transaction.is_fork:
            self._fork_counter += 1
            if self._fork_counter == 2:
                print("start voting")
                first_tx = transaction
                for tx in self.dag.tangle.successors(transaction.parent):
                    if tx != first_tx and tx.type == RECEIVE:
                        second_tx = tx
                self.start_voting(first_tx, second_tx)

    def _get_edge_colors(self):
        edges = self.dag.tangle.edges
        return [RED if u.is_mc and v.is_mc else BLACK for u, v in edges]

    def start_voting(self, first_tx, second_tx):
        file = open("review.csv", "a")
        file.write("id;votes;\n")
        file.close()

        self.update_balances()
        voting = dict()
        for round_i in range(self.rounds_quantity):
            if round_i == 0:
                for agent_i in range(len(self.agents)):
                    if not self.agents[agent_i].is_repr:
                        break
                    voting[agent_i] = self._first_vote(self.agents[agent_i], first_tx, second_tx)
            self._compare_votes(voting)
            self._review(voting)

    def _first_vote(self, repr: 'Agent', first_tx, second_tx):
        self._update_repr_balance(repr)
        print(repr.repr_balance)
        if first_tx.owner.repr == repr and second_tx.owner.repr == repr:
            if first_tx.owner == first_tx.parent:
                return [0, repr.repr_balance]
            return [repr.repr_balance, 0]
        if first_tx.owner.repr == repr:
            return [repr.repr_balance, 0]
        if second_tx.owner.repr == repr:
            return [0, repr.repr_balance]
        return [repr.repr_balance / 2, repr.repr_balance / 2]

    def _compare_votes(self, voting):
        for k, v in voting.items():
            repr_ids_order = list()
            for i in range(self.repr_quantity):
                if self.round.repr_matrix[k, i] != 0 and self.round.repr_matrix[k, i] < self.round.duration:
                    repr_ids_order.append(i)
            for i in repr_ids_order:
                if v[0] == v[1]:
                    if voting[i][0] == voting[i][1]:
                        return
                    elif v[0] < sum(voting[i]):
                        if voting[i][0] == 0:
                            voting[k] = [0, sum(v)]
                        else:
                            voting[k] = [sum(v), 0]
                if voting[i][0] == voting[i][1]:
                    voting[i][1] = 0
                if sum(v) < sum(voting[i]):
                    if voting[i][0] == 0:
                        voting[k] = [0, sum(v)]
                    else:
                        voting[k] = [sum(v), 0]
        # for k, v in voting.items():
        #     for _k, _v in voting.items():
        #         if k == _k:
        #             continue
        #         if self.round.repr_matrix[k, _k] < self.round.duration:
        #             if sum(v) < sum(_v):
        #                 if _v[0] == 0:
        #                     voting[k] = [0, sum(v)]
        #                 else:
        #                     voting[k] = [sum(v), 0]

    def update_balances(self):
        for agent in self.agents:
            if len(agent.recent_txs) == 0:
                agent.total = agent.balance
                continue
            last_tx = agent.recent_txs[len(agent.recent_txs) - 1]
            agent.total = self.get_balance(agent, last_tx)

    def get_balance(self, initiator: 'Agent', transaction: 'NanoTX') -> float:
        if transaction is None:
            return initiator.balance
        for tx in self.dag.tangle.successors(transaction):
            if tx.owner == initiator and transaction.time > tx.time:
                if transaction.is_fork or transaction.balance < 0:
                    return self.get_balance(initiator, tx)
                return transaction.balance + self.get_balance(initiator, tx)
        if transaction.balance < 0:
            return transaction.owner.balance
        return transaction.balance + transaction.owner.balance

    def _update_repr_balance(self, repr: 'Agent'):
        repr.repr_balance = 0
        for agent in self.agents:
            if agent.repr == repr:
                repr.repr_balance += agent.total

    def _review(self, votes):
        file = open("review.csv", "a")
        for k, v in votes.items():
            file.write(f"{k};{v};\n")
        file.close()


def sort_by_time(tx: 'Transaction'):
    return tx.time


class Round:
    def __init__(self, quantity, duration, network_delay, agent_delay):
        self.quantity = quantity
        self.duration = duration
        self.network_delay = network_delay
        self.agent_delay = agent_delay
        self.repr_matrix = None

    def generate_representative_delay_matrix(self, repr_q):
        repr_matrix = np.zeros((repr_q, repr_q))
        for i in range(repr_q):
            for j in range(repr_q):
                if i == j:
                    continue
                if i > j:
                    repr_matrix[i][j] = repr_matrix[j][i]
                    continue
                repr_matrix[i][j] = self.network_delay + np.random.random_sample() * self.agent_delay
        self.repr_matrix = repr_matrix
