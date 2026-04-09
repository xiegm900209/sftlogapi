/**
 * API 接口封装
 */

import axios from 'axios';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: '/api', // 后端API的基础路径
  timeout: 30000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * 拦截请求
 */
apiClient.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，如添加认证token
    return config;
  },
  error => {
    // 请求错误处理
    return Promise.reject(error);
  }
);

/**
 * 拦截响应
 */
apiClient.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response;
  },
  error => {
    // 响应错误处理
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

/**
 * 根据REQ_SN搜索日志
 * @param {string} reqSn - 请求序列号
 * @param {string} service - 服务名称，默认为sft-aipg
 * @returns {Promise<object>}
 */
export function searchByReqSn(reqSn, service = 'sft-aipg') {
  return apiClient.get('/search', {
    params: {
      req_sn: reqSn,
      service
    }
  });
}

/**
 * 追踪交易链路
 * @param {string} reqSn - 请求序列号
 * @param {string} transactionType - 交易类型
 * @returns {Promise<object>}
 */
export function traceTransaction(reqSn, transactionType = null) {
  return apiClient.get('/trace', {
    params: {
      req_sn: reqSn,
      transaction_type: transactionType
    }
  });
}

/**
 * 获取交易链路摘要
 * @param {string} reqSn - 请求序列号
 * @param {string} transactionType - 交易类型
 * @returns {Promise<object>}
 */
export function getTransactionSummary(reqSn, transactionType = null) {
  return apiClient.get('/trace-summary', {
    params: {
      req_sn: reqSn,
      transaction_type: transactionType
    }
  });
}

/**
 * 根据TraceID搜索日志
 * @param {string} traceId - 追踪ID
 * @param {string} service - 服务名称，为空表示搜索所有服务
 * @returns {Promise<object>}
 */
export function searchByTraceId(traceId, service = '') {
  return apiClient.get('/search-by-trace', {
    params: {
      trace_id: traceId,
      service
    }
  });
}

/**
 * 获取可用服务列表
 * @returns {Promise<object>}
 */
export function getAvailableServices() {
  return apiClient.get('/services');
}

/**
 * 获取支持的交易类型
 * @returns {Promise<object>}
 */
export function getTransactionTypes() {
  return apiClient.get('/transaction-types');
}

/**
 * 全文搜索
 * @param {string} query - 搜索查询
 * @param {string} service - 服务名称，默认为all
 * @param {boolean} caseSensitive - 是否区分大小写
 * @param {number} maxResults - 最大结果数
 * @returns {Promise<object>}
 */
export function fullTextSearch(query, service = 'all', caseSensitive = false, maxResults = 100) {
  return apiClient.post('/search/full-text', {
    query,
    service,
    case_sensitive: caseSensitive,
    max_results: maxResults
  });
}

/**
 * 按时间范围搜索
 * @param {string} startTime - 开始时间
 * @param {string} endTime - 结束时间
 * @param {string} service - 服务名称，默认为all
 * @returns {Promise<object>}
 */
export function searchByTimeRange(startTime, endTime, service = 'all') {
  return apiClient.post('/search/by-time-range', {
    start_time: startTime,
    end_time: endTime,
    service
  });
}

/**
 * 按日志级别搜索
 * @param {string} level - 日志级别
 * @param {string} service - 服务名称，默认为all
 * @param {number} hoursBack - 查询过去多少小时
 * @returns {Promise<object>}
 */
export function searchByLogLevel(level, service = 'all', hoursBack = 1) {
  return apiClient.get('/search/by-level', {
    params: {
      level,
      service,
      hours_back: hoursBack
    }
  });
}

/**
 * 获取日志文件列表
 * @param {string} service - 服务名称，默认为all
 * @returns {Promise<object>}
 */
export function getLogFiles(service = 'all') {
  return apiClient.get('/search/log-files', {
    params: {
      service
    }
  });
}

/**
 * 获取应用配置
 * @returns {Promise<object>}
 */
export function getAppConfig() {
  return apiClient.get('/config/get-app-config');
}

/**
 * 更新应用配置
 * @param {object} config - 配置对象
 * @returns {Promise<object>}
 */
export function updateAppConfig(config) {
  return apiClient.post('/config/update-app-config', config);
}

/**
 * 获取交易类型配置
 * @returns {Promise<object>}
 */
export function getTransactionTypesConfig() {
  return apiClient.get('/config/get-transaction-types');
}

/**
 * 更新交易类型配置
 * @param {object} config - 交易类型配置
 * @returns {Promise<object>}
 */
export function updateTransactionTypesConfig(config) {
  return apiClient.post('/config/update-transaction-types', config);
}

/**
 * 获取日志目录配置
 * @returns {Promise<object>}
 */
export function getLogDirsConfig() {
  return apiClient.get('/config/get-log-dirs');
}

/**
 * 更新日志目录配置
 * @param {object} config - 日志目录配置
 * @returns {Promise<object>}
 */
export function updateLogDirsConfig(config) {
  return apiClient.post('/config/update-log-dirs', config);
}

/**
 * 验证配置
 * @param {object} config - 要验证的配置
 * @returns {Promise<object>}
 */
export function validateConfig(config) {
  return apiClient.post('/config/validate-config', config);
}

/**
 * 获取可用服务列表
 * @returns {Promise<object>}
 */
export function getAvailableServicesConfig() {
  return apiClient.get('/config/get-available-services');
}