import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
from models.log_parser import read_log_blocks


class IndexBuilder:
    """日志索引构建器"""

    def __init__(self, log_dir: str = '/root/sft/testlogs', index_dir: str = '/root/sft/log-tracker/logs_index'):
        self.log_dir = log_dir
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

    def build_service_index(self, service_name: str) -> Dict[str, List[Dict]]:
        """
        为指定服务的所有日志文件构建索引
        返回格式: {
            'TRACE_ID': [
                {'file_path': '...', 'position': int, 'timestamp': '...'},
                ...
            ]
        }
        """
        import hashlib

        service_dir = os.path.join(self.log_dir, service_name)
        if not os.path.exists(service_dir):
            return {}

        trace_index = {}

        for filename in os.listdir(service_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(service_dir, filename)

                # 计算文件哈希，用于检测文件是否变更
                file_hash = self._get_file_hash(file_path)
                index_file_path = os.path.join(self.index_dir, f"{service_name}_{filename}.index.json")

                # 检查索引文件是否存在且文件未更改
                if os.path.exists(index_file_path):
                    try:
                        with open(index_file_path, 'r', encoding='utf-8') as f:
                            index_data = json.load(f)

                        # 检查文件哈希是否一致
                        if index_data.get('file_hash') == file_hash:
                            # 文件未变化，直接使用现有索引
                            existing_index = index_data.get('trace_index', {})

                            # 合并到总索引中
                            for trace_id, entries in existing_index.items():
                                if trace_id not in trace_index:
                                    trace_index[trace_id] = []
                                trace_index[trace_id].extend(entries)

                            continue
                    except:
                        # 如果索引文件损坏，则重新构建
                        pass

                # 构建当前文件的索引
                file_trace_index = self._build_single_file_index(file_path)

                # 更新总索引
                for trace_id, entries in file_trace_index.items():
                    if trace_id not in trace_index:
                        trace_index[trace_id] = []
                    trace_index[trace_id].extend(entries)

                # 保存此文件的索引
                index_data = {
                    'file_hash': file_hash,
                    'timestamp': datetime.now().isoformat(),
                    'trace_index': file_trace_index
                }

                with open(index_file_path, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, ensure_ascii=False, indent=2)

        return trace_index

    def _build_single_file_index(self, file_path: str) -> Dict[str, List[Dict]]:
        """为单个日志文件构建索引"""
        trace_positions = {}
        position = 0

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines):
            # 查找TraceID模式: TC[A-Z0-9]+
            matches = re.findall(r'\[(TC[A-Z0-9]+)\]', line)
            for trace_id in matches:
                if trace_id not in trace_positions:
                    trace_positions[trace_id] = []

                trace_positions[trace_id].append({
                    'file_path': file_path,
                    'line_num': line_num,
                    'position': position,
                    'timestamp': self._extract_timestamp(line)
                })

            position += len(line.encode('utf-8'))

        return trace_positions

    def _get_file_hash(self, file_path: str) -> str:
        """计算文件的MD5哈希值"""
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # 分块读取大文件
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _extract_timestamp(self, line: str) -> str:
        """从日志行中提取时间戳"""
        match = re.match(r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\]', line)
        return match.group(1) if match else ''

    def build_full_system_index(self) -> Dict[str, Dict[str, List[Dict]]]:
        """为整个系统的日志构建索引"""
        all_services_index = {}

        for service_name in os.listdir(self.log_dir):
            service_path = os.path.join(self.log_dir, service_name)
            if os.path.isdir(service_path):
                print(f"正在为服务 {service_name} 构建索引...")
                service_index = self.build_service_index(service_name)
                all_services_index[service_name] = service_index

        return all_services_index

    def search_by_trace_id(self, trace_id: str) -> List[Dict]:
        """根据TraceID搜索所有相关的日志块"""
        # 扫描所有服务的索引文件
        results = []

        for service_name in os.listdir(self.log_dir):
            service_path = os.path.join(self.log_dir, service_name)
            if os.path.isdir(service_path):
                # 查找对应的服务索引文件
                for filename in os.listdir(service_path):
                    if filename.endswith('.log'):
                        index_file_path = os.path.join(self.index_dir, f"{service_name}_{filename}.index.json")

                        if os.path.exists(index_file_path):
                            try:
                                with open(index_file_path, 'r', encoding='utf-8') as f:
                                    index_data = json.load(f)

                                trace_entries = index_data.get('trace_index', {}).get(trace_id, [])
                                for entry in trace_entries:
                                    # 读取实际的日志内容
                                    with open(entry['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                                        lines = f.readlines()
                                        if entry['line_num'] < len(lines):
                                            content = lines[entry['line_num']].strip()
                                            results.append({
                                                'service': service_name,
                                                'file': filename,
                                                'line_num': entry['line_num'],
                                                'content': content,
                                                'timestamp': entry['timestamp'],
                                                'trace_id': trace_id
                                            })
                            except:
                                continue  # 忽略损坏的索引文件

        # 按时间戳排序
        results.sort(key=lambda x: x['timestamp'])
        return results

    def update_index_if_needed(self, service_name: str) -> bool:
        """检查服务日志是否有更新，如有则更新索引"""
        service_dir = os.path.join(self.log_dir, service_name)
        if not os.path.exists(service_dir):
            return False

        updated = False
        for filename in os.listdir(service_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(service_dir, filename)
                index_file_path = os.path.join(self.index_dir, f"{service_name}_{filename}.index.json")

                # 检查文件是否比索引文件新
                if (not os.path.exists(index_file_path) or
                    os.path.getmtime(file_path) > os.path.getmtime(index_file_path)):
                    # 需要更新索引
                    print(f"更新 {service_name}/{filename} 的索引...")
                    file_trace_index = self._build_single_file_index(file_path)

                    # 保存索引
                    file_hash = self._get_file_hash(file_path)
                    index_data = {
                        'file_hash': file_hash,
                        'timestamp': datetime.now().isoformat(),
                        'trace_index': file_trace_index
                    }

                    with open(index_file_path, 'w', encoding='utf-8') as f:
                        json.dump(index_data, f, ensure_ascii=False, indent=2)

                    updated = True

        return updated