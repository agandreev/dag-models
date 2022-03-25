from typing import Dict

SEND = "send"
RECEIVE = "receive"


class Transaction:
    def __init__(self, id: int, time: float):
        self.id: int = id
        self.time: float = time
        self.owner: 'Agent' = None
        self.weight_for_each_agent: Dict['Agent', int] = dict()
        self.is_mc: bool = False

        self.is_malicious = False
        self.is_fork = False
        self.balance: float = 0

    def __repr__(self) -> str:
        return f"{self.id}"#\n{self.weight_for_each_agent}\n"

    def __str__(self) -> str:
        return f"{self.id}"


class NanoTX(Transaction):
    def __init__(self, id: int, time: float):
        super().__init__(id, time)
        self.amount: float = 0
        self.type = ""
        self.parent = None


class MaliciousTX(NanoTX):
    def __init__(self, id: int, time: float):
        super().__init__(id, time)