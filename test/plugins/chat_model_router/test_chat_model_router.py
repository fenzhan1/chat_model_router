"""chat_model_router 插件核心逻辑测试。"""

from __future__ import annotations

from typing import Any

import pytest

from plugins.chat_model_router.config import ChatModelRouterConfig
from plugins.chat_model_router.handler import ChatModelRouterHandler


class FakePlugin:
    """只提供 config 的最小插件替身。"""

    def __init__(self, config: ChatModelRouterConfig) -> None:
        self.config = config


@pytest.fixture
def config() -> ChatModelRouterConfig:
    """构造一套用于断言的默认配置。"""
    return ChatModelRouterConfig()


@pytest.fixture
def handler(config: ChatModelRouterConfig) -> ChatModelRouterHandler:
    """构造事件处理器，并屏蔽媒体管理器的副作用。"""
    instance = ChatModelRouterHandler(FakePlugin(config))
    instance._sync_skip_recognition = lambda stream_id, chat_type: None  # type: ignore[method-assign]
    return instance


def test_config_defaults(config: ChatModelRouterConfig) -> None:
    """任务名默认 actor，原生多模态默认关闭。"""
    assert config.private.actor_task_name == "actor"
    assert config.private.native_multimodal is False
    assert config.group.actor_task_name == "actor"
    assert config.group.native_multimodal is False


def test_task_name_lookup(handler: ChatModelRouterHandler) -> None:
    """按聊天类型返回配置的任务名。"""
    assert handler._task_name_for("private") == "actor"
    assert handler._task_name_for("group") == "actor"

    config = handler._config()
    assert config is not None
    config.private.actor_task_name = "actor_private"
    assert handler._task_name_for("private") == "actor_private"


def test_native_multimodal_lookup(handler: ChatModelRouterHandler) -> None:
    """按聊天类型返回原生多模态开关。"""
    assert handler._native_multimodal_for("private") is False
    assert handler._native_multimodal_for("group") is False

    config = handler._config()
    assert config is not None
    config.private.native_multimodal = True
    assert handler._native_multimodal_for("private") is True


@pytest.mark.asyncio
async def test_create_request_override(
    handler: ChatModelRouterHandler,
) -> None:
    """私聊任务名应被插件配置覆盖。"""
    handler._chat_type_for_stream = _fake_chat_type  # type: ignore[method-assign]

    result = await handler.execute(
        "neo_default_chatter:create_request",
        {
            "stream_id": "private_stream",
            "task_name": "actor",
            "request_name": "",
            "with_reminder": "actor",
            "request": None,
        },
    )
    assert result[1]["task_name"] == "actor"

    handler._config().private.actor_task_name = "actor_private"
    result = await handler.execute(
        "neo_default_chatter:create_request",
        {
            "stream_id": "private_stream",
            "task_name": "actor",
            "request_name": "",
            "with_reminder": "actor",
            "request": None,
        },
    )
    assert result[1]["task_name"] == "actor_private"


@pytest.mark.asyncio
async def test_inject_unread_payload_override(
    handler: ChatModelRouterHandler,
) -> None:
    """私聊原生多模态开关应被插件配置覆盖。"""
    handler._chat_type_for_stream = _fake_chat_type  # type: ignore[method-assign]

    result = await handler.execute(
        "neo_default_chatter:inject_unread_payload",
        {"stream_id": "private_stream", "native_multimodal": True, "skip": False},
    )
    assert result[1]["native_multimodal"] is False

    handler._config().private.native_multimodal = True
    result = await handler.execute(
        "neo_default_chatter:inject_unread_payload",
        {"stream_id": "private_stream", "native_multimodal": True, "skip": False},
    )
    assert result[1]["native_multimodal"] is True


async def _fake_chat_type(stream_id: str) -> str:
    """测试用聊天类型解析器。"""
    return "private" if stream_id == "private_stream" else "group"
