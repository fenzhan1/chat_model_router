# chat_model_router（私聊/群聊模型分流）

按聊天类型给 `neo_default_chatter` 分流模型：私聊和群聊可以使用不同的
`actor_task_name`，并各自控制原生多模态开关。

## 安装

将 `chat_model_router-1.0.0.mfp` 放入机器人的 `plugins/` 目录后执行
`/reload chat_model_router`，或把 `chat_model_router/` 源码目录放入 `plugins/`
后重启。

## 目录说明

- `chat_model_router/`：插件源码（与 plugins/ 目录布局一致）
- `test/`：插件核心逻辑测试
- `chat_model_router-1.0.0.mfp` / `.zip`：发布包（内容相同，任选其一）

## 配置

首次加载自动生成 `config/plugins/chat_model_router/config.toml`。默认任务名为
`actor`，原生多模态开关默认关闭。启用原生多模态前请确认对应模型支持图片输入。

## 测试

```bash
python -m pytest test/plugins/chat_model_router -p no:randomly -q -o addopts=""
```

## 许可证

GPL-3.0。
