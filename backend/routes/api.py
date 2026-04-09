from flask import Blueprint, request, jsonify
from models.log_parser import find_logs_by_req_sn, find_logs_by_trace_id
from models.trace_analyzer import TraceAnalyzer
from models.indexer import IndexBuilder
import os

bp = Blueprint('api', __name__)

# 初始化分析器
analyzer = TraceAnalyzer()
indexer = IndexBuilder()


@bp.route('/search', methods=['GET'])
def search_by_req_sn():
    """根据REQ_SN搜索日志"""
    req_sn = request.args.get('req_sn')
    service = request.args.get('service', 'sft-aipg')  # 默认查询sft-aipg服务

    if not req_sn:
        return jsonify({'error': '缺少REQ_SN参数'}), 400

    try:
        logs = find_logs_by_req_sn(service, req_sn)

        result = []
        for log in logs:
            result.append({
                'timestamp': log.timestamp,
                'thread': log.thread,
                'trace_id': log.trace_id,
                'level': log.level,
                'env': log.env,
                'company': log.company,
                'service': log.service,
                'content': log.content,
                'parsed_content': log.parsed_content
            })

        return jsonify({
            'success': True,
            'req_sn': req_sn,
            'service': service,
            'logs': result
        })
    except Exception as e:
        return jsonify({'error': f'搜索过程中发生错误: {str(e)}'}), 500


@bp.route('/trace', methods=['GET'])
def trace_transaction():
    """追踪交易链路"""
    req_sn = request.args.get('req_sn')
    transaction_type = request.args.get('transaction_type')

    if not req_sn:
        return jsonify({'error': '缺少REQ_SN参数'}), 400

    try:
        result = analyzer.trace_transaction_chain(req_sn, transaction_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'追踪过程中发生错误: {str(e)}'}), 500


@bp.route('/trace-summary', methods=['GET'])
def trace_transaction_summary():
    """获取交易链路摘要"""
    req_sn = request.args.get('req_sn')
    transaction_type = request.args.get('transaction_type')

    if not req_sn:
        return jsonify({'error': '缺少REQ_SN参数'}), 400

    try:
        result = analyzer.get_transaction_summary(req_sn, transaction_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'获取摘要过程中发生错误: {str(e)}'}), 500


@bp.route('/search-by-trace', methods=['GET'])
def search_by_trace_id():
    """根据TraceID搜索日志"""
    trace_id = request.args.get('trace_id')
    service = request.args.get('service')  # 如果未指定服务，则搜索所有服务

    if not trace_id:
        return jsonify({'error': '缺少TraceID参数'}), 400

    try:
        if service:
            # 查询特定服务
            logs = find_logs_by_trace_id(service, trace_id)
        else:
            # 搜索所有服务
            logs = []
            log_dirs = analyzer.log_dirs
            for svc_name in log_dirs.keys():
                svc_logs = find_logs_by_trace_id(svc_name, trace_id)
                logs.extend(svc_logs)

        result = []
        for log in logs:
            result.append({
                'timestamp': log.timestamp,
                'thread': log.thread,
                'trace_id': log.trace_id,
                'level': log.level,
                'env': log.env,
                'company': log.company,
                'service': log.service,
                'content': log.content,
                'parsed_content': log.parsed_content
            })

        return jsonify({
            'success': True,
            'trace_id': trace_id,
            'service': service or 'all',
            'logs': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({'error': f'搜索过程中发生错误: {str(e)}'}), 500


@bp.route('/services', methods=['GET'])
def get_available_services():
    """获取可用的服务列表"""
    try:
        log_dirs = analyzer.log_dirs
        services = list(log_dirs.keys())

        # 额外检查testlogs目录下的服务
        import glob
        testlogs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')
        if os.path.exists(testlogs_path):
            for item in os.listdir(testlogs_path):
                item_path = os.path.join(testlogs_path, item)
                if os.path.isdir(item_path) and item not in services:
                    services.append(item)

        return jsonify({
            'success': True,
            'services': services
        })
    except Exception as e:
        return jsonify({'error': f'获取服务列表过程中发生错误: {str(e)}'}), 500


@bp.route('/transaction-types', methods=['GET'])
def get_transaction_types():
    """获取支持的交易类型"""
    try:
        transaction_types = analyzer.transaction_types
        return jsonify({
            'success': True,
            'transaction_types': transaction_types
        })
    except Exception as e:
        return jsonify({'error': f'获取交易类型过程中发生错误: {str(e)}'}), 500