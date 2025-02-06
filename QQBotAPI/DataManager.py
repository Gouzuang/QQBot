import json
import logging
import os
import sqlalchemy
from QQBotAPI.message import ReceivedMessageChain
from QQBotAPI.person import Group, Person
from QQBotAPI.config import DataBasePath
from QQBotAPI.errors import DataNotFoundInDataBaseError

class MessageManager():
    def __init__(self,qq_id):
        self.logger = logging.getLogger('MessageManager')

        
        # Get database directory from config
        db_dir = DataBasePath().db_path
        os.makedirs(db_dir, exist_ok=True)
        # Use absolute path with configured directory
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
        group_id = message.get_group()
        if group_id:
            group_id = group_id.get_group_id()
        with self.engine.connect() as conn:
            conn.execute(self.message_table.insert().values(
                message_id = message.get_message_id(),
                time = message.get_time(),
                group = group_id,
                sender = message.get_sender().get_user_id(),
                json = message.get_json_for_db()
            ))
            conn.commit()
        
        self.logger.debug(f"Message {message.get_message_id()} added to database: {json.dumps(message.get_json_for_db(), indent=4, ensure_ascii=False)}")
        
    def get_message_via_id(self,message_id:int,group:Group = None, sender:Person = None) -> ReceivedMessageChain | None:
        #通过消息ID获取消息
        with self.engine.connect() as conn:
            query = self.message_table.select().where(self.message_table.c.message_id == message_id)
            if group:
                query = query.where(self.message_table.c.group == group.group_id())
            if sender:
                query = query.where(self.message_table.c.sender == sender.user_id())
            result = conn.execute(query).fetchone()
        self.logger.debug(f"Message {message_id} queried from database: {json.dumps(result[4], indent=4, ensure_ascii=False)}")
        if result:
            return ReceivedMessageChain.json_from_db(result[4])
        else:
            raise DataNotFoundInDataBaseError(f"Message {message_id} not found in database")
        
    def __del__(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()
            self.logger.info("Database connection closed")
            
    def update_message(self,message:ReceivedMessageChain):
        #更新消息
        group_id = message.get_group()
        if group_id:
            group_id = group_id.get_group_id()
        with self.engine.connect() as conn:
            conn.execute(self.message_table.update().where(self.message_table.c.message_id == message.get_message_id()).values(
                time = message.get_time(),
                group = group_id,
                sender = message.get_sender().get_user_id(),
                json = message.get_json_for_db()
            ))
            conn.commit()
        self.logger.debug(f"Message {message.get_message_id()} updated in database: {json.dumps(message.get_json_for_db(), indent=4, ensure_ascii=False)}")