import numpy as np
from typing import List

from simulation_components.transaction import Transaction


class Agent:
    def __init__(self, id: int):
        self.id: int = id
        self.existing_transactions: List = list()
        self.not_existing_transaction: List = list()
        self.color: str = "#%06x" % np.random.randint(0, 0xFFFFFF)
        self.is_witness: bool = False
        self.recent_txs: List['NanoTX'] = list()

        self.is_repr: bool = False
        self.repr_balance: float = 0
        self.repr: 'Agent' = None
        self.balance: float = 0
        self.total: float = 0

    def clear_transactions_lists(self) -> None:
        self.existing_transactions: List = list()
        self.not_existing_transaction: List = list()

    def get_legend(self) -> (str, str):
        return str(self), self.color

    def __str__(self) -> str:
        return f"Agent №{self.id}"

    def __repr__(self) -> str:
        return f"Agent №{self.id}"
