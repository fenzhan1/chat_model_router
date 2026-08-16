# chat_model_router

按聊天类型给 `neo_default_chatter` 分流模型：私聊和群聊可以使用不同的
`actor_task_name`，并各自指定 `native_multimodal`（原生多模态开关）。

本插件不改动 `neo_default_chatter` 源码，只订阅它发布的事件：

- `neo_default_chatter:create_request`：覆盖 `task_name`
- `neo_default_chatter:inject_unread_payload`：覆盖 `native_multimodal`
- `ON_MESSAGE_RECEIVED` / 插件启动时：同步媒体管理器的 VLM 识别跳过标志

## 配置步骤

1. 在 `config/model.toml` 中添加私聊/群聊对应的任务（如果私聊要用独立模型）：

```toml
[model_tasks.actor_private]
model_list = ["你的私聊模型名"]
max_tokens = 800
temperature = 0.7
concurrency_count = 1
embedding_dimension = 0
```

2. 编辑 `config/plugins/chat_model_router/config.toml`（首次启动会自动生成）：

```toml
[private]
actor_task_name = "actor"
native_multimodal = false

[group]
actor_task_name = "actor"
native_multimodal = false
```

`actor_task_name` 默认 `actor`，留空表示沿用 `neo_default_chatter` 的 `actor_task_name`；
`native_multimodal` 是开关，默认关闭，开启后该聊天类型使用原生多模态。

启用原生多模态前，请确认对应任务使用的模型支持图片输入。
