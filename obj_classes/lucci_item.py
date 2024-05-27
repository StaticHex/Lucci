from typing import Any

class LucciItem:
    __id = 1
    def __init__(
        self,
        guild_id : int,
        name : str,
        price : float = 0,
        id : int = 0,
        _id : Any = None # Just here to avoid runtime error with pymongo
    ):
        self.guild_id : int = guild_id
        self.name : int = name
        self.price : float = price
        self.id : int = id
        if self.id == 0:
            self.id = LucciItem.__id
            LucciItem.__id += 1