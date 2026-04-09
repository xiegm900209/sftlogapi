from flask import Blueprint, request, jsonify
import json
import os

bp = Blueprint('config', __name__)


@bp.route('/get-app-config', methods=['GET'])
def get_app_config():
    """获取应用配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'app_config.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 默认配置
            config = {
                "app_name": "Log Tracker",
                "version": "1.0.0",
                "debug": True,
                "log_level": "INFO",
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "index_update_interval": 300,  # 5分钟
                "max_search_results": 1000
            }

        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'error': f'获取应用配置失败: {str(e)}'}), 500


@bp.route('/update-app-config', methods=['POST'])
def update_app_config():
    """更新应用配置"""
    data = request.get_json()

    if not data:
        return jsonify({'error': '缺少配置数据'}), 400

    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, 'app_config.json')

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': '应用配置已更新'
        })
    except Exception as e:
        return jsonify({'error': f'更新应用配置失败: {str(e)}'}), 500


@bp.route('/get-transaction-types', methods=['GET'])
def get_transaction_types_config():
    """获取交易类型配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'transaction_types.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 默认配置
            config = {
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

        return jsonify({
            'success': True,
            'transaction_types': config
        })
    except Exception as e:
        return jsonify({'error': f'获取交易类型配置失败: {str(e)}'}), 500


@bp.route('/update-transaction-types', methods=['POST'])
def update_transaction_types_config():
    """更新交易类型配置"""
    data = request.get_json()

    if not data:
        return jsonify({'error': '缺少交易类型配置数据'}), 400

    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, 'transaction_types.json')

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': '交易类型配置已更新'
        })
    except Exception as e:
        return jsonify({'error': f'更新交易类型配置失败: {str(e)}'}), 500


@bp.route('/get-log-dirs', methods=['GET'])
def get_log_dirs_config():
    """获取日志目录配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'log_dirs.json')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 默认配置
            config = {
                "sft-aipg": "../testlogs/testlogs/sft-aipg",
                "sft-trxqry": "../testlogs/testlogs/sft-trxqry",
                "sft-pay": "../testlogs/testlogs/sft-pay",
                "sft-batchpay": "../testlogs/testlogs/sft-batchpay",
                "sft-contract": "../testlogs/testlogs/sft-contract"
            }

        return jsonify({
            'success': True,
            'log_dirs': config
        })
    except Exception as e:
        return jsonify({'error': f'获取日志目录配置失败: {str(e)}'}), 500


@bp.route('/update-log-dirs', methods=['POST'])
def update_log_dirs_config():
    """更新日志目录配置"""
    data = request.get_json()

    if not data:
        return jsonify({'error': '缺少日志目录配置数据'}), 400

    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, 'log_dirs.json')

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': '日志目录配置已更新'
        })
    except Exception as e:
        return jsonify({'error': f'更新日志目录配置失败: {str(e)}'}), 500


@bp.route('/get-available-services', methods=['GET'])
def get_available_services():
    """获取系统中可用的服务列表"""
    try:
        import os
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'testlogs', 'testlogs')

        if not os.path.exists(log_dir):
            return jsonify({
                'success': True,
                'services': []
            })

        services = []
        for item in os.listdir(log_dir):
            item_path = os.path.join(log_dir, item)
            if os.path.isdir(item_path):
                services.append(item)

        return jsonify({
            'success': True,
            'services': services
        })
    except Exception as e:
        return jsonify({'error': f'获取服务列表失败: {str(e)}'}), 500


@bp.route('/validate-config', methods=['POST'])
def validate_config():
    """验证配置的有效性"""
    data = request.get_json()

    if not data:
        return jsonify({'error': '缺少配置数据'}), 400

    errors = []

    # 验证日志目录配置
    if 'log_dirs' in data:
        for service, path in data['log_dirs'].items():
            if not os.path.exists(path):
                errors.append(f"服务 {service} 的日志目录不存在: {path}")

    # 验证交易类型配置
    if 'transaction_types' in data:
        for trx_code, config in data['transaction_types'].items():
            if 'name' not in config:
                errors.append(f"交易类型 {trx_code} 缺少名称")
            if 'apps' not in config:
                errors.append(f"交易类型 {trx_code} 缺少关联应用列表")
            elif not isinstance(config['apps'], list):
                errors.append(f"交易类型 {trx_code} 的应用列表格式不正确")

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        })
    else:
        return jsonify({
            'success': True,
            'message': '配置验证通过'
        })