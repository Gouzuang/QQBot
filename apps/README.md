功能的具体实现

每个功能需定义为一个class

class需放入list functions

class需实现以下接口：

1. check(MessageChain) -> str 检测是否符合调用条件,不符合返回“”，符合返回命中的规则
2. register() -> name(str),type()
3. process() 响应数据

其中如果type为extern_call_function需实现路由表
type可以是：message_function ，quiet_function ， regular_task_function ， extern_call_function
