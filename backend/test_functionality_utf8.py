"""
测试脚本 - 验证后端主要功能
"""
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.log_parser import read_log_blocks, find_logs_by_req_sn, parse_log_block
from models.indexer import IndexBuilder
from models.trace_analyzer import TraceAnalyzer

def sanitize_output(text):
    """清理输出中的特殊字符以避免编码问题"""
    if isinstance(text, str):
        # 移除或替换可能导致编码错误的字符
        return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    return str(text)

def test_log_parsing():
    """测试日志解析功能"""
    print("=== 测试日志解析功能 ===")

    # 读取示例日志文件
    sample_log_path = "../../testlogs/testlogs/sft-aipg/sft-aipg-sft-aipg-59c947b9c9-cj6fm_zb_2026040809.log"

    if os.path.exists(sample_log_path):
        print(sanitize_output(f"解析日志文件: {sample_log_path}"))

        # 测试生成器读取
        log_blocks = []
        for i, block in enumerate(read_log_blocks(sample_log_path)):
            log_blocks.append(block)
            if i < 3:  # 只打印前3个日志块作为示例
                print(sanitize_output(f"日志块 {i+1}:"))
                print(sanitize_output(f"  时间戳: {block.timestamp}"))
                print(sanitize_output(f"  TraceID: {block.trace_id}"))
                print(sanitize_output(f"  服务: {block.service}"))
                print(sanitize_output(f"  级别: {block.level}"))
                # 处理内容中的特殊字符以避免编码错误
                content_preview = block.content[:100]
                print(sanitize_output(f"  内容: {content_preview}..."))  # 只显示前100个字符
                print()

            if i >= 9:  # 只处理前10个块用于测试
                break

        print(sanitize_output(f"总共解析了 {len(log_blocks)} 个日志块\n"))
    else:
        print(sanitize_output(f"示例日志文件不存在: {sample_log_path}"))
        # 尝试另一种路径
        alt_path = "D:/sft-log/testlogs/testlogs/sft-aipg/sft-aipg-sft-aipg-59c947b9c9-cj6fm_zb_2026040809.log"
        if os.path.exists(alt_path):
            print(sanitize_output(f"发现日志文件在: {alt_path}"))
            sample_log_path = alt_path
            log_blocks = []
            for i, block in enumerate(read_log_blocks(sample_log_path)):
                log_blocks.append(block)
                if i < 3:  # 只打印前3个日志块作为示例
                    print(sanitize_output(f"日志块 {i+1}:"))
                    print(sanitize_output(f"  时间戳: {block.timestamp}"))
                    print(sanitize_output(f"  TraceID: {block.trace_id}"))
                    print(sanitize_output(f"  服务: {block.service}"))
                    print(sanitize_output(f"  级别: {block.level}"))
                    # 处理内容中的特殊字符以避免编码错误
                    content_preview = block.content[:100]
                    print(sanitize_output(f"  内容: {content_preview}..."))  # 只显示前100个字符
                    print()

                if i >= 9:  # 只处理前10个块用于测试
                    break

            print(sanitize_output(f"总共解析了 {len(log_blocks)} 个日志块\n"))
        else:
            print(sanitize_output("请确保日志文件路径正确\n"))


def test_req_sn_search():
    """测试REQ_SN搜索功能"""
    print("=== 测试REQ_SN搜索功能 ===")

    # 使用示例REQ_SN进行测试
    # 根据提供的日志样本，我们知道REQ_SN是202604080800000001
    req_sn = "202604080800000001"

    print(sanitize_output(f"搜索REQ_SN: {req_sn}"))
    logs = find_logs_by_req_sn('sft-aipg', req_sn, '../../testlogs/testlogs')

    if logs:
        print(sanitize_output(f"找到 {len(logs)} 条相关日志:"))
        for i, log in enumerate(logs[:3]):  # 只显示前3条
            print(sanitize_output(f"  {i+1}. TraceID: {log.trace_id}, 时间: {log.timestamp}"))
            content_preview = log.content[:100]
            print(sanitize_output(f"     内容: {content_preview}..."))
            print()
    else:
        print("未找到相关日志")

    print()


def test_index_builder():
    """测试索引构建功能"""
    print("=== 测试索引构建功能 ===")

    indexer = IndexBuilder('../../testlogs/testlogs', '../logs_index')

    # 为sft-aipg服务构建索引
    print("为sft-aipg服务构建索引...")
    try:
        index = indexer.build_service_index('sft-aipg')
        print(sanitize_output(f"构建完成，找到 {len(index)} 个唯一的TraceID"))

        # 显示前几个TraceID作为示例
        trace_ids = list(index.keys())[:5]
        for trace_id in trace_ids:
            entries = index[trace_id]
            print(sanitize_output(f"  {trace_id}: {len(entries)} 个日志条目"))
    except Exception as e:
        print(sanitize_output(f"构建索引时出错: {e}"))

    print()


def test_trace_analyzer():
    """测试链路追踪分析功能"""
    print("=== 测试链路追踪分析功能 ===")

    analyzer = TraceAnalyzer('../config', '../../testlogs/testlogs')

    # 使用示例REQ_SN进行测试
    req_sn = "202604080800000001"

    print(sanitize_output(f"分析REQ_SN: {req_sn}"))
    try:
        result = analyzer.trace_transaction_chain(req_sn)

        if result['success']:
            print(sanitize_output(f"成功找到链路:"))
            print(sanitize_output(f"  TraceID: {result['trace_id']}"))
            print(sanitize_output(f"  交易类型: {result['transaction_type'] or '未指定'}"))
            print(sanitize_output(f"  日志数量: {len(result['trace_data'])}"))

            # 显示前几个日志条目的摘要
            for i, log_item in enumerate(result['trace_data'][:3]):
                print(sanitize_output(f"  {i+1}. {log_item['timestamp']} - {log_item['app']} - {log_item['level']}"))
        else:
            print(sanitize_output(f"分析失败: {result['error']}"))
    except Exception as e:
        print(sanitize_output(f"分析过程中出错: {e}"))

    print()


if __name__ == "__main__":
    print("开始测试交易日志链路追踪系统后端功能\n")

    test_log_parsing()
    test_req_sn_search()
    test_index_builder()
    test_trace_analyzer()

    print("测试完成！")