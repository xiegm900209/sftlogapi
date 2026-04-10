#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智多星 AI - sftlogapi 集成客户端

提供完整的 API 调用、日志分析、知识库集成功能
"""

import requests
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# ============================================
# 配置
# ============================================

@dataclass
class Config:
    """配置类"""
    base_url: str = "http://172.16.2.164:8090/sftlogapi"
    api_key: str = "zhiduoxing-prod"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


# ============================================
# 数据模型
# ============================================

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    service: str
    thread: str
    level: str
    content: str
    parsed: Dict[str, Any]


@dataclass
class TransactionSummary:
    """交易摘要"""
    transaction_type: str
    transaction_name: str
    trace_id: str
    req_sn: str
    status: str
    total_logs: int
    service_count: int
    duration_ms: int
    start_time: str
    end_time: str
    services: List[str]


@dataclass
class QueryResult:
    """查询结果"""
    success: bool
    summary: Optional[TransactionSummary]
    logs: List[LogEntry]
    service_logs: Dict[str, List[LogEntry]]
    error: Optional[str]
    query_time_ms: int


# ============================================
# 智多星客户端
# ============================================

class SFTLogClient:
    """sftlogapi 客户端"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        })
        self._transaction_types_cache = None
        self._services_cache = None
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """发送 HTTP 请求"""
        url = f"{self.config.base_url}{path}"
        
        for i in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method, url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                if i == self.config.max_retries - 1:
                    raise
                time.sleep(self.config.retry_delay * (2 ** i))
        
        return {}
    
    def query_transaction(self, transaction_type: str, req_sn: str, 
                         log_time: str, service: str = None) -> QueryResult:
        """
        查询交易链路日志
        
        Args:
            transaction_type: 交易类型代码，如 "310011"
            req_sn: 交易序列号，如 "LX260408090024C80C82F3"
            log_time: 日志时间，10 位数字 YYYYMMDDHH
            service: 可选，指定服务
        
        Returns:
            QueryResult: 查询结果
        """
        params = {
            "transaction_type": transaction_type,
            "req_sn": req_sn,
            "log_time": log_time
        }
        
        if service:
            params["service"] = service
        
        result = self._request('POST', '/api/ai/query', json={
            "query_type": "transaction_trace",
            "params": params
        })
        
        if not result.get('success'):
            return QueryResult(
                success=False,
                summary=None,
                logs=[],
                service_logs={},
                error=result.get('error', '未知错误'),
                query_time_ms=0
            )
        
        data = result.get('data', {})
        logs = self._parse_logs(data.get('logs', []))
        service_logs = {
            svc: self._parse_logs(log_list)
            for svc, log_list in data.get('service_results', {}).items()
        }
        
        summary = TransactionSummary(
            transaction_type=data.get('transaction_type', ''),
            transaction_name=data.get('transaction_name', ''),
            trace_id=data.get('trace_id', ''),
            req_sn=req_sn,
            status=data.get('summary', {}).get('status', 'unknown'),
            total_logs=data.get('total_logs', 0),
            service_count=data.get('service_count', 0),
            duration_ms=self._calculate_duration(
                data.get('summary', {}).get('start_time'),
                data.get('summary', {}).get('end_time')
            ),
            start_time=data.get('summary', {}).get('start_time', ''),
            end_time=data.get('summary', {}).get('end_time', ''),
            services=data.get('services', [])
        )
        
        return QueryResult(
            success=True,
            summary=summary,
            logs=logs,
            service_logs=service_logs,
            error=None,
            query_time_ms=result.get('metadata', {}).get('query_time_ms', 0)
        )
    
    def _parse_logs(self, log_list: List[Dict]) -> List[LogEntry]:
        """解析日志列表"""
        return [
            LogEntry(
                timestamp=log.get('timestamp', ''),
                service=log.get('service', ''),
                thread=log.get('thread', ''),
                level=log.get('level', ''),
                content=log.get('content', ''),
                parsed=log.get('parsed', {})
            )
            for log in log_list
        ]
    
    def _calculate_duration(self, start: str, end: str) -> int:
        """计算耗时（毫秒）"""
        try:
            fmt = "%Y-%m-%d %H:%M:%S.%f"
            start_dt = datetime.strptime(start, fmt)
            end_dt = datetime.strptime(end, fmt)
            return int((end_dt - start_dt).total_seconds() * 1000)
        except:
            return 0
    
    def get_transaction_types(self) -> Dict[str, Dict]:
        """获取交易类型列表（带缓存）"""
        if self._transaction_types_cache:
            return self._transaction_types_cache
        
        result = self._request('GET', '/api/ai/transaction-types')
        if result.get('success'):
            self._transaction_types_cache = result.get('data', {})
        
        return self._transaction_types_cache or {}
    
    def get_services(self) -> List[str]:
        """获取服务列表（带缓存）"""
        if self._services_cache:
            return self._services_cache
        
        result = self._request('GET', '/api/ai/services')
        if result.get('success'):
            self._services_cache = result.get('data', [])
        
        return self._services_cache or []
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            result = self._request('GET', '/api/ai/health')
            return result.get('status') == 'healthy'
        except:
            return False


# ============================================
# 智多星分析器
# ============================================

class ZhiduoxingAnalyzer:
    """智多星日志分析器"""
    
    def __init__(self, client: SFTLogClient):
        self.client = client
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        return {
            'transaction_types': {},
            'error_patterns': [
                (r'error', 'ERROR'),
                (r'fail', 'FAILED'),
                (r'exception', 'EXCEPTION'),
                (r'timeout', 'TIMEOUT'),
            ],
            'service_descriptions': {
                'sft-aipg': '协议支付网关',
                'sft-trxqry': '交易查询服务',
                'sft-pay': '支付服务',
                'sft-merapi': '商户 API 服务',
                'sft-trxcharge': '交易计费服务',
                'sft-chnlagent': '渠道代理服务',
            }
        }
    
    def analyze_transaction(self, result: QueryResult) -> Dict:
        """
        分析交易日志
        
        Args:
            result: 查询结果
        
        Returns:
            Dict: 分析结果
        """
        if not result.success:
            return {
                'success': False,
                'error': result.error,
                'suggestion': '请检查参数后重试'
            }
        
        summary = result.summary
        
        # 1. 提取关键信息
        transaction_info = self._extract_transaction_info(result.logs)
        
        # 2. 分析交易流程
        flow_analysis = self._analyze_flow(result.service_logs)
        
        # 3. 检测异常
        anomalies = self._detect_anomalies(result.logs)
        
        # 4. 生成建议
        suggestions = self._generate_suggestions(summary, anomalies)
        
        return {
            'success': True,
            'summary': asdict(summary),
            'transaction_info': transaction_info,
            'flow_analysis': flow_analysis,
            'anomalies': anomalies,
            'suggestions': suggestions,
            'user_message': self._generate_user_message(summary, transaction_info, anomalies)
        }
    
    def _extract_transaction_info(self, logs: List[LogEntry]) -> Dict:
        """提取交易关键信息"""
        info = {}
        
        for log in logs:
            parsed = log.parsed
            if parsed.get('req_sn') and 'req_sn' not in info:
                info['req_sn'] = parsed['req_sn']
            if parsed.get('merchant_id') and 'merchant_id' not in info:
                info['merchant_id'] = parsed['merchant_id']
            if parsed.get('amount') and 'amount' not in info:
                info['amount'] = parsed['amount']
            if parsed.get('trx_code') and 'trx_code' not in info:
                info['trx_code'] = parsed['trx_code']
            if parsed.get('user_name') and 'user_name' not in info:
                info['user_name'] = parsed['user_name']
        
        return info
    
    def _analyze_flow(self, service_logs: Dict[str, List[LogEntry]]) -> Dict:
        """分析交易流程"""
        flow = []
        
        for service, logs in sorted(service_logs.items(), key=lambda x: x[0]):
            desc = self.knowledge_base['service_descriptions'].get(
                service, service
            )
            flow.append({
                'service': service,
                'description': desc,
                'log_count': len(logs),
                'first_time': logs[0].timestamp if logs else '',
                'last_time': logs[-1].timestamp if logs else ''
            })
        
        return {
            'total_services': len(flow),
            'flow': flow
        }
    
    def _detect_anomalies(self, logs: List[LogEntry]) -> List[Dict]:
        """检测异常"""
        anomalies = []
        
        for log in logs:
            # 检查错误级别
            if log.level in ['ERROR', 'FATAL', 'CRITICAL']:
                anomalies.append({
                    'type': 'ERROR_LEVEL',
                    'severity': 'high',
                    'timestamp': log.timestamp,
                    'service': log.service,
                    'content': log.content[:200]
                })
            
            # 检查错误关键字
            for pattern, error_type in self.knowledge_base['error_patterns']:
                if re.search(pattern, log.content, re.IGNORECASE):
                    anomalies.append({
                        'type': error_type,
                        'severity': 'medium',
                        'timestamp': log.timestamp,
                        'service': log.service,
                        'content': log.content[:200]
                    })
                    break
        
        return anomalies
    
    def _generate_suggestions(self, summary: TransactionSummary, 
                            anomalies: List[Dict]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if summary.status == 'failed':
            suggestions.append('❌ 交易失败，请检查错误日志')
        
        if len(anomalies) > 0:
            suggestions.append(f'⚠️ 发现 {len(anomalies)} 个异常，请重点关注')
        
        if summary.duration_ms > 5000:
            suggestions.append(f'⏱️ 交易耗时较长 ({summary.duration_ms}ms)，建议优化')
        
        if summary.service_count > 10:
            suggestions.append(f'🔗 交易链路较长 ({summary.service_count}个服务)，注意依赖管理')
        
        if not suggestions:
            suggestions.append('✅ 交易正常，未发现明显问题')
        
        return suggestions
    
    def _generate_user_message(self, summary: TransactionSummary,
                              transaction_info: Dict,
                              anomalies: List[Dict]) -> str:
        """生成用户友好的回复"""
        status_emoji = '✅' if summary.status == 'success' else '❌'
        
        message = f"""
{status_emoji} **交易查询结果**

📋 **基本信息**
- 交易类型：{summary.transaction_name} ({summary.transaction_type})
- TraceID: `{summary.trace_id}`
- 交易状态：{summary.status}

📊 **统计数据**
- 日志总数：{summary.total_logs} 条
- 涉及服务：{summary.service_count} 个
- 耗时：{summary.duration_ms}ms

⏰ **时间范围**
- 开始：{summary.start_time}
- 结束：{summary.end_time}
"""
        
        if transaction_info:
            message += "\n💳 **交易详情**\n"
            if transaction_info.get('amount'):
                message += f"- 金额：{transaction_info['amount']} 元\n"
            if transaction_info.get('merchant_id'):
                message += f"- 商户号：{transaction_info['merchant_id']}\n"
            if transaction_info.get('user_name'):
                message += f"- 用户：{transaction_info['user_name']}\n"
        
        if anomalies:
            message += f"\n⚠️ **发现 {len(anomalies)} 个异常**\n"
            for i, anomaly in enumerate(anomalies[:3], 1):
                message += f"{i}. [{anomaly['timestamp']}] {anomaly['service']}: {anomaly['type']}\n"
            if len(anomalies) > 3:
                message += f"... 还有 {len(anomalies) - 3} 个异常\n"
        
        return message.strip()


# ============================================
# 智多星主类
# ============================================

class ZhiduoxingIntegration:
    """智多星集成主类"""
    
    def __init__(self, config: Config = None):
        self.client = SFTLogClient(config)
        self.analyzer = ZhiduoxingAnalyzer(self.client)
    
    def query_and_analyze(self, transaction_type: str, req_sn: str, 
                         log_time: str) -> Dict:
        """
        查询并分析交易
        
        Args:
            transaction_type: 交易类型
            req_sn: 交易序列号
            log_time: 日志时间
        
        Returns:
            Dict: 分析结果
        """
        # 1. 查询日志
        result = self.client.query_transaction(
            transaction_type=transaction_type,
            req_sn=req_sn,
            log_time=log_time
        )
        
        # 2. 分析日志
        analysis = self.analyzer.analyze_transaction(result)
        
        return analysis
    
    def natural_language_query(self, user_input: str) -> Dict:
        """
        自然语言查询
        
        Args:
            user_input: 用户自然语言输入
        
        Returns:
            Dict: 分析结果
        """
        # 1. 解析自然语言
        params = self._parse_natural_language(user_input)
        
        if not params:
            return {
                'success': False,
                'error': '无法解析您的请求，请提供更详细的信息',
                'example': '例如："帮我看下 310011 交易，REQ_SN=LX260408090024C80C82F3，时间 2026040809"'
            }
        
        # 2. 查询并分析
        return self.query_and_analyze(
            transaction_type=params['transaction_type'],
            req_sn=params['req_sn'],
            log_time=params['log_time']
        )
    
    def _parse_natural_language(self, text: str) -> Optional[Dict]:
        """解析自然语言"""
        params = {}
        
        # 提取交易类型（5-6 位数字）
        match = re.search(r'\b(\d{5,6})\b', text)
        if match:
            params['transaction_type'] = match.group(1)
        
        # 提取 REQ_SN（字母数字组合，16-32 位）
        match = re.search(r'(?:REQ_SN[=：:\s]*|req_sn[=：:\s]*|交易号 [=：:\s]*)([A-Za-z0-9]{16,32})', text, re.IGNORECASE)
        if match:
            params['req_sn'] = match.group(1)
        else:
            match = re.search(r'\b([A-Z][A-Za-z0-9]{15,31})\b', text)
            if match:
                params['req_sn'] = match.group(1)
        
        # 提取时间（10 位数字）
        match = re.search(r'(?:时间 [=：:\s]*|time[=：:\s]*)(\d{10})\b', text, re.IGNORECASE)
        if match:
            params['log_time'] = match.group(1)
        else:
            match = re.search(r'\b(\d{10})\b', text)
            if match:
                params['log_time'] = match.group(1)
        
        # 验证必填参数
        if not all(k in params for k in ['transaction_type', 'req_sn', 'log_time']):
            return None
        
        return params
    
    def get_transaction_type_name(self, code: str) -> str:
        """获取交易类型名称"""
        types = self.client.get_transaction_types()
        return types.get(code, {}).get('name', code)
    
    def list_transaction_types(self) -> List[Dict]:
        """列出所有交易类型"""
        types = self.client.get_transaction_types()
        return [
            {'code': code, 'name': info.get('name', ''), 'apps': info.get('apps', [])}
            for code, info in types.items()
        ]


# ============================================
# 使用示例
# ============================================

if __name__ == '__main__':
    # 初始化
    zhiduoxing = ZhiduoxingIntegration()
    
    # 示例 1: 自然语言查询
    print("=" * 80)
    print("示例 1: 自然语言查询")
    print("=" * 80)
    
    user_input = "帮我看下 310011 交易的日志，REQ_SN=LX260408090024C80C82F3，时间 2026040809"
    print(f"用户输入：{user_input}\n")
    
    result = zhiduoxing.natural_language_query(user_input)
    
    if result.get('success'):
        print(result.get('user_message'))
    else:
        print(f"查询失败：{result.get('error')}")
    
    # 示例 2: 直接查询
    print("\n" + "=" * 80)
    print("示例 2: 直接查询")
    print("=" * 80)
    
    result = zhiduoxing.query_and_analyze(
        transaction_type="310011",
        req_sn="LX260408090024C80C82F3",
        log_time="2026040809"
    )
    
    if result.get('success'):
        print(f"交易类型：{result['summary']['transaction_name']}")
        print(f"TraceID: {result['summary']['trace_id']}")
        print(f"日志总数：{result['summary']['total_logs']}")
        print(f"交易状态：{result['summary']['status']}")
    else:
        print(f"查询失败：{result.get('error')}")
    
    # 示例 3: 获取交易类型列表
    print("\n" + "=" * 80)
    print("示例 3: 交易类型列表")
    print("=" * 80)
    
    types = zhiduoxing.list_transaction_types()
    for t in types[:5]:
        print(f"{t['code']}: {t['name']} - {t['apps']}")
