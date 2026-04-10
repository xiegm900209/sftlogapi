"""
API Key 鉴权模块
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
from flask import request, jsonify


class APIKeyManager:
    """API Key 管理器"""
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.api_keys = {}
        self.rate_limits = defaultdict(list)
        self.load_keys()
    
    def load_keys(self):
        """加载 API Key 配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_keys = config.get('api_keys', {})
                    self.settings = config.get('settings', {})
            except Exception as e:
                print(f"加载 API Key 配置失败：{e}")
                self.api_keys = {}
                self.settings = {}
        else:
            print(f"API Key 配置文件不存在：{self.config_path}")
            self.api_keys = {}
            self.settings = {}
    
    def validate(self, api_key):
        """验证 API Key 是否有效"""
        if not api_key:
            return False
        
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        return key_info.get('enabled', False)
    
    def get_key_info(self, api_key):
        """获取 API Key 信息"""
        if api_key in self.api_keys:
            return self.api_keys[api_key]
        return None
    
    def check_rate_limit(self, api_key):
        """检查速率限制"""
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        limit = key_info.get('rate_limit', self.settings.get('default_rate_limit', 10))
        period = key_info.get('rate_limit_period', self.settings.get('default_rate_limit_period', 'minute'))
        
        now = datetime.now()
        
        # 计算时间窗口
        if period == 'minute':
            window = timedelta(minutes=1)
        elif period == 'hour':
            window = timedelta(hours=1)
        else:
            window = timedelta(minutes=1)
        
        # 清理过期记录
        self.rate_limits[api_key] = [
            t for t in self.rate_limits[api_key]
            if now - t < window
        ]
        
        # 检查是否超限
        if len(self.rate_limits[api_key]) >= limit:
            return False
        
        # 记录本次请求
        self.rate_limits[api_key].append(now)
        return True
    
    def get_remaining_requests(self, api_key):
        """获取剩余请求次数"""
        if api_key not in self.api_keys:
            return 0
        
        key_info = self.api_keys[api_key]
        limit = key_info.get('rate_limit', self.settings.get('default_rate_limit', 10))
        period = key_info.get('rate_limit_period', 'minute')
        
        now = datetime.now()
        window = timedelta(minutes=1) if period == 'minute' else timedelta(hours=1)
        
        # 清理过期记录
        self.rate_limits[api_key] = [
            t for t in self.rate_limits[api_key]
            if now - t < window
        ]
        
        return max(0, limit - len(self.rate_limits[api_key]))


# 全局 API Key 管理器实例
_api_key_manager = None


def get_api_key_manager():
    """获取全局 API Key 管理器"""
    global _api_key_manager
    if _api_key_manager is None:
        config_path = '/root/sft/sftlogapi/config/api_keys.json'
        _api_key_manager = APIKeyManager(config_path)
    return _api_key_manager


def require_api_key(f):
    """API Key 鉴权装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从 Header 或 Query 获取 API Key
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
        else:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': '缺少 API Key',
                'code': 'MISSING_API_KEY',
                'message': '请在请求头中提供 Authorization: Bearer <api_key> 或在查询参数中提供 api_key'
            }), 401
        
        manager = get_api_key_manager()
        
        # 验证 API Key
        if not manager.validate(api_key):
            return jsonify({
                'success': False,
                'error': '无效的 API Key',
                'code': 'INVALID_API_KEY',
                'message': '提供的 API Key 无效或已被禁用'
            }), 401
        
        # 检查速率限制
        if not manager.check_rate_limit(api_key):
            key_info = manager.get_key_info(api_key)
            return jsonify({
                'success': False,
                'error': '请求频率超限',
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': f'请求频率超过限制，请稍后重试',
                'rate_limit': key_info.get('rate_limit'),
                'rate_limit_period': key_info.get('rate_limit_period')
            }), 429
        
        # 将 API Key 信息传递给处理函数
        request.api_key = api_key
        request.api_key_info = manager.get_key_info(api_key)
        request.api_key_remaining = manager.get_remaining_requests(api_key)
        
        return f(*args, **kwargs)
    
    return decorated
