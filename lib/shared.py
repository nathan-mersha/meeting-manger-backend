from fastapi import Query
from dal.blocklist import BlockListModelDAL


class SharedFuncs():
    
    def __init__(self) -> None:
        self.block_list_model_dal = BlockListModelDAL()

    def isUserBlocked(self, subject: str, blocked: str):
        blocked_query = {"$or" : [{"subject" : subject, "blocked" : blocked}, {"subject" : blocked, "blocked" : subject}]}
        blockedLists = self.block_list_model_dal.read(query=blocked_query, limit=1)
        if len(blockedLists) == 0:
            return False
        return True    