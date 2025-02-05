class Person():
    def __init__(self, user_id, nickname='',card='',sex='',remark='',level = -1):
        self._user_id = user_id
        self._nickname = nickname
        self._card = card
        self._sex = sex
        self._remark = remark
        self._level = level
        
    def user_id(self):
        return self._user_id
    def nickname(self):
        return self._nickname
    def card(self):
        return self._card
    
    def __str__(self):
        str = ""
        str += f"{self.nickname()}"
        if self._card != "":
            str += f"({self.card()})"
        else:
            if self._remark != "":
                str += f"({self.remark()})"
        return str
    
    def __eq__(self, other):
        if isinstance(other, Person):
            return self.user_id() == other.user_id()
        elif isinstance(other, int):
            return self.user_id() == other
        elif isinstance(other, str):
            return self.user_id() == int(other)
        return False
    
    
class Group():
    def __init__(self, group_id, group_name='',card=''):
        self._group_id = group_id
        self._group_name = group_name
        self._card = card
        
    def group_id(self):
        return self._group_id
    def group_name(self):
        return self._group_name
    def card(self):
        return self._card
    
    def __str__(self):
        str = ""
        str += f"{self.group_name()}"
        if self._card != "":
            str += f"({self.card()})"
        return str
    
    def __eq__(self, other):
        if isinstance(other, Group):
            return self.group_id() == other.group_id()
        elif isinstance(other, int):
            return self.group_id() == other
        elif isinstance(other, str):
            return self.group_id() == int(other)
        return False