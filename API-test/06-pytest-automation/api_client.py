"""
API Client - HTTP客户端封装
封装BaseURL、日志、认证等功能
"""
import json
import logging
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class APIClient:
    """API HTTP客户端"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化API客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None

    def set_token(self, token: str):
        """设置认证token"""
        self.token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
        logger.info(f"Token已设置: {token[:20]}...")

    def clear_token(self):
        """清除认证token"""
        self.token = None
        self.session.headers.pop('Authorization', None)
        logger.info("Token已清除")

    def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            path: API路径
            json_data: JSON请求体
            params: URL参数
            **kwargs: 其他requests参数

        Returns:
            Response对象
        """
        url = f"{self.base_url}{path}"

        # 记录请求
        logger.info(f"请求: {method} {url}")
        if json_data:
            logger.info(f"请求体: {json.dumps(json_data, ensure_ascii=False)}")

        # 发送请求
        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
            timeout=self.timeout,
            **kwargs
        )

        # 记录响应
        logger.info(f"响应状态码: {response.status_code}")
        try:
            response_json = response.json()
            logger.info(f"响应体: {json.dumps(response_json, ensure_ascii=False)}")
        except:
            logger.info(f"响应体: {response.text[:200]}")

        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        """GET请求"""
        return self.request('GET', path, **kwargs)

    def post(self, path: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """POST请求"""
        return self.request('POST', path, json_data=json_data, **kwargs)

    def put(self, path: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """PUT请求"""
        return self.request('PUT', path, json_data=json_data, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """DELETE请求"""
        return self.request('DELETE', path, **kwargs)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录响应数据
        """
        response = self.post('/api/auth/login', json_data={
            'username': username,
            'password': password
        })
        data = response.json()

        if response.status_code == 200 and data.get('code') == 200:
            token = data['data']['token']
            self.set_token(token)
            logger.info(f"用户 {username} 登录成功")
        else:
            logger.warning(f"用户 {username} 登录失败: {data.get('message')}")

        return data

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("API客户端会话已关闭")