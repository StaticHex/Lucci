import json
from obj_classes.lucci_item import LucciItem
from typing import Dict, Any, List

class LucciUser:
    def __init__(
            self, 
            id : int,
            name : str,
            lastWork : int = 0,
            lastDaily : int = 0,
            money : int = 0,
            bank : int = 0,
            dailyCount : int = 0,
            messageCount : int = 0,
            timeoutValue : int = 0,
            timeoutExpire : int = 0,
            exp : int = 0,
            rank : int = 0,
            _id : Any = None # Just here to avoid runtime error with pymongo
        ) -> None:
        self.id : int = id
        self.name : str = name
        self.lastWork : int = lastWork
        self.lastDaily : int = lastDaily
        self.money : int = money
        self.bank : int = bank
        self.dailyCount : int = dailyCount
        self.messageCount : int = messageCount
        self.timeoutValue : int = timeoutValue
        self.timeoutExpire : int = timeoutExpire
        self.exp : int = exp
        self.rank : int = rank
    
    def toDict(self) -> Dict[str, any]:
        return {
            "id":self.id,
            "name":self.name,
            "lastWork":self.lastWork,
            "lastDaily":self.lastDaily,
            "money":self.money,
            "bank":self.bank,
            "dailyCount":self.dailyCount,
            "messageCount":self.messageCount,
            "messageCount":self.timeoutValue,
            "timeoutExpire":self.timeoutExpire,
            "exp":self.exp,
            "rank":self.rank
        }

    
    def __str__(self):
        return json.dumps(self.toDict())