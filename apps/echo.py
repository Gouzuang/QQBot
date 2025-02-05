
import QQBotAPI
from QQBotAPI.message import ReceivedMessageChain


class echo_message:
    def __init__(self, msg:ReceivedMessageChain,QQBot:QQBotAPI.QQBot):
        rep = QQBot.MessageManager.get_message_via_id(msg.reply_info,msg.group())
        msg.reply(rep,QQBot)

    @classmethod
    def check(cls, msg):
        if msg.is_reply and msg.text_only().strip() == "echo":
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