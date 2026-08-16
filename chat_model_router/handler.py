"""chat_model_router 事件处理器。"""

from __future__ import annotations

from typing import Any

from src.app.plugin_system.api.log_api import get_logger
from src.app.plugin_system.base import BaseEventHandler
from src.app.plugin_system.types import EventType, Message
from src.kernel.event import EventDecision

from .config import ChatModelRouterConfig

logger = get_logger("chat_model_router")

_NDFC_CREATE_REQUEST = "neo_default_chatter:create_request"
_NDFC_INJECT_UNREAD_PAYLOAD = "neo_default_chatter:inject_unread_payload"


class ChatModelRouterHandler(BaseEventHandler):
    """订阅 NDFC 事件，按聊天类型覆盖任务名与原生多模态开关。"""

    name = "chat_model_router"
    description = "按私聊/群聊覆盖 neo_default_chatter 的 actor_task_name 与 native_multimodal"
    weight = 200
    init_subscribe = [
        EventType.ON_MESSAGE_RECEIVED,
        _NDFC_CREATE_REQUEST,
        _NDFC_INJECT_UNREAD_PAYLOAD,
    ]

    async def execute(
        self, event_name: str, params: dict[str, Any]
    ) -> tuple[EventDecision, dict[str, Any]]:
        """按事件类型应用模型分流逻辑。"""
        try:
            if event_name == EventType.ON_MESSAGE_RECEIVED.value:
                await self._on_message_received(params)
                return EventDecision.SUCCESS, params

            if event_name == _NDFC_CREATE_REQUEST:
                chat_type = await self._chat_type_for_stream(
                    str(params.get("stream_id") or "")
                )
                if chat_type:
                    self._sync_skip_recognition(
                        str(params.get("stream_id") or ""), chat_type
                    )
                    task_name = self._task_name_for(chat_type)
                    if task_name:
                        params["task_name"] = task_name
                return EventDecision.SUCCESS, params

            if event_name == _NDFC_INJECT_UNREAD_PAYLOAD:
                chat_type = await self._chat_type_for_stream(
                    str(params.get("stream_id") or "")
                )
                if chat_type:
                    native_multimodal = self._native_multimodal_for(chat_type)
                    if native_multimodal is not None:
                        params["native_multimodal"] = native_multimodal
                return EventDecision.SUCCESS, params
        except Exception as exc:  # pragma: no cover - 防御性兜底
            logger.warning(f"chat_model_router 处理 {event_name} 失败: {exc}")
        return EventDecision.SUCCESS, params

    def _config(self) -> ChatModelRouterConfig | None:
        """读取本插件配置。"""
        config = getattr(self.plugin, "config", None)
        return config if isinstance(config, ChatModelRouterConfig) else None

    def _task_name_for(self, chat_type: str) -> str:
        """按聊天类型返回要覆盖的任务名，未配置则返回空串。"""
        config = self._config()
        if config is None:
            return ""
        if chat_type == "private":
            return (config.private.actor_task_name or "").strip()
        if chat_type == "group":
            return (config.group.actor_task_name or "").strip()
        return ""

    def _native_multimodal_for(self, chat_type: str) -> bool | None:
        """按聊天类型返回要覆盖的原生多模态开关，未配置则返回 None。"""
        config = self._config()
        if config is None:
            return None
        if chat_type == "private":
            return config.private.native_multimodal
        if chat_type == "group":
            return config.group.native_multimodal
        return None

    async def _on_message_received(self, params: dict[str, Any]) -> None:
        """消息到达时同步该流的媒体识别跳过标志，确保后续图片走对路径。"""
        message = params.get("message")
        if not isinstance(message, Message):
            return
        stream_id = getattr(message, "stream_id", "") or ""
        chat_type = getattr(message, "chat_type", "") or ""
        if not stream_id:
            return
        self._sync_skip_recognition(stream_id, chat_type)

    async def _chat_type_for_stream(self, stream_id: str) -> str:
        """从内存流或数据库流查询聊天类型。"""
        if not stream_id:
            return ""
        from src.app.plugin_system.api.stream_api import (
            build_stream_from_database,
            get_stream,
        )

        stream = await get_stream(stream_id)
        if stream is None:
            try:
                stream = await build_stream_from_database(stream_id)
            except Exception as exc:
                logger.debug(f"chat_model_router 查询流失败: {exc}")
        return getattr(stream, "chat_type", "") or ""

    def _sync_skip_recognition(self, stream_id: str, chat_type: str) -> None:
        """根据聊天类型的多模态配置，设置或清除该流的 VLM 识别跳过标志。"""
        native_multimodal = self._native_multimodal_for(chat_type)
        if native_multimodal is None:
            return

        try:
            from src.core.managers.media_manager import get_media_manager

            manager = get_media_manager()
            if native_multimodal:
                manager.skip_recognition_for_stream(stream_id, ["image"])
                logger.debug(
                    f"{chat_type} 流 {stream_id[:8]} 已跳过图片识别（原生多模态）"
                )
            else:
                manager.unskip_recognition_for_stream(stream_id)
                logger.debug(
                    f"{chat_type} 流 {stream_id[:8]} 已恢复图片识别（VLM 描述）"
                )
        except Exception as exc:
            logger.warning(f"同步媒体识别标志失败 {stream_id[:8]}: {exc}")
