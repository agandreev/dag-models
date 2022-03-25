from abc import abstractmethod
from typing import List, Dict
import numpy as np

from simulation_components.agents.agent import Agent

class Simulation:
    def __init__(self,
                 transactions_quantity: int,
                 agents_quantity: int,
                 transaction_rate: int,
                 network_delay: float,
                 validation_quantity: int):

        if transactions_quantity <= 0:
            raise Exception("Quantity of transactions should be more than zero!")
        if agents_quantity <= 0:
            raise Exception("Quantity of agents should be more than zero!")
        if transaction_rate <= 0:
            raise Exception("Transaction rate should be more than zero!")
        if network_delay < 0:
            raise Exception("Network delay should be more or equal zero!")
        if validation_quantity <= 0:
            raise Exception("Validation quantity should be more then zero!")

        self.transactions_quantity: int = transactions_quantity
        self.agents_quantity: int = agents_quantity
        self.transaction_rate: int = transaction_rate
        self.network_delay: float = network_delay
        self.validation_quantity: int = validation_quantity

        self.agents: List['Agent'] = list()
        self.arrival_times: List['float'] = list()
        self.node_colors: List[str] = list()
        self.edge_colors: List[str] = list()
        self.dag = None

        self.final_time: float = 0

    def generate_agents(self) -> None:
        for i in range(self.agents_quantity):
            self.agents.append(Agent(i))
            self.agents[i].balance = 1 / self.agents_quantity

    def generate_arrival_times(self) -> None:
        self.arrival_times = np.random.exponential(1 / self.transaction_rate,
                                                   self.transactions_quantity)

    def get_agents_legend(self) -> (List[str], List[str]):
        names = list()
        colors = list()
        for agent in self.agents:
            names.append(str(agent))
            colors.append(agent.color)
        return names, colors
