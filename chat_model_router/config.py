"""chat_model_router 插件配置。"""

from __future__ import annotations

from typing import ClassVar

from src.app.plugin_system.base import BaseConfig, Field, SectionBase, config_section


class ChatModelRouterConfig(BaseConfig):
    """私聊/群聊模型分流配置。"""

    name: ClassVar[str] = "config"
    description: ClassVar[str] = "按聊天类型覆盖 neo_default_chatter 的任务名与原生多模态开关"

    @config_section("plugin", title="插件设置", tag="plugin")
    class PluginSection(SectionBase):
        """插件基础配置。"""

        enabled: bool = Field(
            default=True,
            description="是否启用 chat_model_router",
            label="启用插件",
            tag="plugin",
        )

    @config_section("private", title="私聊", tag="ai")
    class PrivateSection(SectionBase):
        """私聊使用的模型与多模态设置。"""

        actor_task_name: str = Field(
            default="actor",
            description=(
                "私聊使用的 actor 任务名，对应 config/model.toml 中的 [model_tasks.xxx]。"
                "留空则沿用 neo_default_chatter 配置的 actor_task_name。"
            ),
            label="私聊任务名",
            tag="ai",
            hint="默认 actor；需在 model.toml 中先定义该任务。",
        )
        native_multimodal: bool = Field(
            default=False,
            description=(
                "私聊是否启用原生多模态。启用后图片以 base64 直接进入 LLM 并跳过 VLM 识别；"
                "关闭时走 VLM 文字识别。"
            ),
            label="私聊原生多模态",
            tag="ai",
            hint="启用前请确认私聊任务对应的模型支持图片输入。",
            input_type="switch",
        )

    @config_section("group", title="群聊", tag="ai")
    class GroupSection(SectionBase):
        """群聊使用的模型与多模态设置。"""

        actor_task_name: str = Field(
            default="actor",
            description=(
                "群聊使用的 actor 任务名，对应 config/model.toml 中的 [model_tasks.xxx]。"
                "留空则沿用 neo_default_chatter 配置的 actor_task_name。"
            ),
            label="群聊任务名",
            tag="ai",
            hint="默认 actor；需在 model.toml 中先定义该任务。",
        )
        native_multimodal: bool = Field(
            default=False,
            description=(
                "群聊是否启用原生多模态。启用后图片以 base64 直接进入 LLM 并跳过 VLM 识别；"
                "关闭时走 VLM 文字识别。"
            ),
            label="群聊原生多模态",
            tag="ai",
            hint="启用前请确认群聊任务对应的模型支持图片输入。",
            input_type="switch",
        )

    plugin: PluginSection = Field(default_factory=PluginSection)
    private: PrivateSection = Field(default_factory=PrivateSection)
    group: GroupSection = Field(default_factory=GroupSection)
