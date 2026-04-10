from flask import Flask, request, jsonify, send_from_directory, make_response
import os
import json
from datetime import datetime
from config import Config
from models.log_parser import read_log_blocks, find_logs_by_trace_id
from models.trace_analyzer import TraceAnalyzer
from models.indexer import IndexBuilder
from ai_api.auth import require_api_key, get_api_key_manager
from ai_api.query_handler import AIQueryHandler
from ai_api.response_formatter import format_ai_response, format_error_response

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 添加 CORS 支持
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # 初始化分析器和索引器
    analyzer = TraceAnalyzer(config_dir='/root/sft/sftlogapi/config', log_dir='/root/sft/testlogs')
    indexer = IndexBuilder(log_dir='/root/sft/testlogs')
    
    # 初始化 AI 查询处理器
    ai_handler = AIQueryHandler(analyzer, '/root/sft/testlogs')

    @app.route('/')
    def index():
        return send_from_directory('/root/sft/log-tracker/frontend/dist', 'index.html')

    @app.route('/api/search', methods=['GET'])
    def search_by_req_sn():
        """根据 REQ_SN 搜索日志"""
        req_sn = request.args.get('req_sn')
        service = request.args.get('service', 'sft-aipg')

        if not req_sn:
            return jsonify({'error': '缺少 REQ_SN 参数'}), 400

        try:
            from models.log_parser import find_logs_by_req_sn
            logs = find_logs_by_req_sn(service, req_sn, '/root/sft/testlogs')

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
            return jsonify({'error': f'搜索过程中发生错误：{str(e)}'}), 500

    @app.route('/api/trace', methods=['GET'])
    def trace_transaction():
        """追踪交易链路"""
        req_sn = request.args.get('req_sn')
        transaction_type = request.args.get('transaction_type')

        if not req_sn:
            return jsonify({'error': '缺少 REQ_SN 参数'}), 400

        try:
            result = analyzer.trace_transaction_chain(req_sn, transaction_type)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'追踪过程中发生错误：{str(e)}'}), 500


    @app.route('/api/trace-summary', methods=['GET'])
    def trace_transaction_summary():
        """获取交易链路摘要"""
        req_sn = request.args.get('req_sn')
        transaction_type = request.args.get('transaction_type')

        if not req_sn:
            return jsonify({'error': '缺少 REQ_SN 参数'}), 400

        try:
            result = analyzer.get_transaction_summary(req_sn, transaction_type)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'获取摘要过程中发生错误：{str(e)}'}), 500


    @app.route('/api/search-by-trace', methods=['GET'])
    def search_by_trace_id():
        """根据 TraceID 搜索日志"""
        trace_id = request.args.get('trace_id')
        service = request.args.get('service')

        if not trace_id:
            return jsonify({'error': '缺少 TraceID 参数'}), 400

        try:
            if service:
                logs = find_logs_by_trace_id(service, trace_id, '/root/sft/testlogs')
            else:
                logs = []
                log_dirs = analyzer.log_dirs
                for svc_name in log_dirs.keys():
                    svc_logs = find_logs_by_trace_id(svc_name, trace_id, '/root/sft/testlogs')
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
            return jsonify({'error': f'搜索过程中发生错误：{str(e)}'}), 500


    @app.route('/api/services', methods=['GET'])
    def get_available_services():
        """获取可用的服务列表"""
        try:
            log_dirs = analyzer.log_dirs
            services = list(log_dirs.keys())

            testlogs_path = '/root/sft/testlogs'
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
            return jsonify({'error': f'获取服务列表过程中发生错误：{str(e)}'}), 500


    @app.route('/api/transaction-types', methods=['GET'])
    def get_transaction_types():
        """获取支持的交易类型"""
        try:
            transaction_types = analyzer.transaction_types
            return jsonify({
                'success': True,
                'transaction_types': transaction_types
            })
        except Exception as e:
            return jsonify({'error': f'获取交易类型过程中发生错误：{str(e)}'}), 500

    @app.route('/search/full-text', methods=['POST'])
    def full_text_search():
        """全文搜索功能"""
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': '缺少搜索查询参数'}), 400

        query = data['query']
        service = data.get('service', 'all')
        case_sensitive = data.get('case_sensitive', False)
        max_results = data.get('max_results', 100)

        try:
            results = []

            if service == 'all':
                log_dir = '/root/sft/testlogs'
                services = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
            else:
                services = [service]

            for svc in services:
                svc_path = os.path.join(log_dir, svc)

                if not os.path.exists(svc_path):
                    continue

                for log_file in os.listdir(svc_path):
                    if not log_file.endswith('.log') and not log_file.endswith('.log.gz'):
                        continue

                    file_path = os.path.join(svc_path, log_file)

                    if case_sensitive:
                        pattern = query
                    else:
                        pattern = query.lower()

                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            search_line = line if case_sensitive else line.lower()

                            if pattern in search_line:
                                results.append({
                                    'service': svc,
                                    'file': log_file,
                                    'line_number': line_num,
                                    'content': line.strip(),
                                    'matched_position': search_line.find(pattern) if pattern else -1
                                })

                                if len(results) >= max_results:
                                    break

                        if len(results) >= max_results:
                            break

                if len(results) >= max_results:
                    break

            return jsonify({
                'success': True,
                'query': query,
                'results': results[:max_results],
                'total_count': len(results)
            })

        except Exception as e:
            return jsonify({'error': f'全文搜索过程中发生错误：{str(e)}'}), 500

    # ==================== 新增 API 路由 ====================
    
    @app.route('/api/transaction-trace', methods=['GET'])
    def transaction_trace():
        """
        交易类型日志追踪 - 根据交易类型配置的关联应用，依次展示每个应用的日志链路
        
        支持重复查询场景：同一个 REQ_SN 可能对应多个不同的 TraceID
        
        查询逻辑:
        1. 从交易类型配置中获取关联应用列表
        2. 从第一个应用（入口应用）根据 REQ_SN 和时间找到所有不同的 TraceID
        3. 对每个 TraceID，依次查询所有关联应用的日志
        4. 按 TraceID 分组返回结果
        
        注意：log_time 参数为必填，防止查询全量日志导致系统崩溃
        """
        transaction_type = request.args.get('transaction_type')
        req_sn = request.args.get('req_sn')
        log_time = request.args.get('log_time')

        try:
            if not transaction_type:
                return jsonify({
                    'success': False,
                    'message': '请选择交易类型'
                }), 400

            if not req_sn:
                return jsonify({
                    'success': False,
                    'message': '请输入 REQ_SN'
                }), 400

            # 强制要求输入日志时间，防止查询全量日志
            if not log_time:
                return jsonify({
                    'success': False,
                    'message': '请输入日志时间（必填），格式：YYYYMMDDHH（如：2026040809）'
                }), 400

            # 验证时间格式
            import re
            if not re.match(r'^\d{10}$', log_time):
                return jsonify({
                    'success': False,
                    'message': '日志时间格式不正确，应为 10 位数字（如：2026040809）'
                }), 400

            # 1. 获取交易类型配置中的应用列表
            type_info = analyzer.transaction_types.get(transaction_type)
            if not type_info:
                return jsonify({
                    'success': False,
                    'message': f'未找到交易类型 {transaction_type} 的配置'
                }), 404

            apps = type_info.get('apps', [])
            if not apps:
                return jsonify({
                    'success': False,
                    'message': f'交易类型 {transaction_type} 未配置关联应用'
                }), 400

            # 2. 从第一个应用找到所有不同的 TraceID
            first_app = apps[0]
            trace_id_map = {}  # {trace_id: [log1, log2, ...]}
            
            # 确定要查询的文件列表
            if log_time:
                log_files = find_log_files_by_time(first_app, log_time, '/root/sft/testlogs')
            else:
                service_dir = os.path.join('/root/sft/testlogs', first_app)
                if os.path.exists(service_dir):
                    log_files = [os.path.join(service_dir, f) for f in os.listdir(service_dir) if f.endswith('.log') or f.endswith('.log.gz')]
                    log_files.sort(reverse=True)
                else:
                    log_files = []

            # 在文件中查找所有包含 REQ_SN 的行，按 TraceID 分组
            for log_file in log_files:
                for log_block in read_log_blocks(log_file):
                    if req_sn in log_block.content:
                        trace_id = log_block.trace_id
                        if trace_id not in trace_id_map:
                            trace_id_map[trace_id] = []
                        trace_id_map[trace_id].append(log_block)
                    elif 'req_sn' in log_block.parsed_content and log_block.parsed_content['req_sn'] == req_sn:
                        trace_id = log_block.trace_id
                        if trace_id not in trace_id_map:
                            trace_id_map[trace_id] = []
                        trace_id_map[trace_id].append(log_block)

            if not trace_id_map:
                return jsonify({
                    'success': True,
                    'trace_groups': [],
                    'total_logs': 0,
                    'message': '未找到包含 REQ_SN 的日志记录'
                })

            # 3. 对每个 TraceID，查询所有关联应用的日志
            trace_groups = []
            total_logs = 0

            for trace_id, req_sn_logs in trace_id_map.items():
                app_logs = {}
                group_total = 0

                for app in apps:
                    trace_logs = find_logs_by_trace_id_with_time(app, trace_id, '/root/sft/testlogs', log_time)
                    
                    logs_for_app = []
                    for log in trace_logs:
                        log_entry = {
                            'timestamp': log.timestamp,
                            'service': log.service,
                            'level': log.level,
                            'traceId': log.trace_id,
                            'thread': log.thread,
                            'content': log.content,
                            'fullContent': log.content,
                            'isReqSnMatch': any(log.timestamp == req_log.timestamp for req_log in req_sn_logs)
                        }
                        logs_for_app.append(log_entry)
                    
                    app_logs[app] = logs_for_app
                    group_total += len(logs_for_app)

                # 获取第一次出现的时间用于排序
                first_timestamp = req_sn_logs[0].timestamp if req_sn_logs else ''

                trace_groups.append({
                    'trace_id': trace_id,
                    'req_sn_count': len(req_sn_logs),
                    'total_logs': group_total,
                    'first_timestamp': first_timestamp,
                    'app_logs': app_logs,
                    'apps': apps
                })

                total_logs += group_total

            # 按第一次出现的时间排序
            trace_groups.sort(key=lambda x: x['first_timestamp'])

            return jsonify({
                'success': True,
                'trace_groups': trace_groups,
                'total_logs': total_logs,
                'trace_count': len(trace_groups)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'追踪过程中发生错误：{str(e)}'
            }), 500

    @app.route('/api/log-query', methods=['GET'])
    def log_query():
        """
        综合日志查询 - 支持 REQ_SN、商户号、日志时间组合查询
        
        查询逻辑:
        1. 根据日志时间定位日志文件
        2. 找到所有包含 REQ_SN 的行，提取所有不同的 TraceID
        3. 对每个 TraceID 查询所有相关日志
        4. 分组展示每个 TraceID 的完整链路
        
        注意：log_time 参数为必填，防止查询全量日志导致系统崩溃
        """
        req_sn = request.args.get('req_sn')
        merchant_no = request.args.get('merchant_no')
        log_time = request.args.get('log_time')
        service = request.args.get('service')

        try:
            if not req_sn and not merchant_no:
                return jsonify({
                    'success': False,
                    'message': '请输入 REQ_SN 或商户号'
                }), 400

            # 强制要求输入日志时间，防止查询全量日志
            if not log_time:
                return jsonify({
                    'success': False,
                    'message': '请输入日志时间（必填），格式：YYYYMMDDHH（如：2026040809）'
                }), 400

            # 验证时间格式
            import re
            if not re.match(r'^\d{10}$', log_time):
                return jsonify({
                    'success': False,
                    'message': '日志时间格式不正确，应为 10 位数字（如：2026040809）'
                }), 400

            # 第一步：找到所有包含 REQ_SN 的日志行，提取所有不同的 TraceID
            trace_ids = []
            
            if req_sn:
                svc = service or 'sft-aipg'
                
                # 确定要查询的文件列表
                if log_time:
                    log_files = find_log_files_by_time(svc, log_time, '/root/sft/testlogs')
                    if not log_files:
                        return jsonify({
                            'success': False,
                            'message': f'未找到时间 {log_time} 的日志文件'
                        })
                else:
                    service_dir = os.path.join('/root/sft/testlogs', svc)
                    if os.path.exists(service_dir):
                        log_files = [os.path.join(service_dir, f) for f in os.listdir(service_dir) if f.endswith('.log') or f.endswith('.log.gz')]
                        log_files.sort(reverse=True)
                    else:
                        log_files = []
                
                # 在所有文件中查找包含 REQ_SN 的行
                trace_id_map = {}
                for log_file in log_files:
                    for log_block in read_log_blocks(log_file):
                        if req_sn in log_block.content:
                            trace_id = log_block.trace_id
                            if trace_id not in trace_id_map:
                                trace_id_map[trace_id] = []
                            trace_id_map[trace_id].append(log_block)
                        elif 'req_sn' in log_block.parsed_content and log_block.parsed_content['req_sn'] == req_sn:
                            trace_id = log_block.trace_id
                            if trace_id not in trace_id_map:
                                trace_id_map[trace_id] = []
                            trace_id_map[trace_id].append(log_block)
                
                for trace_id, logs in trace_id_map.items():
                    trace_ids.append({
                        'trace_id': trace_id,
                        'req_sn_logs': logs
                    })
            
            if not trace_ids:
                return jsonify({
                    'success': True,
                    'logs': [],
                    'trace_groups': [],
                    'message': '未找到包含 REQ_SN 的日志记录'
                })

            # 第二步：对每个 TraceID 查询所有相关日志
            svc = service or 'sft-aipg'
            all_logs = []
            trace_groups = []
            
            for trace_info in trace_ids:
                trace_id = trace_info['trace_id']
                req_sn_logs = trace_info['req_sn_logs']
                
                trace_logs = find_logs_by_trace_id_with_time(svc, trace_id, '/root/sft/testlogs', log_time)
                
                logs_for_this_trace = []
                for log in trace_logs:
                    log_entry = {
                        'timestamp': log.timestamp,
                        'service': log.service,
                        'level': log.level,
                        'traceId': log.trace_id,
                        'thread': log.thread,
                        'content': log.content,
                        'fullContent': log.content,
                        'traceGroup': trace_id,
                        'isReqSnMatch': any(log.timestamp == req_log.timestamp for req_log in req_sn_logs)
                    }
                    
                    if log_entry['isReqSnMatch']:
                        log_entry['merchantNo'] = extract_merchant(log.parsed_content)
                    
                    logs_for_this_trace.append(log_entry)
                    all_logs.append(log_entry)
                
                trace_groups.append({
                    'trace_id': trace_id,
                    'log_count': len(logs_for_this_trace),
                    'req_sn_count': len(req_sn_logs),
                    'first_timestamp': req_sn_logs[0].timestamp if req_sn_logs else '',
                    'logs': logs_for_this_trace
                })

            trace_groups.sort(key=lambda x: x['first_timestamp'])
            
            if merchant_no and all_logs:
                matched_logs = [log for log in all_logs if merchant_no in log.get('merchantNo', '') or merchant_no in log.get('content', '')]
                if matched_logs:
                    all_logs = matched_logs
                    for group in trace_groups:
                        group['logs'] = [log for log in matched_logs if log['traceId'] == group['trace_id']]
                        group['log_count'] = len(group['logs'])

            return jsonify({
                'success': True,
                'logs': all_logs,
                'trace_groups': trace_groups,
                'total': len(all_logs),
                'trace_count': len(trace_groups)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'查询过程中发生错误：{str(e)}'
            }), 500

    @app.route('/api/config/transaction-types', methods=['POST'])
    def update_transaction_types():
        """更新交易类型配置"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '缺少配置数据'
                }), 400

            config_path = '/root/sft/log-tracker/config/transaction_types.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            analyzer.load_transaction_types()

            return jsonify({
                'success': True,
                'message': '交易类型配置已更新'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'保存配置失败：{str(e)}'
            }), 500

    @app.route('/api/config/log-dirs', methods=['GET', 'POST'])
    def log_dirs_config():
        """获取或更新日志目录配置"""
        if request.method == 'GET':
            try:
                return jsonify({
                    'success': True,
                    'log_dirs': analyzer.log_dirs
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'获取配置失败：{str(e)}'
                }), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'message': '缺少配置数据'
                    }), 400

                config_path = '/root/sft/log-tracker/config/log_dirs.json'
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                analyzer.load_log_dirs()

                return jsonify({
                    'success': True,
                    'message': '日志目录配置已更新'
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'保存配置失败：{str(e)}'
                }), 500

    @app.route('/api/config/validate-path', methods=['POST'])
    def validate_path():
        """验证路径是否存在"""
        try:
            data = request.get_json()
            path = data.get('path')

            if not path:
                return jsonify({
                    'success': False,
                    'message': '缺少路径参数'
                }), 400

            exists = os.path.exists(path)
            is_dir = os.path.isdir(path) if exists else False
            readable = os.access(path, os.R_OK) if exists else False

            return jsonify({
                'success': exists and is_dir and readable,
                'exists': exists,
                'is_dir': is_dir,
                'readable': readable,
                'detail': f'目录包含 {len(os.listdir(path))} 个文件' if exists and is_dir else ''
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'验证失败：{str(e)}'
            }), 500

    # ============================================
    # AI API 路由
    # ============================================
    
    @app.route('/api/ai/query', methods=['POST'])
    @require_api_key
    def ai_query():
        """AI 统一查询接口"""
        import time
        start_time = time.time()
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify(format_error_response('请求体必须为 JSON 格式', 'INVALID_JSON')), 400
            
            query_type = data.get('query_type')
            params = data.get('params', {})
            
            if not query_type:
                return jsonify(format_error_response('缺少 query_type 参数', 'MISSING_QUERY_TYPE')), 400
            
            result = ai_handler.handle_query(query_type, params)
            result['query_time_ms'] = int((time.time() - start_time) * 1000)
            
            api_key_info = {
                'remaining': getattr(request, 'api_key_remaining', 0),
                'limit': getattr(request, 'api_key_info', {}).get('rate_limit', 0),
                'period': getattr(request, 'api_key_info', {}).get('rate_limit_period', 'minute')
            }
            
            return jsonify(format_ai_response(result, api_key_info))
        
        except Exception as e:
            return jsonify(format_error_response(f'查询错误：{str(e)}', 'INTERNAL_ERROR')), 500
    
    @app.route('/api/ai/health', methods=['GET'])
    def ai_health():
        """AI API 健康检查"""
        return jsonify({'success': True, 'status': 'healthy', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'api_version': 'v1'})
    
    @app.route('/api/ai/transaction-types', methods=['GET'])
    @require_api_key
    def ai_get_transaction_types():
        """获取交易类型列表"""
        try:
            return jsonify({'success': True, 'data': analyzer.transaction_types, 'count': len(analyzer.transaction_types), 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        except Exception as e:
            return jsonify(format_error_response(f'获取失败：{str(e)}', 'INTERNAL_ERROR')), 500
    
    @app.route('/api/ai/services', methods=['GET'])
    @require_api_key
    def ai_get_services():
        """获取服务列表"""
        try:
            services = sorted(list(analyzer.log_dirs.keys()))
            return jsonify({'success': True, 'data': services, 'count': len(services), 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        except Exception as e:
            return jsonify(format_error_response(f'获取失败：{str(e)}', 'INTERNAL_ERROR')), 500

    return app

def extract_merchant(parsed_content):
    """从解析内容中提取商户号"""
    if not parsed_content:
        return ''
    if isinstance(parsed_content, dict):
        return parsed_content.get('merchantNo', parsed_content.get('merchant_no', ''))
    return ''


def find_log_files_by_time(service_name, log_time, log_dir):
    """根据时间格式 (YYYYMMDDHH) 查找对应的日志文件
    
    支持:
    - 普通日志文件：xxx_2026040809.log
    - Gzip 压缩文件：xxx_2026040809.log.gz
    """
    import re
    
    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return []
    
    matching_files = []
    for filename in os.listdir(service_dir):
        # 匹配 .log 或 .log.gz 文件
        if filename.endswith('.log') or filename.endswith('.log.gz'):
            match = re.search(r'(\d{10})\.log(\.gz)?$', filename)
            if match and match.group(1) == log_time:
                matching_files.append(os.path.join(service_dir, filename))
    
    return matching_files


def find_req_sn_and_trace_id(log_file, req_sn):
    """在单个日志文件中查找包含 REQ_SN 的行，提取 TraceID"""
    for log_block in read_log_blocks(log_file):
        if req_sn in log_block.content:
            return {
                'trace_id': log_block.trace_id,
                'log': log_block
            }
        if 'req_sn' in log_block.parsed_content and log_block.parsed_content['req_sn'] == req_sn:
            return {
                'trace_id': log_block.trace_id,
                'log': log_block
            }
    
    return None


def find_req_sn_in_all_files(service_name, req_sn, log_dir):
    """在指定服务的所有日志文件中查找包含 REQ_SN 的行"""
    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return None
    
    log_files = sorted(
        [f for f in os.listdir(service_dir) if f.endswith('.log') or f.endswith('.log.gz')],
        reverse=True
    )
    
    for filename in log_files:
        file_path = os.path.join(service_dir, filename)
        result = find_req_sn_and_trace_id(file_path, req_sn)
        if result:
            return result
    
    return None


def find_logs_by_trace_id_with_time(service_name, trace_id, log_dir, log_time=None):
    """根据 TraceID 查找日志，支持按时间过滤
    
    支持:
    - 普通日志文件 (.log)
    - Gzip 压缩文件 (.log.gz)
    """
    from models.log_parser import read_log_blocks
    
    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return []
    
    result = []
    
    if log_time:
        log_files = find_log_files_by_time(service_name, log_time, log_dir)
        if log_files:
            try:
                base_hour = int(log_time[-2:])
                base_date = log_time[:-2]
                
                prev_hour = str(base_hour - 1).zfill(2)
                if base_hour > 0:
                    prev_time = base_date + prev_hour
                    result_files = find_log_files_by_time(service_name, prev_time, log_dir)
                    log_files.extend(result_files)
                
                next_hour = str(base_hour + 1).zfill(2)
                if base_hour < 23:
                    next_time = base_date + next_hour
                    result_files = find_log_files_by_time(service_name, next_time, log_dir)
                    log_files.extend(result_files)
            except:
                pass
    else:
        # 支持 .log 和 .log.gz 文件
        log_files = [os.path.join(service_dir, f) for f in os.listdir(service_dir) 
                     if f.endswith('.log') or f.endswith('.log.gz')]
    
    for file_path in log_files:
        for log_block in read_log_blocks(file_path):
            if log_block.trace_id == trace_id:
                result.append(log_block)
    
    return result

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
