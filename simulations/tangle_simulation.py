from simulation_components.agents.agent import Agent
import numpy as np
import networkx as nx
import time
from threading import Thread

from simulation_components.agents.malicious_agent import MaliciousAgent
from simulation_components.agents.outpace_attacker import OutpaceAttacker
from simulation_components.agents.parasite_chain_attacker import ParasiteChainAttacker
from simulation_components.agents.split_attacker import SplitAttacker
from simulation_components.tangle import Tangle
from simulation_components.functions.built_in_function import calc_exponential_transition
from simulation_components.functions.own_function import calc_own_transition
from collections import Counter
from typing import List

from simulation_components.transaction import Transaction


class TangleSimulation:
    def __init__(self, transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_agents_delay: float,
                 network_delay: float,
                 alpha: float,
                 tip_selection: str,
                 walkers_quantity: int = 2,
                 walkers_choice: str = 'None',
                 start_choice: str = 'None',
                 attacker_type: str = '',
                 attackers_transactions_quantity: int = 0,
                 attackers_start_time: int = 0,
                 attackers_rate: int = 0,
                 attackers_confirmation_delay: int = 0,
                 attackers_references: int = 0,
                 attackers_splits: int = 0):

        # Checking correctness of data
        if transactions_quantity <= 0:
            raise Exception("Quantity of transactions should be more than zero!")
        if agents_quantity <= 0:
            raise Exception("Quantity of agents should be more than zero!")
        if transaction_rate <= 0:
            raise Exception("Transaction rate should be more than zero!")
        if network_agents_delay < 0:
            raise Exception("Agent's network delay should be more or equal zero!")
        if network_delay < 0:
            raise Exception("Network delay should be more or equal zero!")
        if alpha <= 0:
            raise Exception("Alpha should be more than zero!")
        if walkers_quantity <= 0:
            raise Exception("Network delay should be more than zero!")

        # Checking correctness of malicious data
        if attacker_type != '' and attacker_type != 'None':
            if attackers_transactions_quantity <= 0:
                raise Exception("Quantity of attacker's transactions "
                                "should be more than zero!")
            if attackers_rate <= 0:
                raise Exception("Attacker's rate should be more than zero!")
            if attackers_confirmation_delay < 0:
                raise Exception("Confirmation delay should be more or equal zero!")
            if attackers_references < 0:
                raise Exception("Attacker's references should be more or equal zero!")
            if attackers_splits < 0:
                raise Exception("Attacker's references should be more or equal zero!")

        self.alpha: float = alpha
        self.agents: List['Agent'] = list()
        self.arrival_times: List['float'] = list()
        self.colors: List[str] = list()
        self.dag: 'Tangle' = None

        if attacker_type == "":
            self.is_malicious: bool = False
        else:
            self.is_malicious: bool = True
        self.malicious_agent: 'MaliciousAgent' = None
        self.attacker_type: str = attacker_type

        self.tip_selection: str = tip_selection

        self.transactions_quantity: int = transactions_quantity
        self.agents_quantity: int = agents_quantity
        self.transaction_rate: int = transaction_rate
        self.network_delay: float = network_delay
        self.network_agents_delay: float = network_agents_delay
        self.walkers_quantity: int = walkers_quantity
        self.walkers_choice: str = walkers_choice
        self.start_choice: str = start_choice

        self.attackers_transactions_quantity: int = attackers_transactions_quantity
        self.attackers_start_time: int = attackers_start_time
        self.attackers_rate: int = attackers_rate
        self.attackers_confirmation_delay: int = attackers_confirmation_delay
        self.attackers_references: int = attackers_references
        self.attackers_splits: int = attackers_splits

        self.final_time: float = 0

    def setup(self) -> None:
        self._generate_agents()
        self._generate_arrival_times()
        self.dag = Tangle(self.arrival_times)

        # Creating instance of malicious agent
        if self.is_malicious:
            if self.attacker_type == "Parasite":
                self.malicious_agent = \
                    ParasiteChainAttacker(len(self.agents),
                                          self.attackers_transactions_quantity,
                                          self.attackers_start_time,
                                          self.attackers_references,
                                          self.attackers_rate,
                                          self.attackers_confirmation_delay)
            elif self.attacker_type == "Split":
                self.malicious_agent = \
                    SplitAttacker(len(self.agents),
                                  self.attackers_transactions_quantity,
                                  self.attackers_start_time,
                                  self.attackers_rate,
                                  self.attackers_splits)
            elif self.attacker_type == "Outpace":
                self.malicious_agent = \
                    OutpaceAttacker(len(self.agents),
                                    self.attackers_transactions_quantity,
                                    self.attackers_start_time,
                                    self.attackers_rate,
                                    self.attackers_confirmation_delay)
            else:
                raise Exception("Attacker type is incorrect!")

            # Initializing weights for each transaction and for each malicious agent
            for transaction in self.malicious_agent.transactions:
                transaction.weight_for_each_agent[self.malicious_agent] = 1
            for transaction in self.malicious_agent.transactions:
                for agent in self.agents:
                    transaction.weight_for_each_agent[agent] = 1
            for transaction in self.dag.transactions:
                transaction.weight_for_each_agent[self.malicious_agent] = 1

        # Initializing weights for each agent except malicioys
        for agent in self.agents:
            for transaction in self.dag.transactions:
                transaction.weight_for_each_agent[agent] = 1

        # Initializing owner for each transaction except genesis
        for transaction in self.dag.transactions[1:]:
            transaction.owner = np.random.choice(self.agents)

        # Connecting simple and malicious transactions and agents
        if self.malicious_agent is not None:
            self.dag.transactions += self.malicious_agent.transactions
            self.dag.transactions.sort(key=lambda t: t.time)

            self.agents.append(self.malicious_agent)

        # Specifying malicious transactions setup
        if isinstance(self.malicious_agent, ParasiteChainAttacker):
            for transaction in self.dag.transactions:
                if isinstance(transaction.owner, MaliciousAgent):
                    break
                self.malicious_agent.r_transaction = transaction
        elif isinstance(self.malicious_agent, SplitAttacker):
            pass
        elif isinstance(self.malicious_agent, OutpaceAttacker):
            connected_transaction = None
            for transaction in self.dag.transactions:
                if isinstance(transaction.owner, OutpaceAttacker):
                    break
                connected_transaction = transaction
            self.malicious_agent.connected_transaction = connected_transaction

    def run(self) -> None:
        current_time = time.process_time()

        malicious_transactions_counter = 0

        # Starting simulation for each transaction except genesis
        for transaction in self.dag.transactions[1:]:

            if isinstance(self.malicious_agent, ParasiteChainAttacker) \
                    and transaction == self.malicious_agent.r_transaction:
                color = "#8b00ff"
            else:
                color = transaction.owner.color

            # Connecting graphs and outpace
            if isinstance(self.malicious_agent, OutpaceAttacker) \
                    and self.malicious_agent.is_legitimate_sended \
                    and not self.malicious_agent.is_composed:
                # If legitimate transaction is confirmed or all transactions are sent
                if self.malicious_agent.confirmation_value <= transaction.time \
                        or transaction == \
                        self.dag.transactions[len(self.dag.transactions) - 1]:
                    self.malicious_agent.is_composed = True
                    # self.dag.tangle = nx.compose(self.dag.tangle, self.malicious_agent.outpace_graph)
                    self.dag.tangle.add_edge(self.malicious_agent.transactions[1],
                                             self.malicious_agent.connected_transaction)

            # todo: remake
            # Counting x and y position
            y_axis = np.random.uniform(0, 1) - transaction.owner.id * 1.3
            if isinstance(transaction.owner, ParasiteChainAttacker) \
                    and malicious_transactions_counter == 0:
                y_axis = np.random.uniform(0, len(self.agents)) - (len(self.agents) - 1) / 2 * 1.3
            # Create node for all agents except outpace attacker
            if not isinstance(transaction.owner, OutpaceAttacker):
                self.dag.tangle.add_node(transaction,
                                         pos=(transaction.time, y_axis),
                                         node_color=color)

            # If it is simple transaction
            if not isinstance(transaction.owner, MaliciousAgent):
                self._tip_selection_classificator(transaction)
            # Malicious transactions
            else:
                # Add parasite double-spending
                if isinstance(transaction.owner, ParasiteChainAttacker):
                    if malicious_transactions_counter == 0:
                        self._tip_selection_classificator(transaction)
                    else:
                        if malicious_transactions_counter - 1 != 0:
                            self.dag.tangle.add_edge(
                                transaction,
                                self.malicious_agent.transactions[malicious_transactions_counter - 1])
                        if malicious_transactions_counter - 1 <= self.malicious_agent.reference_quantity:
                            self.dag.tangle.add_edge(
                                transaction,
                                self.malicious_agent.r_transaction)
                elif isinstance(transaction.owner, SplitAttacker):
                    # Initialize double-spending transaction
                    if transaction.owner.splitting_transactions_quantity > malicious_transactions_counter:
                        self._tip_selection_classificator(transaction)
                        transaction.owner.double_spending_transactions.append(transaction)
                    # Work with weight
                    else:
                        aiming_transaction = min(transaction.owner.double_spending_transactions,
                                                 key=lambda tr: self.dag.count_final_weight(tr))
                        # tr.weight_for_each_agent[transaction.owner]
                        not_validated = list()
                        self._find_not_approved_transactions_by_double_spend_branch(
                            aiming_transaction, not_validated)
                        validable_transactions = np.random.choice(not_validated, 2)
                        self.dag.add_edges(list(set(validable_transactions)), transaction)
                elif isinstance(transaction.owner, OutpaceAttacker):
                    # Add legitimate transaction
                    if malicious_transactions_counter == 0:
                        self.dag.tangle.add_node(transaction,
                                                 pos=(transaction.time, y_axis),
                                                 node_color=transaction.owner.color)
                        self._tip_selection_classificator(transaction)
                        self.malicious_agent.is_legitimate_sended = True
                    # Add outpace transactions
                    elif malicious_transactions_counter == 1:
                        self.dag.tangle. \
                            add_node(transaction,
                                     pos=(transaction.time + self.malicious_agent.confirmation_delay,
                                          y_axis),
                                     node_color=transaction.owner.color)
                        self.malicious_agent.sended_malicious_transactions.append(transaction)
                    # Add outpace transaction's validators
                    else:
                        self.dag.tangle. \
                            add_node(transaction,
                                     pos=(transaction.time + self.malicious_agent.confirmation_delay,
                                          y_axis),
                                     node_color=transaction.owner.color)
                        if self.malicious_agent.is_composed:
                            pass
                            # self._tip_selection_classificator(transaction)
                        else:
                            outpace_nodes = np.array(self.malicious_agent.sended_malicious_transactions)
                            validable_transactions = set(np.random.choice(outpace_nodes, 2))
                            for validable_transaction in validable_transactions:
                                self.dag.tangle. \
                                    add_edge(transaction, validable_transaction)
                        self.malicious_agent.sended_malicious_transactions.append(transaction)

                malicious_transactions_counter += 1

            self._get_existing_transactions_for_agent(transaction)
            self.update_weights_multiple_agents(transaction)

        self.final_time = time.process_time() - current_time

        # Saving final results
        self.dag.save_time(self.final_time)
        if isinstance(self.malicious_agent, ParasiteChainAttacker) \
                or isinstance(self.malicious_agent, SplitAttacker) \
                or isinstance(self.malicious_agent, OutpaceAttacker):
            self.dag.save_attack_result(self.malicious_agent.transactions[0],
                                        self.malicious_agent.transactions[1])
        self.dag.save_cumulative_weights()

    def _find_not_approved_transactions_by_double_spend_branch(self, aiming_transaction: 'Transaction',
                                                               not_validated: List['Transaction']):
        validators = self.dag.tangle.predecessors(aiming_transaction)

        while len(list(validators)) != 0:
            for validator in validators:
                self._find_not_approved_transactions_by_double_spend_branch(validator, not_validated)
        not_validated.append(aiming_transaction)

    def _tip_selection_classificator(self, transaction):
        # run selection for clever algorithms
        if self.tip_selection == "MCMC" or self.tip_selection == "OWN":
            # get existing transactions for owner
            self._get_existing_transactions_for_agent(transaction)
            # run default selection
            if self.start_choice == 'None':
                self._weighted_mcmc_selection(transaction)
            # run selection with certain walker by number or time
            elif self.start_choice == 'Number' or self.start_choice == 'Time':
                possible_walkers = list()
                # run selection with certain walker by number
                if self.start_choice == 'Number':
                    upper = np.maximum(1, len(transaction.owner.existing_transactions) - self.transaction_rate)
                    possible_walkers = transaction.owner.existing_transactions[0:upper]
                # run selection of certain walker by time
                elif self.start_choice == 'Time':
                    closest_time = transaction.time / 2
                    upper = min(transaction.owner.existing_transactions,
                                key=lambda t: abs(t.time - closest_time))
                    possible_walkers = list(self._gen(transaction.owner.existing_transactions,
                                                      upper))
                # start selection with start walker
                self._weighted_mcmc_selection(transaction,
                                              np.random.choice(possible_walkers))
            else:
                raise Exception(f"Incorrect type of start walker selection! "
                                f"{self.start_choice}")
            return
        # run simple selection
        if self.tip_selection == "URTC":
            self._urtc_selection(transaction)
            return
        raise Exception("Incorrect tip selection type!")

    def _gen(self, transactions, break_point):
        for transaction in transactions:
            yield transaction
            if transaction == break_point:
                return

    def _urtc_selection(self, transaction: 'Transaction') -> None:
        self._get_existing_transactions_for_agent(transaction)
        tips = self._get_not_approved_transactions(transaction)

        validated_tips = set()
        validated_tips.add(np.random.choice(tips, 1)[0])
        validated_tips.add(np.random.choice(tips, 1)[0])

        self.dag.add_edges(validated_tips, transaction)

    def _weighted_mcmc_selection(self, transaction: 'Transaction',
                                 start_walker=None) -> None:
        tips = self._get_not_approved_transactions(transaction)

        if start_walker is None:
            start_walker = self.dag.transactions[0]

        validated_tips = list()
        threads = list()
        for _ in range(self.walkers_quantity):
            t = Thread(target=self._thread_worker,
                       args=(validated_tips, transaction, tips, start_walker))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()

        self.dag.add_edges(list(self._walkers_selection(validated_tips)), transaction)

    def _walkers_selection(self, validated_tips):
        chosen_validated_tips = set()
        if self.walkers_choice == 'None' or self.walkers_choice == 'First':
            chosen_validated_tips.add(validated_tips[-1])
            chosen_validated_tips.add(validated_tips[-2])
        elif self.walkers_choice == 'Last':
            chosen_validated_tips.add(validated_tips[0])
            chosen_validated_tips.add(validated_tips[1])
        elif self.walkers_choice == 'Random':
            chosen_validated_tips.add(np.random.choice(validated_tips, 1)[0])
            chosen_validated_tips.add(np.random.choice(validated_tips, 1)[0])
        else:
            raise Exception('Incorrect type of walker\'s selection')

        return chosen_validated_tips

    def _thread_worker(self, validated_tips, transaction, tips, start_walker):
        validated_tips.append(
            self.weighted_random_walk(transaction, tips, start_walker))

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
                            self.network_agents_delay + \
                            self.network_delay <= current_transaction.time:
                        agent.existing_transactions.append(transaction)

                    elif current_transaction.owner == agent:
                        current_transaction.owner.not_existing_transaction.append(transaction)

    def weighted_random_walk(self, current_transaction: 'Transaction',
                             not_validated_transactions: List['Transaction'],
                             walker=None) -> 'Transaction':

        if walker is None:
            walker = self.dag.transactions[0]
        chain_of_walkers_weights = list()

        # If only genesis a valid tip, approve genesis
        if len(not_validated_transactions) == 1 \
                and not_validated_transactions[0].id == 0:
            return walker

        while walker not in not_validated_transactions:
            # nodes that validated walker node
            walker_validators = list(self.dag.tangle.predecessors(walker))

            visible_validators = [item for item, count
                                  in Counter(walker_validators +
                                             current_transaction.owner.existing_transactions).items()
                                  if count > 1]
            if self.tip_selection == "MCMC":
                transition_probabilities = \
                    calc_exponential_transition(self.alpha,
                                                walker,
                                                visible_validators,
                                                current_transaction.owner,
                                                chain_of_walkers_weights)
            elif self.tip_selection == "OWN":
                transition_probabilities = \
                    calc_own_transition(self.alpha,
                                        walker,
                                        visible_validators,
                                        current_transaction.owner,
                                        chain_of_walkers_weights)

            # Choose with transition probabilities
            walker = np.random.choice(visible_validators, p=transition_probabilities)

        return walker

    def update_weights_multiple_agents(self, aiming_transaction: 'Transaction') -> None:
        # checking for subtangles (new)
        if self.dag.tangle.has_node(aiming_transaction):
            validated_transactions_by_aim = \
                list(nx.neighbors(self.dag.tangle, aiming_transaction))
        else:
            validated_transactions_by_aim = list()

        if len(validated_transactions_by_aim) == 0:
            return

        for transaction in validated_transactions_by_aim:
            self.update_weights_multiple_agents(transaction)
            for agent in self.agents:
                if transaction in agent.existing_transactions:
                    transaction.weight_for_each_agent[agent] += 1

    def calc_log_transition(self, walker: 'Transaction',
                            walker_validators: List['Transaction'],
                            agent: 'Agent', walkers_weights) -> np.ndarray:

        walker_validators_weights = np.array([walker_validator.weight_for_each_agent[agent]
                                              for walker_validator in walker_validators])

        probabilities = list()
        for walker_validator in walker_validators:
            probability = (walker.weight_for_each_agent[agent]
                           - walker_validator.weight_for_each_agent[agent]) ** (self.alpha)
            probabilities.append(probability)

        # walker_validators_weights = walker_validators_weights - np.max(walker_validators_weights)
        print(np.divide(np.array(probabilities),
                        np.sum(walker.weight_for_each_agent[agent] - walker_validators_weights) ** (self.alpha)))
        return np.divide(np.array(probabilities),
                         np.sum(walker.weight_for_each_agent[agent] - walker_validators_weights) ** (self.alpha))

    def _generate_agents(self) -> None:
        for i in range(self.agents_quantity):
            self.agents.append(Agent(i))

    def _generate_arrival_times(self) -> None:
        self.arrival_times = np.random.exponential(1 / self.transaction_rate,
                                                   self.transactions_quantity)

    def get_agents_legend(self) -> (List[str], List[str]):
        names = list()
        colors = list()
        for agent in self.agents:
            names.append(str(agent))
            colors.append(agent.color)
        return names, colors
