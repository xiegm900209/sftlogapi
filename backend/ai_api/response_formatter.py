"""
AI 响应格式化模块
"""

from datetime import datetime


def format_ai_response(result, api_key_info=None):
    """
    格式化 AI 响应
    
    Args:
        result: 查询结果
        api_key_info: API Key 信息（可选）
    
    Returns:
        dict: 格式化的响应
    """
    response = {
        'success': result.get('success', False),
        'query_type': result.get('query_type'),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'api_version': 'v1'
    }
    
    if result.get('success'):
        response['data'] = result.get('data', {})
        
        # 添加元数据
        response['metadata'] = {
            'query_time_ms': result.get('query_time_ms', 0),
            'total_logs': result.get('data', {}).get('total_logs', 0),
            'api_version': 'v1'
        }
        
        # 如果有 API Key 信息，添加速率限制信息
        if api_key_info:
            response['metadata']['rate_limit'] = {
                'remaining': api_key_info.get('remaining', 0),
                'limit': api_key_info.get('limit'),
                'period': api_key_info.get('period')
            }
    
    else:
        response['error'] = result.get('error', '未知错误')
        response['code'] = result.get('code', 'UNKNOWN_ERROR')
        response['message'] = result.get('message', '')
    
    return response


def format_error_response(error, code, message='', http_status=500):
    """
    格式化错误响应
    
    Args:
        error: 错误描述
        code: 错误代码
        message: 详细消息
        http_status: HTTP 状态码
    
    Returns:
        dict: 错误响应
    """
    return {
        'success': False,
        'error': error,
        'code': code,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'api_version': 'v1'
    }


def format_logs_for_ai(logs, max_logs=100):
    """
    为 AI 格式化日志（精简版）
    
    Args:
        logs: 日志列表
        max_logs: 最大返回数量
    
    Returns:
        list: 格式化的日志
    """
    formatted = []
    
    # 按时间排序
    sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''))
    
    # 限制返回数量
    if len(sorted_logs) > max_logs:
        sorted_logs = sorted_logs[:max_logs]
    
    for log in sorted_logs:
        formatted.append({
            'timestamp': log.get('timestamp'),
            'service': log.get('service'),
            'level': log.get('level'),
            'thread': log.get('thread'),
            'content': log.get('content'),
            'key_fields': extract_key_fields(log.get('parsed_content', {}))
        })
    
    return formatted


def extract_key_fields(parsed_content):
    """
    从解析内容中提取关键字段
    
    Args:
        parsed_content: 解析后的内容
    
    Returns:
        dict: 关键字段
    """
    key_fields = {}
    
    if not parsed_content:
        return key_fields
    
    # 常见的关键字段
    important_keys = [
        'req_sn', 'merchant_no', 'trace_id', 'trans_type',
        'status', 'code', 'message', 'amount', 'currency'
    ]
    
    for key in important_keys:
        if key in parsed_content:
            key_fields[key] = parsed_content[key]
    
    return key_fields


def generate_natural_language_summary(data):
    """
    生成自然语言摘要（给 AI 用）
    
    Args:
        data: 查询数据
    
    Returns:
        str: 自然语言摘要
    """
    if not data:
        return "未找到相关数据"
    
    summary_parts = []
    
    # 交易类型信息
    if data.get('transaction_name'):
        summary_parts.append(f"交易类型：{data.get('transaction_name')}({data.get('transaction_type')})")
    
    # TraceID
    if data.get('trace_id'):
        summary_parts.append(f"TraceID: {data.get('trace_id')}")
    
    # 日志统计
    total_logs = data.get('total_logs', 0)
    service_count = data.get('service_count', 0)
    summary_parts.append(f"共找到 {total_logs} 条日志，涉及 {service_count} 个服务")
    
    # 时间范围
    log_summary = data.get('summary', {})
    if log_summary.get('start_time') and log_summary.get('end_time'):
        summary_parts.append(f"时间范围：{log_summary.get('start_time')} 至 {log_summary.get('end_time')}")
    
    # 交易状态
    status = log_summary.get('status', 'unknown')
    if status == 'success':
        summary_parts.append("交易状态：✅ 成功")
    elif status == 'failed':
        summary_parts.append("交易状态：❌ 失败")
    else:
        summary_parts.append(f"交易状态：{status}")
    
    return " | ".join(summary_parts)
