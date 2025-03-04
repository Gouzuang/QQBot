from src.func_template import FunctionTemplate
import QQBotAPI
from QQBotAPI.message import ReceivedMessageChain


class echo_message(FunctionTemplate):
    def __init__(self, msg:ReceivedMessageChain,QQBot:QQBotAPI.QQBot):
        self.msg = msg
        self.bot = QQBot

    def process(self):
        if self.msg.is_reply:
            rep = self.QQBot.MessageManager.get_message_via_id(self.msg.reply_info, self.msg.get_group())
            self.msg.reply(rep,self.QQBot)
        else:
            self.msg.reply("没有读取到echo的消息", self.QQBot)

    @classmethod
    def check(cls, msg):
        if msg.text_only().strip() == "echo":
                    return "echo"
        return ""

    @classmethod
    def register(cls):
        # 静态注册方法
        return {
            'type': 'message_function',
            'name': 'echo_message'
        }
        


functions = [echo_message,]