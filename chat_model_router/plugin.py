"""chat_model_router 插件入口。"""

from __future__ import annotations

from src.app.plugin_system.base import BasePlugin, register_plugin
from src.app.plugin_system.api.log_api import get_logger

from .config import ChatModelRouterConfig
from .handler import ChatModelRouterHandler

logger = get_logger("chat_model_router")


@register_plugin
class ChatModelRouterPlugin(BasePlugin):
    """按聊天类型分流 neo_default_chatter 使用的模型。"""

    plugin_name = "chat_model_router"
    plugin_description = "私聊/群聊使用不同 actor 任务与原生多模态开关"
    plugin_version = "1.0.0"

    configs: list[type] = [ChatModelRouterConfig]

    async def on_plugin_loaded(self) -> None:
        """启动后为已有聊天流同步媒体识别标志，避免首条图片消息走错路径。"""
        try:
            from src.app.plugin_system.api.stream_api import get_stream_ids_from_db

            handler = ChatModelRouterHandler(self)
            for chat_type, native in (
                ("private", self._private_native_multimodal()),
                ("group", self._group_native_multimodal()),
            ):
                if native is None:
                    continue
                for stream_id in await get_stream_ids_from_db(chat_type):
                    handler._sync_skip_recognition(stream_id, chat_type)
            logger.info("chat_model_router 已同步已有聊天流的媒体识别标志")
        except Exception as exc:
            logger.warning(f"chat_model_router 同步媒体识别标志失败: {exc}")

    def _private_native_multimodal(self) -> bool | None:
        config = getattr(self, "config", None)
        if isinstance(config, ChatModelRouterConfig):
            return config.private.native_multimodal
        return None

    def _group_native_multimodal(self) -> bool | None:
        config = getattr(self, "config", None)
        if isinstance(config, ChatModelRouterConfig):
            return config.group.native_multimodal
        return None

    def get_components(self) -> list[type]:
        """返回本插件提供的组件类。"""
        config = getattr(self, "config", None)
        if isinstance(config, ChatModelRouterConfig) and not config.plugin.enabled:
            logger.info("chat_model_router 未启用")
            return []
        return [ChatModelRouterHandler]
