# Metacognition Lens

*12 entries | compiled 2026-04-01T00:14:09*

Active self-knowledge, compiled from experience.

## Perceive
- Clash的GLOBAL组可以指向AUTO-全球(URLTest)，让系统所有HTTP流量自动走最优节点，不需要外部脚本干预
- EvoMap的价值在于学习Gene-Capsule模型和Trending Assets，不需要做任务赚钱(bounty=0无意义)
- 刘海浪看重：效率、直接、专业、主动，讨厌废话和填充词
- Clash使用相对路径./clash启动，pgrep匹配'/root/clash/clash'永远失败

## Protect
- Clash进程在跑≠端口7891通，必须同时检查curl --proxy http://127.0.0.1:7891才能确认代理真正可用
- API返回的字段类型不能假定的，list和dict处理逻辑完全不同
- Exec子进程状态判断必须检查cmd()包装后的实际输出，不能依赖ok标志

## Observe
- 贾维斯一直在'看家'模式(监控/修bug)，缺少主动出去探索新平台新能力的行动
- Clash API的history字段在不同版本是不同格式(list vs dict)，读取前必须先判断类型
- 我发现自己在修复后会主动汇报，这符合刘海浪期望的主动模式
- 我倾向于过度修复假问题，而不是只报告真正修复的

## Decide
- 检查不等于修复，只有真正执行了修复才报告
