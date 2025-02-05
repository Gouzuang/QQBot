
class echo_message:
    def __init__(self, data,QQBot):
        pass

    @classmethod
    def check(cls, data):
        pass

    @classmethod
    def register(cls):
        # 静态注册方法
        return {
            'type': 'message_function',
            'name': 'echo_message'
        }
        
    def run(self):
        pass


functions = [echo_message,]