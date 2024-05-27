from typing import Dict, List, Any
from obj_classes.lucci_item import LucciItem
import discord
import json
class LucciGuild:
    def __init__(
        self,
        id : int,
        name : str,
        botChannel : int = 0,
        expCap : int = 35040,
        dailyMin : int = 50,
        dailyMax : int = 150,
        workMin : int = 10,
        workMax : int = 150,
        pfp : str = "",
        roleMappings : str = "",
        shop : str = "",
        _id : Any = None # Just here to avoid runtime error with pymongo
    ) -> None:
        self.id : int = id
        self.name : str = name
        self.botChannel : int = botChannel
        self.expCap = expCap
        self.dailyMin = dailyMin
        self.dailyMax = dailyMax
        self.workMin = workMin
        self.workMax = workMax
        self.pfp : str = ""
        self.roleMappings : Dict[int, Dict[str, List[int]]] = {}
        if roleMappings != "":
            self.roleMappings = json.loads(roleMappings)
        self.shop : Dict[str, LucciItem] = {}
        if shop != "":
            self.shop = json.loads(shop)
    
    def toDict(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "botChannel":self.botChannel,
            "expCap":self.expCap,
            "dailyMin":self.dailyMin,
            "dailyMax":self.dailyMax,
            "workMin":self.workMin,
            "workMax":self.workMax,
            "pfp":self.pfp,
            "roleMappings":json.dumps(self.roleMappings),
            "shop":json.dumps(self.shop)
        }