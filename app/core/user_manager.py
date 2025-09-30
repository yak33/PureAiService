"""
用户管理模块 - 使用 JSON 文件存储用户信息
Author: ZHANGCHAO
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.core.logger import app_logger

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用户数据文件路径
USER_DATA_FILE = "data/users.json"


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化用户管理器"""
        self._ensure_data_dir()
        self._ensure_default_admin()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        if not os.path.exists(USER_DATA_FILE):
            self._save_users({})
    
    def _ensure_default_admin(self):
        """确保默认管理员账号存在"""
        from dotenv import load_dotenv
        load_dotenv()
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "123456")
        default_nickname = "🍒樱桃七喜丸子"
        
        users = self._load_users()
        if default_username not in users:
            self.create_user(default_username, default_password, default_nickname)
            app_logger.info(f"创建默认管理员账号: {default_username}")
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict):
        """保存用户数据"""
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def get_password_hash(self, password: str) -> str:
        """加密密码"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, password: str, nickname: str = None) -> bool:
        """
        创建用户
        
        Args:
            username: 用户名
            password: 密码（明文）
            nickname: 昵称（可选，默认使用用户名）
            
        Returns:
            是否创建成功
        """
        users = self._load_users()
        
        # 检查用户是否已存在
        if username in users:
            return False
        
        # 创建新用户
        users[username] = {
            "username": username,
            "nickname": nickname or username,  # 如果没有昵称，使用用户名
            "password_hash": self.get_password_hash(password),
            "created_at": datetime.now().isoformat()  # 使用当前时间
        }
        
        self._save_users(users)
        app_logger.info(f"创建新用户: {username}, 昵称: {nickname or username}")
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        验证用户
        
        Args:
            username: 用户名
            password: 密码（明文）
            
        Returns:
            验证是否成功
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        user = users[username]
        return self.verify_password(password, user["password_hash"])
    
    def user_exists(self, username: str) -> bool:
        """
        检查用户是否存在
        
        Args:
            username: 用户名
            
        Returns:
            用户是否存在
        """
        users = self._load_users()
        return username in users
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户信息（不包含密码）
        """
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username].copy()
        user.pop("password_hash", None)  # 移除密码哈希
        return user
    
    def list_users(self) -> List[str]:
        """
        获取所有用户名列表
        
        Returns:
            用户名列表
        """
        users = self._load_users()
        return list(users.keys())
    
    def update_nickname(self, username: str, nickname: str) -> bool:
        """
        更新用户昵称
        
        Args:
            username: 用户名
            nickname: 新昵称
            
        Returns:
            是否更新成功
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        users[username]["nickname"] = nickname
        self._save_users(users)
        app_logger.info(f"更新用户昵称: {username} -> {nickname}")
        return True
    
    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        更新用户密码
        
        Args:
            username: 用户名
            old_password: 旧密码（明文）
            new_password: 新密码（明文）
            
        Returns:
            是否更新成功
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        # 验证旧密码
        if not self.verify_password(old_password, users[username]["password_hash"]):
            return False
        
        # 更新密码
        users[username]["password_hash"] = self.get_password_hash(new_password)
        self._save_users(users)
        app_logger.info(f"更新用户密码: {username}")
        return True


# 全局用户管理器实例
user_manager = UserManager()
