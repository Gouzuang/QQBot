功能的具体实现

每个功能需定义为一个class

class需放入list functions

class需实现以下接口：

1. check(MessageChain) -> str 检测是否符合调用条件,不符合返回“”，符合返回命中的规则
2. register() -> name(str),type()
3. 实例化时响应数据

其中如果type为extern_call_function需实现路由表
