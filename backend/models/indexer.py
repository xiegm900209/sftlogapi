"""
日志索引模块
为 TraceID 和 REQ_SN 建立索引，加速查询
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set


class IndexBuilder:
    """索引构建器"""
    
    def __init__(self, log_dir: str = '/app/logs', index_dir: str = '/app/logs_index'):
        self.log_dir = log_dir
        self.index_dir = index_dir
        self.trace_id_index: Dict[str, Set[str]] = {}  # TraceID -> {文件路径}
        self.req_sn_index: Dict[str, Set[str]] = {}    # REQ_SN -> {文件路径}
        
    def build_index(self, services: List[str] = None):
        """
        构建索引
        
        Args:
            services: 服务列表，不指定则扫描所有服务
        """
        if not services:
            services = self._scan_services()
        
        for service in services:
            self._index_service(service)
    
    def _scan_services(self) -> List[str]:
        """扫描所有服务目录"""
        services = []
        if os.path.exists(self.log_dir):
            for item in os.listdir(self.log_dir):
                item_path = os.path.join(self.log_dir, item)
                if os.path.isdir(item_path):
                    services.append(item)
        return services
    
    def _index_service(self, service: str):
        """为单个服务构建索引"""
        service_dir = os.path.join(self.log_dir, service)
        if not os.path.exists(service_dir):
            return
        
        for filename in os.listdir(service_dir):
            if filename.endswith('.log') or filename.endswith('.log.gz'):
                file_path = os.path.join(service_dir, filename)
                self._index_file(file_path)
    
    def _index_file(self, file_path: str):
        """为单个日志文件构建索引"""
        from models.log_parser import read_log_blocks
        
        try:
            for log_block in read_log_blocks(file_path):
                # 索引 TraceID
                if log_block.trace_id:
                    if log_block.trace_id not in self.trace_id_index:
                        self.trace_id_index[log_block.trace_id] = set()
                    self.trace_id_index[log_block.trace_id].add(file_path)
                
                # 索引 REQ_SN
                if isinstance(log_block.parsed_content, dict):
                    req_sn = log_block.parsed_content.get('req_sn')
                    if req_sn:
                        if req_sn not in self.req_sn_index:
                            self.req_sn_index[req_sn] = set()
                        self.req_sn_index[req_sn].add(file_path)
        except Exception as e:
            print(f"索引文件失败 {file_path}: {e}")
    
    def save_index(self, index_file: str = None):
        """保存索引到文件"""
        if not index_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            index_file = os.path.join(self.index_dir, f'index_{timestamp}.json')
        
        os.makedirs(os.path.dirname(index_file), exist_ok=True)
        
        # 转换 set 为 list（JSON 不支持 set）
        index_data = {
            'trace_id_index': {k: list(v) for k, v in self.trace_id_index.items()},
            'req_sn_index': {k: list(v) for k, v in self.req_sn_index.items()},
            'created_at': datetime.now().isoformat()
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print(f"索引已保存到：{index_file}")
        return index_file
    
    def load_index(self, index_file: str = None):
        """从文件加载索引"""
        if not index_file:
            index_file = self._find_latest_index()
        
        if not index_file or not os.path.exists(index_file):
            print("未找到索引文件")
            return False
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 转换 list 回 set
            self.trace_id_index = {k: set(v) for k, v in index_data.get('trace_id_index', {}).items()}
            self.req_sn_index = {k: set(v) for k, v in index_data.get('req_sn_index', {}).items()}
            
            print(f"索引已加载：{index_file}")
            print(f"  TraceID 索引：{len(self.trace_id_index)} 条")
            print(f"  REQ_SN 索引：{len(self.req_sn_index)} 条")
            return True
        except Exception as e:
            print(f"加载索引失败：{e}")
            return False
    
    def _find_latest_index(self) -> Optional[str]:
        """查找最新的索引文件"""
        if not os.path.exists(self.index_dir):
            return None
        
        index_files = [f for f in os.listdir(self.index_dir) if f.startswith('index_') and f.endswith('.json')]
        if not index_files:
            return None
        
        index_files.sort(reverse=True)
        return os.path.join(self.index_dir, index_files[0])
    
    def find_files_by_trace_id(self, trace_id: str) -> List[str]:
        """通过 TraceID 查找文件"""
        return list(self.trace_id_index.get(trace_id, set()))
    
    def find_files_by_req_sn(self, req_sn: str) -> List[str]:
        """通过 REQ_SN 查找文件"""
        return list(self.req_sn_index.get(req_sn, set()))


class IndexManager:
    """索引管理器（单例模式）"""
    
    _instance = None
    _indexer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_indexer(self, auto_load: bool = True) -> IndexBuilder:
        """获取索引构建器"""
        if self._indexer is None:
            self._indexer = IndexBuilder()
            if auto_load:
                self._indexer.load_index()
        return self._indexer
    
    def rebuild_index(self, services: List[str] = None):
        """重建索引"""
        indexer = self.get_indexer(auto_load=False)
        indexer.build_index(services)
        indexer.save_index()


# 全局索引管理器
index_manager = IndexManager()
