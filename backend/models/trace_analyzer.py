import json
import os
from typing import Dict, List, Optional
from models.log_parser import find_logs_by_req_sn, find_logs_by_trace_id
from models.indexer import IndexBuilder


class TraceAnalyzer:
    """链路追踪分析器"""

    def __init__(self, config_dir: str = '/root/sft/log-tracker/config', log_dir: str = '/root/sft/testlogs'):
        self.config_dir = config_dir
        self.log_dir = log_dir
        self.index_builder = IndexBuilder(log_dir=log_dir)

        # 加载配置
        self.transaction_types = self._load_transaction_types()
        self.log_dirs = self._load_log_dirs()

    def _load_transaction_types(self) -> Dict:
        """加载交易类型配置"""
        config_path = os.path.join(self.config_dir, 'transaction_types.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "310011": {
                    "name": "协议支付",
                    "apps": ["sft-aipg", "sft-trxqry", "sft-pay"]
                },
                "310016": {
                    "name": "批量协议支付",
                    "apps": ["sft-aipg", "sft-trxqry", "sft-batchpay"]
                },
                "310002": {
                    "name": "协议支付签约",
                    "apps": ["sft-aipg", "sft-contract"]
                },
                "200004": {
                    "name": "交易查询",
                    "apps": ["sft-aipg", "sft-trxqry"]
                }
            }

    def load_transaction_types(self):
        """重新加载交易类型配置（用于配置更新后）"""
        self.transaction_types = self._load_transaction_types()

    def load_log_dirs(self):
        """重新加载日志目录配置（用于配置更新后）"""
        self.log_dirs = self._load_log_dirs()

    def _load_log_dirs(self) -> Dict:
        """加载日志目录配置"""
        config_path = os.path.join(self.config_dir, 'log_dirs.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "sft-aipg": "/root/sft/testlogs/sft-aipg",
                "sft-trxqry": "/root/sft/testlogs/sft-trxqry",
                "sft-pay": "/root/sft/testlogs/sft-pay",
                "sft-batchpay": "/root/sft/testlogs/sft-batchpay",
                "sft-contract": "/root/sft/testlogs/sft-contract"
            }

    def trace_transaction_chain(self, req_sn: str, transaction_type: Optional[str] = None) -> Dict:
        """
        追踪完整交易链路
        """
        # 1. 在入口应用日志中查找REQ_SN (默认为sft-aipg)
        initial_logs = find_logs_by_req_sn('sft-aipg', req_sn, self.log_dir)

        if not initial_logs:
            return {
                'success': False,
                'error': f'未找到REQ_SN为 {req_sn} 的日志',
                'trace_data': []
            }

        # 2. 提取TraceID
        trace_id = initial_logs[0].trace_id

        if not trace_id:
            return {
                'success': False,
                'error': f'无法从REQ_SN {req_sn} 提取TraceID',
                'trace_data': []
            }

        # 3. 确定需要追踪的应用列表
        related_apps = self._get_apps_for_transaction_type(transaction_type)

        # 4. 在相关应用中查找该TraceID的所有日志
        all_logs = {'sft-aipg': initial_logs}

        for app in related_apps:
            if app != 'sft-aipg':  # 避免重复查询入口应用
                app_logs = find_logs_by_trace_id(app, trace_id, self.log_dir)
                all_logs[app] = app_logs

        # 5. 整理并按时间顺序合并日志
        timeline = self._merge_and_sort_logs(all_logs)

        return {
            'success': True,
            'req_sn': req_sn,
            'trace_id': trace_id,
            'transaction_type': transaction_type,
            'trace_data': timeline
        }

    def _get_apps_for_transaction_type(self, transaction_type: Optional[str]) -> List[str]:
        """获取特定交易类型关联的应用列表"""
        if transaction_type and transaction_type in self.transaction_types:
            return self.transaction_types[transaction_type].get('apps', [])
        elif transaction_type:
            # 如果指定的交易类型不存在，返回默认的常用应用
            return ['sft-aipg', 'sft-trxqry']
        else:
            # 如果未指定交易类型，返回所有已知的应用
            all_apps = set()
            for config in self.transaction_types.values():
                all_apps.update(config.get('apps', []))
            return list(all_apps)

    def _merge_and_sort_logs(self, all_logs: Dict[str, List]) -> List[Dict]:
        """将来自不同应用的日志合并并按时间排序"""
        timeline = []

        for app, logs in all_logs.items():
            for log in logs:
                # 解析时间戳
                try:
                    timestamp = log.timestamp
                    parsed_time = timestamp.replace(' ', 'T') + '+08:00'  # 假设为北京时间
                except:
                    parsed_time = ''

                timeline.append({
                    'timestamp': parsed_time,
                    'app': app,
                    'trace_id': log.trace_id,
                    'level': log.level,
                    'thread': log.thread,
                    'content': log.content,
                    'parsed_content': log.parsed_content
                })

        # 按时间戳排序
        timeline.sort(key=lambda x: x['timestamp'])

        return timeline

    def get_transaction_summary(self, req_sn: str, transaction_type: Optional[str] = None) -> Dict:
        """获取交易摘要信息"""
        trace_result = self.trace_transaction_chain(req_sn, transaction_type)

        if not trace_result['success']:
            return trace_result

        trace_data = trace_result['trace_data']

        # 统计各应用的处理情况
        app_stats = {}
        for item in trace_data:
            app = item['app']
            if app not in app_stats:
                app_stats[app] = {'count': 0, 'levels': {}}
            app_stats[app]['count'] += 1

            level = item['level']
            if level not in app_stats[app]['levels']:
                app_stats[app]['levels'][level] = 0
            app_stats[app]['levels'][level] += 1

        # 找出交易的开始和结束时间
        start_time = trace_data[0]['timestamp'] if trace_data else ''
        end_time = trace_data[-1]['timestamp'] if trace_data else ''

        # 提取关键业务信息
        business_info = self._extract_business_info(trace_data)

        summary = {
            'req_sn': req_sn,
            'trace_id': trace_result['trace_id'],
            'transaction_type': transaction_type,
            'start_time': start_time,
            'end_time': end_time,
            'duration': self._calculate_duration(start_time, end_time),
            'total_logs': len(trace_data),
            'apps_involved': list(app_stats.keys()),
            'app_statistics': app_stats,
            'business_info': business_info
        }

        return {
            'success': True,
            'summary': summary,
            'trace_data': trace_data
        }

    def _extract_business_info(self, trace_data: List[Dict]) -> Dict:
        """从日志中提取业务相关信息"""
        business_info = {
            'trx_codes': [],
            'ret_codes': [],
            'amounts': [],
            'accounts': [],
            'errors': []
        }

        for item in trace_data:
            parsed = item['parsed_content']
            if 'data' in parsed and isinstance(parsed['data'], dict):
                # 提取交易代码
                if 'TRX_CODE' in parsed['data']:
                    trx_code = parsed['data']['TRX_CODE']
                    if trx_code not in business_info['trx_codes']:
                        business_info['trx_codes'].append(trx_code)

                # 提取返回码
                info_section = parsed['data'].get('INFO', {})
                if 'RET_CODE' in info_section:
                    ret_code = info_section['RET_CODE']
                    if ret_code not in business_info['ret_codes']:
                        business_info['ret_codes'].append(ret_code)

                # 提取错误信息
                if 'ERR_MSG' in info_section:
                    err_msg = info_section['ERR_MSG']
                    if err_msg not in business_info['errors']:
                        business_info['errors'].append(err_msg)

            # 提取金额和账号信息（如果存在于普通内容中）
            content = item['content']
            if 'AMOUNT' in content:
                import re
                amounts = re.findall(r'AMOUNT[^>]*>([^<]*)', content)
                business_info['amounts'].extend(amounts)

            if 'ACCOUNT_NO' in content:
                import re
                accounts = re.findall(r'ACCOUNT_NO[^>]*>([^<]*)', content)
                business_info['accounts'].extend(accounts)

        return business_info

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """计算时间间隔"""
        if not start_time or not end_time:
            return ''

        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_time.replace('T', ' ').replace('+08:00', ''))
            end_dt = datetime.fromisoformat(end_time.replace('T', ' ').replace('+08:00', ''))
            duration = end_dt - start_dt
            return str(duration)
        except:
            return '计算失败'

    def update_config(self, config_type: str, data: Dict) -> bool:
        """更新配置"""
        try:
            config_path = os.path.join(self.config_dir, f'{config_type}.json')
            os.makedirs(self.config_dir, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 重新加载配置
            if config_type == 'transaction_types':
                self.transaction_types = self._load_transaction_types()
            elif config_type == 'log_dirs':
                self.log_dirs = self._load_log_dirs()

            return True
        except Exception as e:
            print(f"更新配置失败: {str(e)}")
            return False