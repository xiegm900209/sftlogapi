from flask import Blueprint, request, jsonify
from models.log_parser import read_log_blocks
from models.indexer import IndexBuilder
import os
import glob

bp = Blueprint('search', __name__)
indexer = IndexBuilder()


@bp.route('/full-text', methods=['POST'])
def full_text_search():
    """全文搜索功能"""
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': '缺少搜索查询参数'}), 400

    query = data['query']
    service = data.get('service', 'all')  # 搜索特定服务或所有服务
    case_sensitive = data.get('case_sensitive', False)
    max_results = data.get('max_results', 100)

    try:
        results = []

        if service == 'all':
            # 搜索所有服务
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')
            services = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
        else:
            services = [service]

        for svc in services:
            svc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs', svc)

            if not os.path.exists(svc_path):
                continue

            for log_file in os.listdir(svc_path):
                if not log_file.endswith('.log'):
                    continue

                file_path = os.path.join(svc_path, log_file)

                # 根据是否区分大小写进行搜索
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
                                'matched_position': search_line.find(pattern)
                            })

                            # 限制结果数量
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
        return jsonify({'error': f'全文搜索过程中发生错误: {str(e)}'}), 500


@bp.route('/by-time-range', methods=['POST'])
def search_by_time_range():
    """按时间范围搜索日志"""
    data = request.get_json()

    if not data or 'start_time' not in data or 'end_time' not in data:
        return jsonify({'error': '缺少时间范围参数'}), 400

    start_time = data['start_time']
    end_time = data['end_time']
    service = data.get('service', 'all')

    try:
        import re
        from datetime import datetime

        results = []

        if service == 'all':
            # 搜索所有服务
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')
            services = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
        else:
            services = [service]

        # 将时间字符串转换为datetime对象以便比较
        start_dt = datetime.strptime(start_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_time.split('.')[0], '%Y-%m-%d %H:%M:%S')

        for svc in services:
            svc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs', svc)

            if not os.path.exists(svc_path):
                continue

            for log_file in os.listdir(svc_path):
                if not log_file.endswith('.log'):
                    continue

                file_path = os.path.join(svc_path, log_file)

                # 使用日志解析器读取日志块
                for log_block in read_log_blocks(file_path):
                    # 解析日志块的时间戳
                    try:
                        log_dt = datetime.strptime(log_block.timestamp.split('.')[0], '%Y-%m-%d %H:%M:%S')

                        if start_dt <= log_dt <= end_dt:
                            results.append({
                                'service': svc,
                                'file': log_file,
                                'timestamp': log_block.timestamp,
                                'thread': log_block.thread,
                                'trace_id': log_block.trace_id,
                                'level': log_block.level,
                                'content': log_block.content,
                                'parsed_content': log_block.parsed_content
                            })
                    except ValueError:
                        # 如果时间戳格式不匹配，跳过该日志块
                        continue

        return jsonify({
            'success': True,
            'start_time': start_time,
            'end_time': end_time,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({'error': f'时间范围搜索过程中发生错误: {str(e)}'}), 500


@bp.route('/by-level', methods=['GET'])
def search_by_log_level():
    """按日志级别搜索"""
    level = request.args.get('level')
    service = request.args.get('service', 'all')
    hours_back = request.args.get('hours_back', 1, type=int)  # 默认查询最近1小时

    if not level:
        return jsonify({'error': '缺少日志级别参数'}), 400

    try:
        import re
        from datetime import datetime, timedelta

        results = []

        if service == 'all':
            # 搜索所有服务
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')
            services = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
        else:
            services = [service]

        # 计算查询时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)

        for svc in services:
            svc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs', svc)

            if not os.path.exists(svc_path):
                continue

            for log_file in os.listdir(svc_path):
                if not log_file.endswith('.log'):
                    continue

                # 检查文件修改时间是否在查询范围内
                file_path = os.path.join(svc_path, log_file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                # 粗略过滤，如果文件修改时间早于查询开始时间，可能不包含所需数据
                if file_mtime < start_time - timedelta(days=1):  # 添加一天的缓冲
                    continue

                # 使用日志解析器读取日志块
                for log_block in read_log_blocks(file_path):
                    # 检查日志级别是否匹配（不区分大小写）
                    if log_block.level.upper() == level.upper():
                        # 解析日志块的时间戳
                        try:
                            log_dt = datetime.strptime(log_block.timestamp.split('.')[0], '%Y-%m-%d %H:%M:%S')

                            if start_time <= log_dt <= end_time:
                                results.append({
                                    'service': svc,
                                    'file': log_file,
                                    'timestamp': log_block.timestamp,
                                    'thread': log_block.thread,
                                    'trace_id': log_block.trace_id,
                                    'level': log_block.level,
                                    'content': log_block.content,
                                    'parsed_content': log_block.parsed_content
                                })
                        except ValueError:
                            # 如果时间戳格式不匹配，仍然包含该日志（因为级别已匹配）
                            results.append({
                                'service': svc,
                                'file': log_file,
                                'timestamp': log_block.timestamp,
                                'thread': log_block.thread,
                                'trace_id': log_block.trace_id,
                                'level': log_block.level,
                                'content': log_block.content,
                                'parsed_content': log_block.parsed_content
                            })

        return jsonify({
            'success': True,
            'level': level,
            'hours_back': hours_back,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({'error': f'按日志级别搜索过程中发生错误: {str(e)}'}), 500


@bp.route('/log-files', methods=['GET'])
def get_log_files():
    """获取可用的日志文件列表"""
    service = request.args.get('service', 'all')

    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')

        if service == 'all':
            services = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
        else:
            services = [service] if os.path.isdir(os.path.join(log_dir, service)) else []

        file_info = {}

        for svc in services:
            svc_path = os.path.join(log_dir, svc)
            if not os.path.exists(svc_path):
                continue

            files = []
            for log_file in os.listdir(svc_path):
                if log_file.endswith('.log'):
                    file_path = os.path.join(svc_path, log_file)
                    stat = os.stat(file_path)

                    files.append({
                        'name': log_file,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'path': file_path
                    })

            file_info[svc] = sorted(files, key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'services': file_info
        })

    except Exception as e:
        return jsonify({'error': f'获取日志文件列表过程中发生错误: {str(e)}'}), 500