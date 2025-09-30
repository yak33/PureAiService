"""
认证API接口
Author: ZHANGCHAO
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.logger import app_logger

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    nickname: Optional[str] = None
    password: str
    confirm_password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（分钟）


class UserInfo(BaseModel):
    """用户信息"""
    username: str


@router.post("/login", summary="用户登录")
async def login(request: LoginRequest):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    Returns:
        JWT Token、过期时间和昵称
    """
    from app.core.user_manager import user_manager
    
    # 验证用户名和密码
    if not authenticate_user(request.username, request.password):
        app_logger.warning(f"登录失败: username={request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户信息
    user = user_manager.get_user(request.username)
    nickname = user.get("nickname", request.username) if user else request.username
    
    # 创建 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=access_token_expires
    )
    
    app_logger.info(f"用户登录成功: username={request.username}, nickname={nickname}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES,
        "nickname": nickname
    }


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要在请求头中携带有效的 JWT Token:
    Authorization: Bearer <token>
    """
    return UserInfo(username=current_user["username"])


@router.post("/logout", summary="用户登出")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出接口
    
    前端应该清除本地存储的 Token
    """
    app_logger.info(f"用户登出: username={current_user['username']}")
    return {"message": "登出成功"}


@router.post("/register", summary="用户注册")
async def register(request: RegisterRequest):
    """
    用户注册接口
    
    - **username**: 用户名（3-20个字符）
    - **password**: 密码（至少6个字符）
    - **confirm_password**: 确认密码
    
    Returns:
        注册结果
    """
    from app.core.user_manager import user_manager
    
    # 验证用户名长度
    if len(request.username) < 3 or len(request.username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在 3-20 个字符之间"
        )
    
    # 验证密码长度
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为 6 个字符"
        )
    
    # 验证两次密码是否一致
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )
    
    # 检查用户名是否已存在
    if user_manager.user_exists(request.username):
        app_logger.warning(f"注册失败，用户名已存在: username={request.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户（传入昵称）
    success = user_manager.create_user(request.username, request.password, request.nickname)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )
    
    app_logger.info(f"用户注册成功: username={request.username}")
    
    return {
        "message": "注册成功",
        "username": request.username
    }


class UpdateProfileRequest(BaseModel):
    """更新用户信息请求"""
    nickname: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None


@router.put("/profile", summary="更新用户信息")
async def update_profile(request: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    """
    更新用户信息接口
    
    - **nickname**: 新昵称（可选）
    - **old_password**: 旧密码（修改密码时必填）
    - **new_password**: 新密码（可选）
    
    Returns:
        更新结果
    """
    from app.core.user_manager import user_manager
    
    username = current_user["username"]
    updated = False
    
    # 更新昵称
    if request.nickname:
        if len(request.nickname) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称长度不能超过20个字符"
            )
        success = user_manager.update_nickname(username, request.nickname)
        if success:
            updated = True
            app_logger.info(f"用户更新昵称: username={username}, nickname={request.nickname}")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新昵称失败"
            )
    
    # 更新密码
    if request.new_password:
        if not request.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码需要提供旧密码"
            )
        
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码长度至少为6个字符"
            )
        
        success = user_manager.update_password(username, request.old_password, request.new_password)
        if success:
            updated = True
            app_logger.info(f"用户更新密码: username={username}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有需要更新的信息"
        )
    
    # 返回最新的用户信息
    user = user_manager.get_user(username)
    return {
        "message": "更新成功",
        "nickname": user.get("nickname", username) if user else username
    }
