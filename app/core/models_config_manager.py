"""
模型配置管理器
用于管理用户选择的可用模型配置

作者: ZHANGCHAO
"""

import os
import json
from typing import List, Dict, Any
from app.core.logger import app_logger

# 模型配置文件路径
MODELS_CONFIG_FILE = "data/models_config.json"


class ModelsConfigManager:
    """模型配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """确保配置文件存在"""
        os.makedirs(os.path.dirname(MODELS_CONFIG_FILE), exist_ok=True)
        if not os.path.exists(MODELS_CONFIG_FILE):
            # 创建默认配置
            default_config = {
                "enabled_models": [],
                "updated_at": None
            }
            self._save_config(default_config)
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置到文件"""
        try:
            with open(MODELS_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            app_logger.info("模型配置已保存")
        except Exception as e:
            app_logger.error(f"保存模型配置失败: {e}")
            raise
    
    def _load_config(self) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            with open(MODELS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            app_logger.error(f"加载模型配置失败: {e}")
            return {"enabled_models": [], "updated_at": None}
    
    def get_enabled_models(self) -> List[Dict[str, Any]]:
        """
        获取已启用的模型列表
        
        Returns:
            List[Dict]: 启用的模型列表
        """
        config = self._load_config()
        return config.get("enabled_models", [])
    
    def save_enabled_models(self, models: List[Dict[str, Any]]) -> bool:
        """
        保存启用的模型列表
        
        Args:
            models: 模型列表，每个模型包含 id, object, created, owned_by 等字段
            
        Returns:
            bool: 是否保存成功
        """
        try:
            from datetime import datetime
            config = {
                "enabled_models": models,
                "updated_at": datetime.now().isoformat()
            }
            self._save_config(config)
            app_logger.info(f"已保存 {len(models)} 个模型配置")
            return True
        except Exception as e:
            app_logger.error(f"保存模型配置失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置信息
        
        Returns:
            Dict: 包含模型数量、更新时间等信息
        """
        config = self._load_config()
        return {
            "total_models": len(config.get("enabled_models", [])),
            "updated_at": config.get("updated_at"),
            "config_file": MODELS_CONFIG_FILE
        }


# 全局实例
models_config_manager = ModelsConfigManager()
