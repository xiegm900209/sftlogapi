import re
import gzip
from datetime import datetime
from typing import Generator, Dict, List, Optional
import xml.etree.ElementTree as ET


class LogBlock:
    """日志块数据结构"""
    def __init__(self, timestamp: str, thread: str, trace_id: str, level: str,
                 env: str, company: str, service: str, content: str):
        self.timestamp = timestamp
        self.thread = thread
        self.trace_id = trace_id
        self.level = level
        self.env = env
        self.company = company
        self.service = service
        self.content = content
        self.parsed_content = self._parse_content(content)

    def _parse_content(self, content: str) -> Dict:
        """解析日志内容，提取关键信息"""
        parsed = {'original': content}

        # 尝试解析 XML 内容
        if '<?xml' in content and '</AIPG>' in content:
            try:
                xml_start = content.find('<?xml')
                xml_end = content.rfind('>') + 1
                xml_str = content[xml_start:xml_end]

                root = ET.fromstring(xml_str)
                parsed['type'] = 'xml'
                parsed['data'] = self._xml_to_dict(root)

                info_elem = root.find('.//INFO')
                if info_elem is not None:
                    req_sn_elem = info_elem.find('REQ_SN')
                    if req_sn_elem is not None:
                        parsed['req_sn'] = req_sn_elem.text

                    trx_code_elem = info_elem.find('TRX_CODE')
                    if trx_code_elem is not None:
                        parsed['trx_code'] = trx_code_elem.text

            except ET.ParseError:
                parsed['type'] = 'malformed_xml'
        else:
            parsed['type'] = 'text'

        return parsed

    def _xml_to_dict(self, element):
        """将 XML 元素转换为字典"""
        result = {}
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()

        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result


def read_log_blocks(file_path: str) -> Generator[LogBlock, None, None]:
    """
    使用生成器逐块读取日志文件
    每条完整的日志记录以时间戳 [YYYY-MM-DD HH:mm:ss.SSS] 开头
    如果一行不以时间戳开头，它属于上一条日志的延续（多行日志）
    
    支持:
    - 普通日志文件 (.log)
    - Gzip 压缩文件 (.log.gz)
    - GBK 和 UTF-8 编码
    """
    # 检查是否为 gzip 文件
    is_gzip_file = file_path.endswith('.gz')
    
    # 尝试不同编码读取文件 - GBK 在前因为中文日志通常是 GBK
    encodings = ['gbk', 'gb18030', 'utf-8']
    content = None
    used_encoding = 'utf-8'
    
    try:
        if is_gzip_file:
            # 使用 gzip 读取压缩文件
            for encoding in encodings:
                try:
                    with gzip.open(file_path, 'rt', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, gzip.BadGzipFile, EOFError, OSError):
                    continue
            
            if content is None:
                # 如果编码都失败，尝试二进制读取
                with gzip.open(file_path, 'rb') as f:
                    raw_bytes = f.read()
                try:
                    content = raw_bytes.decode('gbk', errors='replace')
                    used_encoding = 'gbk (from gzip)'
                except:
                    content = raw_bytes.decode('latin-1')
                    used_encoding = 'latin-1'
        else:
            # 普通文件读取
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if content is None:
                with open(file_path, 'rb') as f:
                    raw_bytes = f.read()
                try:
                    content = raw_bytes.decode('gbk', errors='replace')
                    used_encoding = 'gbk (from binary)'
                except:
                    content = raw_bytes.decode('latin-1')
                    used_encoding = 'latin-1'
    except Exception as e:
        # 如果文件读取失败，返回空内容
        print(f"Warning: Failed to read {file_path}: {e}")
        return
    
    # 按行处理
    lines = content.split('\n')
    current_block_lines = []

    for line in lines:
        # 检查是否为新的日志块开头（以时间戳开始）
        if re.match(r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\]', line):
            if current_block_lines:
                # 解析上一个日志块
                yield parse_log_block(''.join(current_block_lines))

            current_block_lines = [line]
        else:
            # 续行内容，添加到当前块
            current_block_lines.append(line)

    # 处理最后一个块
    if current_block_lines:
        yield parse_log_block(''.join(current_block_lines))


def parse_log_block(block_text: str) -> Optional[LogBlock]:
    """
    解析单个日志块的文本，提取各个字段
    格式：[timestamp][thread][trace_id][level][env][company][service][]-[content]
    
    支持多行日志：第一行包含头部信息，后续行是 content 的延续
    """
    lines = block_text.split('\n')
    first_line = lines[0] if lines else ''
    
    # 正则表达式匹配日志头部格式
    # [2026-04-08 09:00:00.335][http-apr-8195-exec-2284][TC5PCfGK][DEBUG][C02][sft][sft-aipg][]-[content]
    pattern = r'^\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[\]-\[(.*)$'
    
    match = re.match(pattern, first_line.strip())
    if not match:
        # 如果无法解析，返回基本结构
        return LogBlock(
            timestamp='',
            thread='',
            trace_id='',
            level='',
            env='',
            company='',
            service='',
            content=block_text
        )

    groups = match.groups()
    timestamp = groups[0]
    thread = groups[1]
    trace_id = groups[2]
    level = groups[3]
    env = groups[4]
    company = groups[5]
    service = groups[6]
    
    # 第一行的 content 部分（可能不完整）
    first_content = groups[7] if len(groups) > 7 else ''
    
    # 合并所有行作为完整内容（包括续行）
    # 移除末尾的 ?:?] 标记
    full_content = block_text.strip()
    if full_content.endswith('?:?]'):
        full_content = full_content[:-4]
    
    # 第一行 content 移除末尾的 ?:?]
    content_start = first_content
    if content_start.endswith('?:?]'):
        content_start = content_start[:-4]
    
    # 如果有续行，合并所有内容
    if len(lines) > 1:
        content = full_content
    else:
        content = content_start

    return LogBlock(timestamp, thread, trace_id, level, env, company, service, content)


def find_logs_by_req_sn(service_name: str, req_sn: str, log_dir: str = '/root/sft/testlogs') -> List[LogBlock]:
    """
    根据 REQ_SN 在指定服务的日志中查找对应的日志块
    """
    import os

    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return []

    result = []
    for filename in os.listdir(service_dir):
        if filename.endswith('.log') or filename.endswith('.log.gz'):
            file_path = os.path.join(service_dir, filename)
            for log_block in read_log_blocks(file_path):
                if 'req_sn' in log_block.parsed_content and log_block.parsed_content['req_sn'] == req_sn:
                    result.append(log_block)

    return result


def find_logs_by_trace_id(service_name: str, trace_id: str, log_dir: str = '/root/sft/testlogs') -> List[LogBlock]:
    """
    根据 TraceID 在指定服务的日志中查找对应的日志块
    """
    import os

    service_dir = os.path.join(log_dir, service_name)
    if not os.path.exists(service_dir):
        return []

    result = []
    for filename in os.listdir(service_dir):
        if filename.endswith('.log') or filename.endswith('.log.gz'):
            file_path = os.path.join(service_dir, filename)
            for log_block in read_log_blocks(file_path):
                if log_block.trace_id == trace_id:
                    result.append(log_block)

    return result
