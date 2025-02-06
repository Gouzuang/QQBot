from typing import Union


class Person():
    def __init__(self, user_id:Union[str,int], nickname:str='',card:str='',sex:str='',remark:str='',level:int = -1):
        if isinstance(user_id, str):
            user_id = int(user_id)
        self._user_id = user_id
        self._nickname = nickname
        self._card = card
        self._sex = sex
        self._remark = remark
        self._level = level
        
    def get_user_id(self) -> int:
        return self._user_id
    def get_nickname(self) -> str:
        return self._nickname
    def get_card(self) -> str:
        return self._card
    
    def __str__(self):
        str = ""
        str += f"{self.get_nickname()}"
        if self._card != "":
            str += f"({self.get_card()})"
        else:
            if self._remark != "":
                str += f"({self.get_remark()})"
        return str
    
    def __eq__(self, other):
        if isinstance(other, Person):
            return self.get_user_id() == other.user_id()
        elif isinstance(other, int):
            return self.get_user_id() == other
        elif isinstance(other, str):
            return self.get_user_id() == int(other)
        return False
    
    def get_json(self):
        return {
            "user_id":self.get_user_id(),
            "nickname":self.get_nickname(),
            "card":self.get_card()
        }
    
    
class Group():
    def __init__(self, group_id:Union[int,str], group_name='',card=''):
        if isinstance(group_id, str):
            group_id = int(group_id)
        self._group_id = group_id
        self._group_name = group_name
        self._card = card
        
    def get_group_id(self)->int:
        return self._group_id
    def get_group_name(self)->str:
        return self._group_name
    def get_card(self)->str:
        return self._card
    
    def __str__(self):
        str = ""
        str += f"{self.get_group_name()}"
        if self._card != "":
            str += f"({self.get_card()})"
        return str
    
    def __eq__(self, other):
        if isinstance(other, Group):
            return self.get_group_id() == other.get_group_id()
        elif isinstance(other, int):
            return self.get_group_id() == other
        elif isinstance(other, str):
            return self.get_group_id() == int(other)
        return False