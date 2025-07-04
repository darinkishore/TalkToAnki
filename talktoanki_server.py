#!/usr/bin/env python3
"""
TalkToAnki - 完整的单文件版本
一个专业的 MCP (Model Context Protocol) 服务器，提供20个Anki集成工具
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx
from mcp.server import FastMCP

# ============================================================================
# 配置管理
# ============================================================================

class Config:
    """配置管理类"""
    
    # AnkiConnect 配置
    ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    ANKI_CONNECT_VERSION = int(os.getenv("ANKI_CONNECT_VERSION", "6"))
    
    # 服务器配置
    SERVER_NAME = "TalkToAnki"
    SERVER_VERSION = "1.0.0"
    SERVER_INSTRUCTIONS = "A server for interacting with Anki through AnkiConnect"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 超时配置
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
    CONNECTION_TIMEOUT = float(os.getenv("CONNECTION_TIMEOUT", "10.0"))
    
    # 重试配置
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # 默认笔记类型
    DEFAULT_NOTE_TYPE = os.getenv("DEFAULT_NOTE_TYPE", "Basic")
    
    # 并发配置
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        try:
            assert cls.ANKI_CONNECT_VERSION > 0, "AnkiConnect版本必须大于0"
            assert cls.REQUEST_TIMEOUT > 0, "请求超时必须大于0"
            assert cls.MAX_RETRIES >= 0, "最大重试次数不能为负数"
            assert cls.MAX_CONCURRENT_REQUESTS > 0, "最大并发请求数必须大于0"
            return True
        except AssertionError as e:
            print(f"配置验证失败: {e}")
            return False
    
    @classmethod
    def get_anki_connect_config(cls) -> Dict[str, Any]:
        """获取AnkiConnect相关配置"""
        return {
            "url": cls.ANKI_CONNECT_URL,
            "version": cls.ANKI_CONNECT_VERSION,
            "timeout": cls.REQUEST_TIMEOUT,
            "connection_timeout": cls.CONNECTION_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY
        }

# ============================================================================
# AnkiConnect 客户端
# ============================================================================

class AnkiConnectError(Exception):
    """AnkiConnect相关异常"""
    pass

class AnkiConnectClient:
    """AnkiConnect 客户端"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化客户端"""
        if config is None:
            config = Config.get_anki_connect_config()
        
        self.url = config["url"]
        self.version = config["version"]
        self.timeout = config["timeout"]
        self.connection_timeout = config["connection_timeout"]
        self.max_retries = config["max_retries"]
        self.retry_delay = config["retry_delay"]
        
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_REQUESTS)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端实例"""
        if self._client is None:
            timeout_config = httpx.Timeout(
                connect=self.connection_timeout,
                read=self.timeout,
                write=self.timeout,
                pool=self.timeout
            )
            self._client = httpx.AsyncClient(
                timeout=timeout_config,
                limits=httpx.Limits(max_connections=Config.MAX_CONCURRENT_REQUESTS)
            )
        return self._client
    
    async def _make_request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """发送HTTP请求到AnkiConnect"""
        request_data = {
            "action": action,
            "version": self.version,
            "params": params or {}
        }
        
        client = await self._get_client()
        response = await client.post(self.url, json=request_data)
        response.raise_for_status()
        
        result = response.json()
        if result.get("error"):
            raise AnkiConnectError(f"AnkiConnect 错误: {result['error']}")
        
        return result.get("result")
    
    async def invoke(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """调用 AnkiConnect API，带重试机制"""
        async with self._semaphore:  # 限制并发请求
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    logger.debug(f"调用 AnkiConnect: {action} (尝试 {attempt + 1}/{self.max_retries + 1})")
                    result = await self._make_request(action, params)
                    
                    if attempt > 0:
                        logger.info(f"重试成功: {action}")
                    
                    return result
                
                except AnkiConnectError:
                    # AnkiConnect逻辑错误不应该重试
                    raise
                
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                        logger.warning(f"请求失败，{wait_time}秒后重试: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"请求最终失败: {e}")
            
            # 所有重试都失败了
            if isinstance(last_exception, httpx.RequestError):
                raise AnkiConnectError(f"连接 AnkiConnect 失败: {last_exception}")
            elif isinstance(last_exception, json.JSONDecodeError):
                raise AnkiConnectError(f"解析 AnkiConnect 响应失败: {last_exception}")
            else:
                raise AnkiConnectError(f"AnkiConnect 请求失败: {last_exception}")
    
    async def test_connection(self) -> bool:
        """测试与AnkiConnect的连接"""
        try:
            version = await self.invoke("version")
            logger.info(f"AnkiConnect 连接成功，版本: {version}")
            return True
        except Exception as e:
            logger.error(f"AnkiConnect 连接失败: {e}")
            return False
    
    async def close(self):
        """关闭客户端连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("AnkiConnect 客户端已关闭")

class AnkiConnectManager:
    """AnkiConnect 客户端管理器"""
    
    def __init__(self):
        self._client: Optional[AnkiConnectClient] = None
    
    async def get_client(self) -> AnkiConnectClient:
        """获取客户端实例"""
        if self._client is None:
            self._client = AnkiConnectClient()
            # 测试连接
            if not await self._client.test_connection():
                await self._client.close()
                self._client = None
                raise AnkiConnectError("无法连接到 AnkiConnect，请确保 Anki 正在运行并安装了 AnkiConnect 插件")
        
        return self._client
    
    async def close(self):
        """关闭管理器"""
        if self._client:
            await self._client.close()
            self._client = None

# 全局管理器实例
anki_manager = AnkiConnectManager()

@asynccontextmanager
async def get_anki_client():
    """异步上下文管理器，用于获取AnkiConnect客户端"""
    client = await anki_manager.get_client()
    try:
        yield client
    except Exception:
        raise

# ============================================================================
# 服务器初始化
# ============================================================================

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 验证配置
if not Config.validate():
    logger.error("配置验证失败，退出程序")
    sys.exit(1)

# 创建 FastMCP 实例
app = FastMCP(Config.SERVER_NAME, instructions=Config.SERVER_INSTRUCTIONS)

# ============================================================================
# 工具辅助类
# ============================================================================

class AnkiTools:
    """Anki工具集合类"""
    
    @staticmethod
    def should_filter_field(field_name: str, field_value: str) -> bool:
        """判断是否应该过滤掉某个字段"""
        field_name_lower = field_name.lower()
        
        # 过滤音频和图片字段
        if any(keyword in field_name_lower for keyword in ['audio', 'sound', 'image', 'picture']):
            return True
        
        # 过滤特定字段
        if field_name == "Add Reverse":
            return True
        
        # 过滤空值字段
        if not field_value or field_value.strip() == "":
            return True
        
        return False
    
    @staticmethod
    def format_note(note: Dict[str, Any]) -> str:
        """格式化单个笔记为可读格式"""
        lines = [f"<note id={note.get('noteId', 'unknown')}>"]
        
        fields = note.get('fields', {})
        for field_name, field_data in fields.items():
            # 获取字段值
            if isinstance(field_data, dict):
                field_value = field_data.get('value', '')
            else:
                field_value = str(field_data)
            
            # 过滤不需要的字段
            if AnkiTools.should_filter_field(field_name, field_value):
                continue
            
            lines.append(f"{field_name}: {field_value}")
        
        lines.append("</note>")
        return "\n".join(lines)
    
    @staticmethod
    def format_notes_list(notes: List[Dict[str, Any]]) -> str:
        """格式化笔记列表"""
        formatted_notes = []
        for note in notes:
            formatted_notes.append(AnkiTools.format_note(note))
        return "\n\n".join(formatted_notes)
    
    @staticmethod
    def format_response(action: str, data: Any, **extra) -> str:
        """格式化响应数据 - 现在返回纯文本而非JSON"""
        # 对于特定的action，使用特定的格式化
        if action == "find_notes":
            # 构建查找结果的文本输出
            lines = []
            lines.append(f"Found {data.get('total_count', 0)} notes matching '{data.get('query', '')}'")
            
            if data.get('returned_count', 0) > 0:
                lines.append(f"Showing {data.get('returned_count')} notes (offset: {data.get('offset', 0)})")
                
                # 如果有格式化的笔记内容，显示它
                if data.get('formatted_notes'):
                    lines.append("")
                    lines.append(data['formatted_notes'])
                # 否则显示ID列表
                elif data.get('note_ids'):
                    lines.append("")
                    lines.append("Note IDs:")
                    lines.append(", ".join(str(id) for id in data['note_ids']))
                
                if data.get('has_more'):
                    lines.append("")
                    lines.append(f"More results available. Use offset={data.get('next_offset')} to see next page.")
            
            return "\n".join(lines)
        
        elif action == "get_note_info" and "formatted_notes" in data:
            return data['formatted_notes']
        
        elif action == "get_due_cards" and "formatted_sample" in data:
            lines = []
            deck = data.get('deck_name', 'all decks')
            lines.append(f"Due cards in {deck}:")
            lines.append(f"- New: {data.get('new_cards', 0)}")
            lines.append(f"- Learning: {data.get('learning_cards', 0)}")
            lines.append(f"- Review: {data.get('review_cards', 0)}")
            lines.append(f"- Total: {data.get('total_due', 0)}")
            
            if data.get('formatted_sample'):
                lines.append("")
                lines.append("Sample cards:")
                lines.append(data['formatted_sample'])
            
            return "\n".join(lines)
        
        elif action == "get_deck_names":
            decks = data.get('decks', [])
            if not decks:
                return "No decks found"
            lines = [f"Found {len(decks)} decks:"]
            for deck in decks:
                lines.append(f"- {deck}")
            return "\n".join(lines)
        
        elif action == "get_deck_stats":
            lines = []
            lines.append(f"Stats for deck '{data.get('deck_name', 'Unknown')}':")
            lines.append(f"Total notes: {data.get('total_notes', 0)}")
            stats = data.get('stats', {})
            if stats:
                for key, value in stats.items():
                    lines.append(f"- {key}: {value}")
            return "\n".join(lines)
        
        # 默认格式化 - 返回简单的成功消息
        if data.get('success'):
            message = data.get('message', f"{action} completed successfully")
            return message
        
        # 如果没有特定格式，返回关键信息
        return str(data)
    
    @staticmethod
    def handle_error(action: str, error: Exception) -> str:
        """统一错误处理 - 返回纯文本错误消息"""
        error_msg = str(error)
        logger.error(f"{action} 失败: {error_msg}")
        return f"Error: {error_msg}"

# ============================================================================
# 基础工具 (8个)
# ============================================================================

@app.tool()
async def anki_get_deck_names() -> str:
    """获取所有卡组名称列表
    
    Returns:
        JSON格式的卡组列表，包含卡组数量
    """
    try:
        async with get_anki_client() as client:
            deck_names = await client.invoke("deckNames")
            
        return AnkiTools.format_response(
            "get_deck_names",
            {
                "decks": deck_names,
                "count": len(deck_names),
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_deck_names", e)

@app.tool()
async def anki_create_deck(deck_name: str) -> str:
    """创建新的卡组
    
    Args:
        deck_name: 卡组名称
        
    Returns:
        JSON格式的创建结果
    """
    try:
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        
        async with get_anki_client() as client:
            await client.invoke("createDeck", {"deck": deck_name})
            
        return AnkiTools.format_response(
            "create_deck",
            {
                "deck_name": deck_name,
                "success": True,
                "message": f"卡组 '{deck_name}' 创建成功"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("create_deck", e)

@app.tool()
async def anki_add_note(
    deck_name: str, 
    front: str, 
    back: str, 
    note_type: Optional[str] = None, 
    tags: Optional[List[str]] = None
) -> str:
    """添加新卡片到指定卡组
    
    Args:
        deck_name: 目标卡组名称
        front: 卡片正面内容
        back: 卡片背面内容
        note_type: 笔记类型（可选，默认为配置中的默认类型）
        tags: 标签列表（可选）
        
    Returns:
        JSON格式的添加结果，包含新卡片ID
    """
    try:
        # 参数验证
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        if not front.strip():
            raise ValueError("卡片正面内容不能为空")
        if not back.strip():
            raise ValueError("卡片背面内容不能为空")
        
        if note_type is None:
            note_type = Config.DEFAULT_NOTE_TYPE
        if tags is None:
            tags = []
        
        note = {
            "deckName": deck_name,
            "modelName": note_type,
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": tags
        }
        
        async with get_anki_client() as client:
            note_id = await client.invoke("addNote", {"note": note})
            
        return AnkiTools.format_response(
            "add_note",
            {
                "note_id": note_id,
                "deck_name": deck_name,
                "front": front,
                "back": back,
                "note_type": note_type,
                "tags": tags,
                "success": True,
                "message": f"卡片已添加到 '{deck_name}'，ID: {note_id}"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("add_note", e)

@app.tool()
async def anki_find_notes(query: str, limit: int = 20, offset: int = 0, with_content: bool = True) -> str:
    """根据查询条件查找卡片，支持分页和内容预览
    
    Args:
        query: 查询字符串（使用Anki查询语法）
        limit: 返回结果数量限制（默认20，设为0只返回总数）
        offset: 结果偏移量，用于分页（默认0）
        with_content: 是否获取卡片内容（默认True，设为False只返回ID列表）
        
    Returns:
        JSON格式的查找结果，包含卡片预览或ID列表
        
    Examples:
        - find_notes("tag:grammar") - 返回前20个语法卡片的内容
        - find_notes("deck:Japanese", limit=50) - 返回前50个日语卡片
        - find_notes("is:new", offset=20) - 跳过前20个，返回接下来的20个新卡片
        - find_notes("verb", with_content=False, limit=1000) - 快速获取所有动词卡片的ID
    """
    try:
        if not query.strip():
            raise ValueError("查询条件不能为空")
        
        async with get_anki_client() as client:
            # 获取所有匹配的笔记ID
            all_note_ids = await client.invoke("findNotes", {"query": query})
            total_count = len(all_note_ids)
            
            # 处理分页
            if limit == 0:
                # 只返回计数，不获取内容
                return AnkiTools.format_response(
                    "find_notes",
                    {
                        "query": query,
                        "total_count": total_count,
                        "message": f"Found {total_count} notes",
                        "success": True
                    }
                )
            
            # 获取分页后的ID子集
            start_idx = offset
            end_idx = offset + limit
            page_note_ids = all_note_ids[start_idx:end_idx]
            
            # 根据需要获取内容
            formatted_notes = ""
            notes_info = []
            if with_content and page_note_ids:
                notes_info = await client.invoke("notesInfo", {"notes": page_note_ids})
                formatted_notes = AnkiTools.format_notes_list(notes_info)
            
            # 构建响应
            response_data = {
                "query": query,
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "returned_count": len(page_note_ids),
                "note_ids": page_note_ids,
                "success": True
            }
            
            if with_content:
                response_data["formatted_notes"] = formatted_notes
                response_data["notes"] = notes_info
            
            # 添加分页提示信息
            if total_count > offset + limit:
                response_data["has_more"] = True
                response_data["next_offset"] = offset + limit
            else:
                response_data["has_more"] = False
            
            return AnkiTools.format_response("find_notes", response_data)
            
    except Exception as e:
        return AnkiTools.handle_error("find_notes", e)

@app.tool()
async def anki_get_note_info(note_ids: List[int]) -> str:
    """获取指定卡片的详细信息
    
    Args:
        note_ids: 卡片ID列表
        
    Returns:
        JSON格式的卡片详细信息
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("卡片ID必须为正整数")
        
        async with get_anki_client() as client:
            notes_info = await client.invoke("notesInfo", {"notes": note_ids})
            
        # 格式化笔记显示
        formatted_notes = AnkiTools.format_notes_list(notes_info)
        
        return AnkiTools.format_response(
            "get_note_info",
            {
                "formatted_notes": formatted_notes,
                "notes": notes_info,
                "count": len(notes_info),
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_note_info", e)

@app.tool()
async def anki_get_deck_stats(deck_name: str) -> str:
    """获取卡组统计信息
    
    Args:
        deck_name: 卡组名称
        
    Returns:
        JSON格式的卡组统计信息
    """
    try:
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        
        async with get_anki_client() as client:
            # 获取卡组统计
            all_stats = await client.invoke("getDeckStats", {"decks": [deck_name]})
            deck_stats = all_stats.get(deck_name, {})
            
            # 获取卡组中的卡片数量
            note_ids = await client.invoke("findNotes", {"query": f'deck:"{deck_name}"'})
            
        return AnkiTools.format_response(
            "get_deck_stats",
            {
                "deck_name": deck_name,
                "stats": deck_stats,
                "total_notes": len(note_ids),
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_deck_stats", e)

@app.tool()
async def anki_view_deck_contents(deck_name: str, limit: int = 20, offset: int = 0) -> str:
    """查看指定卡组的卡片内容
    
    Args:
        deck_name: 卡组名称
        limit: 显示卡片数量（默认20）
        offset: 跳过的卡片数量，用于分页（默认0）
        
    Returns:
        格式化的卡组内容列表
    """
    try:
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        
        # 使用find_notes来获取卡组内容
        return await anki_find_notes(f'deck:"{deck_name}"', limit=limit, offset=offset, with_content=True)
    except Exception as e:
        return AnkiTools.handle_error("view_deck_contents", e)

@app.tool()
async def anki_sync() -> str:
    """同步 Anki 数据库
    
    Returns:
        JSON格式的同步结果
    """
    try:
        async with get_anki_client() as client:
            await client.invoke("sync")
            
        return AnkiTools.format_response(
            "sync",
            {
                "success": True,
                "message": "同步完成"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("sync", e)

@app.tool()
async def anki_get_server_info() -> str:
    """获取服务器信息和配置
    
    Returns:
        JSON格式的服务器信息
    """
    try:
        config_info = Config.to_dict()
        
        # 测试AnkiConnect连接
        connection_status = "unknown"
        anki_version = None
        try:
            async with get_anki_client() as client:
                anki_version = await client.invoke("version")
                connection_status = "connected"
        except Exception:
            connection_status = "disconnected"
        
        return AnkiTools.format_response(
            "get_server_info",
            {
                "server_config": config_info,
                "anki_connect_status": connection_status,
                "anki_connect_version": anki_version,
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_server_info", e)

# ============================================================================
# 高优先级新功能：卡片编辑和删除
# ============================================================================

@app.tool()
async def anki_update_note(note_id: int, fields: Dict[str, str], tags: Optional[List[str]] = None) -> str:
    """更新现有卡片的内容
    
    Args:
        note_id: 要更新的卡片ID
        fields: 要更新的字段字典 (如 {"Front": "新问题", "Back": "新答案"})
        tags: 新的标签列表（可选，如果提供则替换所有标签）
        
    Returns:
        JSON格式的更新结果
    """
    try:
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("卡片ID必须为正整数")
        if not fields:
            raise ValueError("字段字典不能为空")
        
        update_data = {
            "note": {
                "id": note_id,
                "fields": fields
            }
        }
        
        if tags is not None:
            update_data["note"]["tags"] = tags
        
        async with get_anki_client() as client:
            await client.invoke("updateNoteFields", update_data)
            
            # 如果需要更新标签
            if tags is not None:
                await client.invoke("updateNoteTags", {
                    "note": note_id,
                    "tags": " ".join(tags)
                })
        
        return AnkiTools.format_response(
            "update_note",
            {
                "note_id": note_id,
                "updated_fields": fields,
                "updated_tags": tags,
                "success": True,
                "message": f"卡片 {note_id} 更新成功"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("update_note", e)

@app.tool()
async def anki_delete_notes(note_ids: List[int]) -> str:
    """批量删除卡片
    
    Args:
        note_ids: 要删除的卡片ID列表
        
    Returns:
        JSON格式的删除结果
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("所有卡片ID必须为正整数")
        
        async with get_anki_client() as client:
            await client.invoke("deleteNotes", {"notes": note_ids})
        
        return AnkiTools.format_response(
            "delete_notes",
            {
                "deleted_note_ids": note_ids,
                "count": len(note_ids),
                "success": True,
                "message": f"成功删除 {len(note_ids)} 张卡片"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("delete_notes", e)

@app.tool()
async def anki_move_notes(note_ids: List[int], target_deck: str) -> str:
    """将卡片移动到指定卡组
    
    Args:
        note_ids: 要移动的卡片ID列表
        target_deck: 目标卡组名称
        
    Returns:
        JSON格式的移动结果
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("所有卡片ID必须为正整数")
        if not target_deck.strip():
            raise ValueError("目标卡组名称不能为空")
        
        async with get_anki_client() as client:
            # 获取这些笔记的卡片ID
            card_ids = []
            for note_id in note_ids:
                cards = await client.invoke("findCards", {"query": f"nid:{note_id}"})
                card_ids.extend(cards)
            
            if not card_ids:
                raise ValueError("未找到对应的卡片")
            
            # 移动卡片到目标卡组
            await client.invoke("changeDeck", {
                "cards": card_ids,
                "deck": target_deck
            })
        
        return AnkiTools.format_response(
            "move_notes",
            {
                "moved_note_ids": note_ids,
                "target_deck": target_deck,
                "count": len(note_ids),
                "success": True,
                "message": f"Successfully moved {len(note_ids)} cards to '{target_deck}'"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("move_notes", e)

@app.tool()
async def anki_suspend_notes(note_ids: List[int], suspend: bool = True) -> str:
    """暂停或恢复卡片学习
    
    Args:
        note_ids: 卡片ID列表
        suspend: True为暂停，False为恢复
        
    Returns:
        JSON格式的操作结果
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("所有卡片ID必须为正整数")
        
        async with get_anki_client() as client:
            # 获取笔记对应的卡片
            cards_info = []
            for note_id in note_ids:
                cards = await client.invoke("findCards", {"query": f"nid:{note_id}"})
                cards_info.extend(cards)
            
            if suspend:
                await client.invoke("suspend", {"cards": cards_info})
                action_msg = "暂停"
            else:
                await client.invoke("unsuspend", {"cards": cards_info})
                action_msg = "恢复"
        
        return AnkiTools.format_response(
            "suspend_notes",
            {
                "affected_note_ids": note_ids,
                "affected_card_count": len(cards_info),
                "suspended": suspend,
                "success": True,
                "message": f"成功{action_msg} {len(note_ids)} 张卡片的学习"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("suspend_notes", e)

# ============================================================================
# 高优先级新功能：学习进度跟踪
# ============================================================================

@app.tool()
async def anki_get_due_cards(deck_name: Optional[str] = None) -> str:
    """获取到期需要复习的卡片信息
    
    Args:
        deck_name: 指定卡组名称（可选，不指定则获取所有卡组）
        
    Returns:
        JSON格式的到期卡片信息
    """
    try:
        async with get_anki_client() as client:
            if deck_name:
                query = f'deck:"{deck_name}" is:due'
            else:
                query = "is:due"
            
            # 获取到期卡片ID
            due_card_ids = await client.invoke("findCards", {"query": query})
            
            # 获取卡片详细信息
            cards_info = []
            notes_info = []
            if due_card_ids:
                cards_info = await client.invoke("cardsInfo", {"cards": due_card_ids[:50]})  # 限制返回数量
                
                # 获取对应的笔记信息
                note_ids = list(set(card.get('note') for card in cards_info if card.get('note')))
                if note_ids:
                    notes_info = await client.invoke("notesInfo", {"notes": note_ids[:20]})  # 限制数量
            
            # 统计不同类型的卡片
            new_cards = len(await client.invoke("findCards", {"query": f"{query} is:new"}))
            learning_cards = len(await client.invoke("findCards", {"query": f"{query} is:learn"}))
            review_cards = len(await client.invoke("findCards", {"query": f"{query} is:review"}))
        
        # 格式化笔记显示
        formatted_sample = ""
        if notes_info:
            formatted_sample = AnkiTools.format_notes_list(notes_info)
        
        return AnkiTools.format_response(
            "get_due_cards",
            {
                "deck_name": deck_name or "all_decks",
                "total_due": len(due_card_ids),
                "new_cards": new_cards,
                "learning_cards": learning_cards,
                "review_cards": review_cards,
                "formatted_sample": formatted_sample,
                "sample_cards": cards_info,
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_due_cards", e)

@app.tool()
async def anki_get_study_progress(deck_name: Optional[str] = None, days: int = 7) -> str:
    """获取学习进度统计
    
    Args:
        deck_name: 指定卡组名称（可选）
        days: 统计天数（默认7天）
        
    Returns:
        JSON格式的学习进度信息
    """
    try:
        if days <= 0:
            raise ValueError("统计天数必须为正数")
        
        async with get_anki_client() as client:
            deck_filter = f'deck:"{deck_name}"' if deck_name else ""
            
            # 获取基础统计
            all_cards = await client.invoke("findCards", {"query": deck_filter})
            new_cards = await client.invoke("findCards", {"query": f"{deck_filter} is:new"})
            mature_cards = await client.invoke("findCards", {"query": f"{deck_filter} prop:ivl>=21"})
            young_cards = await client.invoke("findCards", {"query": f"{deck_filter} prop:ivl<21 -is:new"})
            
            # 获取复习统计（近期）
            recent_reviews = await client.invoke("findCards", {"query": f"{deck_filter} rated:{days}"})
            
            # 计算学习效率指标
            total_cards = len(all_cards)
            if total_cards > 0:
                mature_percentage = (len(mature_cards) / total_cards) * 100
                new_percentage = (len(new_cards) / total_cards) * 100
            else:
                mature_percentage = 0
                new_percentage = 0
        
        return AnkiTools.format_response(
            "get_study_progress",
            {
                "deck_name": deck_name or "all_decks",
                "analysis_period_days": days,
                "total_cards": total_cards,
                "new_cards": len(new_cards),
                "young_cards": len(young_cards),
                "mature_cards": len(mature_cards),
                "recent_reviews": len(recent_reviews),
                "mature_percentage": round(mature_percentage, 2),
                "new_percentage": round(new_percentage, 2),
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_study_progress", e)

@app.tool()
async def anki_get_review_history(deck_name: Optional[str] = None, days: int = 30) -> str:
    """获取复习历史数据
    
    Args:
        deck_name: 指定卡组名称（可选）
        days: 历史天数（默认30天）
        
    Returns:
        JSON格式的复习历史信息
    """
    try:
        if days <= 0 or days > 365:
            raise ValueError("历史天数必须在1-365之间")
        
        async with get_anki_client() as client:
            deck_filter = f'deck:"{deck_name}"' if deck_name else ""
            
            # 获取不同评分的复习记录
            review_stats = {}
            for rating in [1, 2, 3, 4]:  # Again, Hard, Good, Easy
                query = f"{deck_filter} rated:{days}:{rating}"
                cards = await client.invoke("findCards", {"query": query})
                review_stats[f"rating_{rating}"] = len(cards)
            
            # 获取总复习次数
            total_reviews = await client.invoke("findCards", {"query": f"{deck_filter} rated:{days}"})
            
            # 计算成功率（Good + Easy）
            successful_reviews = review_stats["rating_3"] + review_stats["rating_4"]
            if len(total_reviews) > 0:
                success_rate = (successful_reviews / len(total_reviews)) * 100
            else:
                success_rate = 0
                
            # 获取平均间隔信息
            studied_cards = await client.invoke("findCards", {"query": f"{deck_filter} -is:new"})
        
        return AnkiTools.format_response(
            "get_review_history",
            {
                "deck_name": deck_name or "all_decks",
                "period_days": days,
                "total_reviews": len(total_reviews),
                "again_count": review_stats["rating_1"],
                "hard_count": review_stats["rating_2"],
                "good_count": review_stats["rating_3"],
                "easy_count": review_stats["rating_4"],
                "success_rate_percentage": round(success_rate, 2),
                "total_studied_cards": len(studied_cards),
                "success": True
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_review_history", e)

# ============================================================================
# 高优先级新功能：批量操作
# ============================================================================

@app.tool()
async def anki_batch_add_notes(notes_data: List[Dict[str, Any]], deck_name: str) -> str:
    """批量添加卡片到指定卡组
    
    Args:
        notes_data: 卡片数据列表，每个元素包含 {"front": "问题", "back": "答案", "tags": ["标签1"]}
        deck_name: 目标卡组名称
        
    Returns:
        JSON格式的批量添加结果
    """
    try:
        if not notes_data:
            raise ValueError("卡片数据列表不能为空")
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        
        # 验证数据格式
        for i, note_data in enumerate(notes_data):
            if not isinstance(note_data, dict):
                raise ValueError(f"第{i+1}个卡片数据格式错误，必须为字典")
            if "front" not in note_data or "back" not in note_data:
                raise ValueError(f"第{i+1}个卡片缺少front或back字段")
        
        async with get_anki_client() as client:
            # 准备批量添加的笔记
            notes_to_add = []
            for note_data in notes_data:
                note = {
                    "deckName": deck_name,
                    "modelName": Config.DEFAULT_NOTE_TYPE,
                    "fields": {
                        "Front": note_data["front"],
                        "Back": note_data["back"]
                    },
                    "tags": note_data.get("tags", [])
                }
                notes_to_add.append(note)
            
            # 批量添加
            result = await client.invoke("addNotes", {"notes": notes_to_add})
            
            # 统计结果
            successful_ids = [nid for nid in result if nid is not None]
            failed_count = len([nid for nid in result if nid is None])
        
        return AnkiTools.format_response(
            "batch_add_notes",
            {
                "deck_name": deck_name,
                "total_attempted": len(notes_data),
                "successful_count": len(successful_ids),
                "failed_count": failed_count,
                "successful_note_ids": successful_ids,
                "success": True,
                "message": f"批量添加完成：成功 {len(successful_ids)} 张，失败 {failed_count} 张"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("batch_add_notes", e)

@app.tool()
async def anki_batch_update_tags(note_ids: List[int], add_tags: Optional[List[str]] = None, remove_tags: Optional[List[str]] = None) -> str:
    """批量更新卡片标签
    
    Args:
        note_ids: 卡片ID列表
        add_tags: 要添加的标签列表（可选）
        remove_tags: 要移除的标签列表（可选）
        
    Returns:
        JSON格式的批量更新结果
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("所有卡片ID必须为正整数")
        if not add_tags and not remove_tags:
            raise ValueError("必须指定要添加或移除的标签")
        
        async with get_anki_client() as client:
            updated_count = 0
            
            for note_id in note_ids:
                try:
                    # 添加标签
                    if add_tags:
                        await client.invoke("addTags", {
                            "notes": [note_id],
                            "tags": " ".join(add_tags)
                        })
                    
                    # 移除标签
                    if remove_tags:
                        await client.invoke("removeTags", {
                            "notes": [note_id],
                            "tags": " ".join(remove_tags)
                        })
                    
                    updated_count += 1
                except Exception:
                    continue  # 跳过失败的卡片
        
        return AnkiTools.format_response(
            "batch_update_tags",
            {
                "total_notes": len(note_ids),
                "updated_count": updated_count,
                "failed_count": len(note_ids) - updated_count,
                "added_tags": add_tags or [],
                "removed_tags": remove_tags or [],
                "success": True,
                "message": f"批量标签更新完成：成功 {updated_count} 张，失败 {len(note_ids) - updated_count} 张"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("batch_update_tags", e)

@app.tool()
async def anki_export_deck(deck_name: str, include_media: bool = False) -> str:
    """导出指定卡组
    
    Args:
        deck_name: 要导出的卡组名称
        include_media: 是否包含媒体文件
        
    Returns:
        JSON格式的导出结果信息
    """
    try:
        if not deck_name.strip():
            raise ValueError("卡组名称不能为空")
        
        async with get_anki_client() as client:
            # 导出卡组
            export_result = await client.invoke("exportPackage", {
                "deck": deck_name,
                "path": f"{deck_name}_export.apkg",
                "includeSched": True,
                "includeMedia": include_media
            })
            
            # 获取卡组统计信息
            notes_in_deck = await client.invoke("findNotes", {"query": f'deck:"{deck_name}"'})
        
        return AnkiTools.format_response(
            "export_deck",
            {
                "deck_name": deck_name,
                "export_path": f"{deck_name}_export.apkg",
                "include_media": include_media,
                "total_notes_exported": len(notes_in_deck),
                "success": True,
                "message": f"卡组 '{deck_name}' 导出成功，包含 {len(notes_in_deck)} 张卡片"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("export_deck", e)

@app.tool()
async def anki_change_note_type(note_ids: List[int], target_model: str, field_mapping: Optional[Dict[str, str]] = None) -> str:
    """更改卡片的笔记类型（模板）
    
    Args:
        note_ids: 要更改的卡片ID列表
        target_model: 目标笔记类型名称
        field_mapping: 字段映射字典（可选），格式为 {"原字段名": "新字段名"}
        
    Returns:
        JSON格式的更改结果
    """
    try:
        if not note_ids:
            raise ValueError("卡片ID列表不能为空")
        if not all(isinstance(nid, int) and nid > 0 for nid in note_ids):
            raise ValueError("所有卡片ID必须为正整数")
        if not target_model.strip():
            raise ValueError("目标笔记类型名称不能为空")
        
        async with get_anki_client() as client:
            # 1. 检查目标模板是否存在
            model_names = await client.invoke("modelNames")
            if target_model not in model_names:
                raise ValueError(f"目标笔记类型 '{target_model}' 不存在。可用类型: {', '.join(model_names[:10])}{'...' if len(model_names) > 10 else ''}")
            
            # 2. 获取原始卡片信息
            original_notes = await client.invoke("notesInfo", {"notes": note_ids})
            if not original_notes:
                raise ValueError("未找到指定的卡片")
            
            # 3. 准备新卡片数据
            new_notes = []
            current_model = original_notes[0].get('modelName', 'Unknown')
            
            for note in original_notes:
                original_fields = note.get('fields', {})
                original_tags = note.get('tags', [])
                deck_name = note.get('deck', 'Default')
                
                # 构建新的字段数据
                new_fields = {}
                if field_mapping:
                    # 使用提供的字段映射
                    for old_field, new_field in field_mapping.items():
                        if old_field in original_fields:
                            new_fields[new_field] = original_fields[old_field].get('value', '')
                else:
                    # 自动映射：尝试保持相同字段名
                    for field_name, field_data in original_fields.items():
                        new_fields[field_name] = field_data.get('value', '')
                
                new_note = {
                    "deckName": deck_name,
                    "modelName": target_model,
                    "fields": new_fields,
                    "tags": original_tags
                }
                new_notes.append(new_note)
            
            # 4. 删除原始卡片
            await client.invoke("deleteNotes", {"notes": note_ids})
            
            # 5. 创建新卡片
            result = await client.invoke("addNotes", {"notes": new_notes})
            
            # 6. 统计结果
            successful_new_ids = [nid for nid in result if nid is not None]
            failed_count = len(result) - len(successful_new_ids)
            
        return AnkiTools.format_response(
            "change_note_type",
            {
                "original_note_ids": note_ids,
                "new_note_ids": successful_new_ids,
                "original_model": current_model,
                "target_model": target_model,
                "total_processed": len(note_ids),
                "successful_count": len(successful_new_ids),
                "failed_count": failed_count,
                "field_mapping_used": field_mapping or "auto",
                "success": True,
                "message": f"成功将 {len(successful_new_ids)} 张卡片从 '{current_model}' 更改为 '{target_model}'"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("change_note_type", e)

@app.tool()
async def anki_get_note_types() -> str:
    """获取所有可用的笔记类型
    
    Returns:
        JSON格式的笔记类型列表
    """
    try:
        async with get_anki_client() as client:
            model_names = await client.invoke("modelNames")
            
            # 获取每个模型的详细信息
            model_details = []
            for model_name in model_names[:20]:  # 限制数量避免太长
                try:
                    model_info = await client.invoke("modelFieldNames", {"modelName": model_name})
                    model_details.append({
                        "name": model_name,
                        "fields": model_info
                    })
                except Exception:
                    model_details.append({
                        "name": model_name,
                        "fields": ["获取字段信息失败"]
                    })
        
        return AnkiTools.format_response(
            "get_note_types",
            {
                "total_count": len(model_names),
                "note_types": model_names,
                "detailed_info": model_details,
                "success": True,
                "message": f"找到 {len(model_names)} 个笔记类型"
            }
        )
    except Exception as e:
        return AnkiTools.handle_error("get_note_types", e)

async def cleanup():
    """清理资源"""
    logger.info("正在清理资源...")
    try:
        await anki_manager.close()
        logger.info("资源清理完成")
    except Exception as e:
        logger.error(f"资源清理失败: {e}")

def setup_signal_handlers():
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，准备退出...")
        asyncio.create_task(cleanup())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """主函数"""
    logger.info(f"启动 {Config.SERVER_NAME} v{Config.SERVER_VERSION}")
    
    # 设置信号处理器
    setup_signal_handlers()
    
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
    finally:
        # 在主线程中处理清理
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(cleanup())
            loop.close()
        except Exception as e:
            logger.error(f"最终清理失败: {e}")

if __name__ == "__main__":
    main() 