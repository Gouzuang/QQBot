import os
import sqlalchemy
from QQBotAPI.message import ReceivedMessageChain
from QQBotAPI.person import Group, Person
from shared.log import LogConfig


class MessageManager():
    def __init__(self,qq_id):
        self.logger = LogConfig().get_logger("MessageManager")
        
        # 确保database目录存在
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))        
        db_dir = os.path.join(base_dir, 'databases')
        os.makedirs(db_dir, exist_ok=True)
        
        # 使用绝对路径
        db_path = os.path.join(db_dir, f'{qq_id}.db')
        db_url = f'sqlite:///{db_path}'
        self.engine = sqlalchemy.create_engine(db_url)
        self.logger.debug(f"Database connected to {db_url}")
        
        #创建表
        self.metadata = sqlalchemy.MetaData()
        self.message_table = sqlalchemy.Table(
            'messages',
            self.metadata,
            sqlalchemy.Column('message_id', sqlalchemy.Integer),
            sqlalchemy.Column('time', sqlalchemy.Integer),
            sqlalchemy.Column('group', sqlalchemy.Integer),
            sqlalchemy.Column('sender', sqlalchemy.Integer),
            sqlalchemy.Column('json', sqlalchemy.JSON)
        )
        
        self.metadata.create_all(self.engine)

        
        
    def add_message(self,message:ReceivedMessageChain):
        #插入消息
        group_id = message.group()
        if group_id:
            group_id = group_id.group_id()
        with self.engine.connect() as conn:
            conn.execute(self.message_table.insert().values(
                message_id = message.message_id(),
                time = message.time(),
                group = group_id,
                sender = message.sender().user_id(),
                json = message.json()
            ))
            conn.commit()
        
        self.logger.debug(f"Message {message.message_id()} added to database")
        
    def get_message_via_id(self,message_id:int,group:Group = None, sender:Person = None) -> ReceivedMessageChain | None:
        #通过消息ID获取消息
        with self.engine.connect() as conn:
            query = self.message_table.select().where(self.message_table.c.message_id == message_id)
            if group:
                query = query.where(self.message_table.c.group == group.group_id())
            if sender:
                query = query.where(self.message_table.c.sender == sender.user_id())
            result = conn.execute(query).fetchone()
        self.logger.debug(f"Message {message_id} queried from database: {result}")
        if result:
            return ReceivedMessageChain(result[4])
        else:
            return None
        
    def __del__(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()