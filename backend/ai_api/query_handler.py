"""
AI 查询处理器
"""

import os
import json
from datetime import datetime
from models.log_parser import read_log_blocks

def find_log_files_by_time(service_name, log_time, log_dir):
    """根据时间查找日志文件（支持复杂文件名）"""
    import os
    import re
    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return []
    
    matching_files = []
    for filename in os.listdir(service_dir):
        # 匹配 .log 或 .log.gz 文件，从文件名末尾提取 10 位时间
        if filename.endswith('.log') or filename.endswith('.log.gz'):
            match = re.search(r'(\d{10})\.log(\.gz)?$', filename)
            if match and match.group(1) == log_time:
                matching_files.append(os.path.join(service_dir, filename))
    
    return matching_files


class AIQueryHandler:
    """AI 查询处理器"""
    
    def __init__(self, analyzer, log_dir):
        self.analyzer = analyzer
        self.log_dir = log_dir
    
    def handle_query(self, query_type, params):
        """
        处理 AI 查询请求
        
        Args:
            query_type: 查询类型 (transaction_trace, single_service, trace_id_search)
            params: 查询参数
        
        Returns:
            dict: 查询结果
        """
        if query_type == 'transaction_trace':
            return self.handle_transaction_trace(params)
        elif query_type == 'single_service':
            return self.handle_single_service(params)
        elif query_type == 'trace_id_search':
            return self.handle_trace_id_search(params)
        else:
            return {
                'success': False,
                'error': f'不支持的查询类型：{query_type}',
                'code': 'UNSUPPORTED_QUERY_TYPE'
            }
    
    def handle_transaction_trace(self, params):
        """
        处理交易类型追踪查询
        
        Args:
            params: {
                "transaction_type": "310011",
                "trace_id": "TCEsVt60",  # 或 req_sn
                "req_sn": "LX260408090024C80C82F3",  # 可选，用于提取 TraceID
                "log_time": "2026040809",
                "service": "sft-aipg"  # 可选
            }
        """
        transaction_type = params.get('transaction_type')
        trace_id = params.get('trace_id')
        req_sn = params.get('req_sn')
        log_time = params.get('log_time')
        service = params.get('service')
        
        # 如果没有 trace_id 但有 req_sn，先从入口应用提取 TraceID
        if not trace_id and req_sn:
            trace_id = self._extract_trace_id_from_req_sn(req_sn, log_time)
            if not trace_id:
                return {
                    'success': False,
                    'error': f'无法从 REQ_SN {req_sn} 提取 TraceID',
                    'code': 'TRACE_ID_NOT_FOUND'
                }
        
        # 参数验证
        if not transaction_type:
            return {
                'success': False,
                'error': '缺少交易类型参数',
                'code': 'MISSING_TRANSACTION_TYPE'
            }
        
        if not trace_id:
            return {
                'success': False,
                'error': '缺少 TraceID 或 REQ_SN 参数',
                'code': 'MISSING_TRACE_ID'
            }
        
        if not log_time:
            return {
                'success': False,
                'error': '缺少日志时间参数（必填）',
                'code': 'MISSING_LOG_TIME'
            }
        
        # 获取交易类型配置
        type_info = self.analyzer.transaction_types.get(transaction_type)
        if not type_info:
            return {
                'success': False,
                'error': f'交易类型 {transaction_type} 不存在',
                'code': 'INVALID_TRANSACTION_TYPE'
            }
        
        # 获取关联应用列表
        apps = type_info.get('apps', [])
        if not apps:
            return {
                'success': False,
                'error': f'交易类型 {transaction_type} 未配置关联应用',
                'code': 'NO_APPS_CONFIGURED'
            }
        
        # 如果指定了 service，只查询该服务
        if service:
            apps = [service]
        
        # 执行追踪查询
        all_logs = []
        service_results = {}
        
        for app in apps:
            logs = self._query_service_logs(app, trace_id, log_time)
            if logs:
                service_results[app] = logs
                all_logs.extend(logs)
        
        # 按时间排序
        all_logs.sort(key=lambda x: x.get('timestamp', ''))
        
        # 格式化响应
        return self._format_transaction_trace_response(
            transaction_type, type_info, trace_id, all_logs, service_results
        )
    
    def handle_single_service(self, params):
        """
        处理单应用查询
        
        Args:
            params: {
                "service": "sft-aipg",
                "trace_id": "LX260408090024C80C82F3",
                "log_time": "2026040809"
            }
        """
        service = params.get('service')
        trace_id = params.get('trace_id') or params.get('req_sn')
        log_time = params.get('log_time')
        
        if not service:
            return {
                'success': False,
                'error': '缺少服务名称参数',
                'code': 'MISSING_SERVICE'
            }
        
        if not trace_id:
            return {
                'success': False,
                'error': '缺少 TraceID 或 REQ_SN 参数',
                'code': 'MISSING_TRACE_ID'
            }
        
        if not log_time:
            return {
                'success': False,
                'error': '缺少日志时间参数',
                'code': 'MISSING_LOG_TIME'
            }
        
        logs = self._query_service_logs(service, trace_id, log_time)
        
        return {
            'success': True,
            'query_type': 'single_service',
            'data': {
                'service': service,
                'trace_id': trace_id,
                'total_logs': len(logs),
                'logs': self._format_logs(logs),
                'summary': self._generate_summary(logs)
            }
        }
    
    def handle_trace_id_search(self, params):
        """
        处理 TraceID 搜索
        
        Args:
            params: {
                "trace_id": "LX260408090024C80C82F3",
                "log_time": "2026040809",
                "services": ["sft-aipg", "sft-trxqry"]  # 可选
            }
        """
        trace_id = params.get('trace_id')
        log_time = params.get('log_time')
        services = params.get('services')
        
        if not trace_id:
            return {
                'success': False,
                'error': '缺少 TraceID 参数',
                'code': 'MISSING_TRACE_ID'
            }
        
        if not log_time:
            return {
                'success': False,
                'error': '缺少日志时间参数',
                'code': 'MISSING_LOG_TIME'
            }
        
        # 如果指定了 services，只查询这些服务
        if services:
            app_list = services
        else:
            # 否则查询所有配置的服务
            app_list = list(self.analyzer.log_dirs.keys())
        
        all_logs = []
        service_results = {}
        
        for app in app_list:
            logs = self._query_service_logs(app, trace_id, log_time)
            if logs:
                service_results[app] = logs
                all_logs.extend(logs)
        
        # 按时间排序
        all_logs.sort(key=lambda x: x.get('timestamp', ''))
        
        return {
            'success': True,
            'query_type': 'trace_id_search',
            'data': {
                'trace_id': trace_id,
                'total_logs': len(all_logs),
                'services': list(service_results.keys()),
                'service_results': service_results,
                'logs': self._format_logs(all_logs),
                'summary': self._generate_summary(all_logs)
            }
        }
    
    def _query_service_logs(self, service, trace_id, log_time):
        """查询单个服务的日志"""
        try:
            # 获取服务的日志目录
            log_dirs = self.analyzer.log_dirs
            service_dir = log_dirs.get(service)
            
            if not service_dir:
                # 尝试从 log_dir 构建路径
                service_dir = os.path.join(self.log_dir, service)
            
            if not os.path.exists(service_dir):
                return []
            
            # 根据时间定位日志文件
            log_files = find_log_files_by_time(service, log_time, self.log_dir)
            
            if not log_files:
                return []
            
            # 查询包含 TraceID 的日志
            logs = []
            for log_file in log_files:
                for log_block in read_log_blocks(log_file):
                    if log_block.trace_id == trace_id:
                        logs.append({
                            'service': service,
                            'timestamp': log_block.timestamp,
                            'thread': log_block.thread,
                            'trace_id': log_block.trace_id,
                            'level': log_block.level,
                            'env': log_block.env,
                            'company': log_block.company,
                            'content': log_block.content,
                            'parsed_content': log_block.parsed_content
                        })
            
            return logs
        
        except Exception as e:
            print(f"查询服务 {service} 日志失败：{e}")
            return []
    
    def _format_logs(self, logs):
        """格式化日志列表"""
        formatted = []
        for log in logs:
            formatted.append({
                'timestamp': log.get('timestamp'),
                'thread': log.get('thread'),
                'level': log.get('level'),
                'service': log.get('service'),
                'content': log.get('content'),
                'parsed': log.get('parsed_content', {})
            })
        return formatted
    
    def _format_transaction_trace_response(self, transaction_type, type_info, trace_id, all_logs, service_results):
        """格式化交易追踪响应"""
        return {
            'success': True,
            'query_type': 'transaction_trace',
            'data': {
                'transaction_type': transaction_type,
                'transaction_name': type_info.get('name'),
                'transaction_code': transaction_type,
                'trace_id': trace_id,
                'total_logs': len(all_logs),
                'services': list(service_results.keys()),
                'service_count': len(service_results),
                'logs': self._format_logs(all_logs),
                'service_results': {
                    service: self._format_logs(logs)
                    for service, logs in service_results.items()
                },
                'summary': self._generate_summary(all_logs)
            }
        }
    
    def _generate_summary(self, logs):
        """生成日志摘要"""
        if not logs:
            return {
                'status': 'no_logs',
                'message': '未找到相关日志'
            }
        
        # 按时间排序
        sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
        
        first_log = sorted_logs[0]
        last_log = sorted_logs[-1]
        
        # 推断交易状态
        status = self._infer_status(logs)
        
        return {
            'start_time': first_log.get('timestamp'),
            'end_time': last_log.get('timestamp'),
            'service_count': len(set(log.get('service') for log in logs)),
            'log_count': len(logs),
            'status': status,
            'has_error': status == 'failed'
        }
    
    def _infer_status(self, logs):
        """推断交易状态"""
        error_keywords = ['error', 'fail', 'exception', 'failed', 'failure']
        
        for log in logs:
            content = log.get('content', '').lower()
            level = log.get('level', '').upper()
            
            # 检查日志级别
            if level in ['ERROR', 'FATAL', 'CRITICAL']:
                return 'failed'
            
            # 检查内容关键字
            if any(keyword in content for keyword in error_keywords):
                return 'failed'
        
        return 'success'
    
    def _extract_trace_id_from_req_sn(self, req_sn, log_time):
        """从 REQ_SN 提取 TraceID（在入口应用中查找）"""
        try:
            # 在入口应用（sft-aipg）中查找包含 REQ_SN 的日志
            service = 'sft-aipg'
            log_files = find_log_files_by_time(service, log_time, self.log_dir)
            
            for log_file in log_files:
                for log_block in read_log_blocks(log_file):
                    # 检查内容或 parsed_content 中是否包含 REQ_SN
                    if req_sn in log_block.content:
                        return log_block.trace_id
                    if isinstance(log_block.parsed_content, dict):
                        if log_block.parsed_content.get('req_sn') == req_sn:
                            return log_block.trace_id
            
            return None
        except Exception as e:
            print(f"提取 TraceID 失败：{e}")
            return None
