/**
 * 日志解析工具函数
 */

/**
 * 解析日志行，提取时间戳、traceId等信息
 * @param {string} logLine - 日志行内容
 * @returns {object} 解析后的日志信息
 */
export function parseLogLine(logLine) {
  // 正则表达式匹配日志格式: [timestamp][thread][trace_id][level][env][company][service][]-[content]
  const logPattern = /^\[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\[(.+?)\]\[\]-\[(.+?)\s*\?:\?\]$/;

  const match = logLine.match(logPattern);

  if (match) {
    const [, timestamp, thread, traceId, level, env, company, service, content] = match;

    return {
      timestamp,
      thread,
      traceId,
      level,
      env,
      company,
      service,
      content: content || '',
      isValid: true
    };
  } else {
    // 尝试解析非标准格式的日志
    return {
      timestamp: '',
      thread: '',
      traceId: '',
      level: '',
      env: '',
      company: '',
      service: '',
      content: logLine,
      isValid: false
    };
  }
}

/**
 * 从日志内容中提取XML信息
 * @param {string} content - 日志内容
 * @returns {object|null} 解析后的XML信息
 */
export function extractXmlInfo(content) {
  if (!content.includes('<?xml') || !content.includes('</AIPG>')) {
    return null;
  }

  try {
    // 提取XML部分
    const xmlStart = content.indexOf('<?xml');
    const xmlEnd = content.lastIndexOf('>') + 1;
    const xmlStr = content.substring(xmlStart, xmlEnd);

    // 简单的XML解析（在浏览器环境中，我们可以使用DOMParser）
    // 这里仅做演示，实际实现会更复杂
    const infoMatch = xmlStr.match(/<TRX_CODE>(.*?)<\/TRX_CODE>/);
    const reqSnMatch = xmlStr.match(/<REQ_SN>(.*?)<\/REQ_SN>/);
    const retCodeMatch = xmlStr.match(/<RET_CODE>(.*?)<\/RET_CODE>/);

    return {
      trxCode: infoMatch ? infoMatch[1] : null,
      reqSn: reqSnMatch ? reqSnMatch[1] : null,
      retCode: retCodeMatch ? retCodeMatch[1] : null,
      xmlContent: xmlStr
    };
  } catch (error) {
    console.warn('XML解析失败:', error);
    return null;
  }
}

/**
 * 高亮显示XML内容
 * @param {string} content - 要高亮的内容
 * @returns {string} 高亮后的HTML
 */
export function highlightXml(content) {
  if (!content) return content;

  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(<\/?[\w]+:?[\w]*\s*)/g, '<span class="xml-tag">$1</span>')
    .replace(/(&lt;\/?[\w]+:?[\w]*\s*&gt;)/g, '<span class="xml-tag">$1</span>')
    .replace(/("[^"]*")/g, '<span class="xml-attr-value">$1</span>')
    .replace(/(&gt;)([^<&]*?)(&lt;\/)/g, '$1<span class="xml-content">$2</span>$3');
}

/**
 * 格式化时间戳
 * @param {string} timestamp - 时间戳字符串
 * @returns {string} 格式化后的时间
 */
export function formatTimestamp(timestamp) {
  if (!timestamp) return '';

  try {
    // 时间戳格式: YYYY-MM-DD HH:mm:ss.SSS
    const date = new Date(timestamp.replace(' ', 'T'));
    return date.toLocaleString();
  } catch (error) {
    return timestamp;
  }
}

/**
 * 根据级别返回颜色
 * @param {string} level - 日志级别
 * @returns {string} 对应的颜色
 */
export function getLevelColor(level) {
  const colors = {
    'ERROR': '#F56565',
    'WARN': '#DD6B20',
    'INFO': '#38A169',
    'DEBUG': '#4299E1'
  };

  return colors[level.toUpperCase()] || '#000000';
}