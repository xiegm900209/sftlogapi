<template>
  <div class="log-viewer">
    <div v-if="logs && logs.length > 0" class="logs-container">
      <div
        v-for="(log, index) in logs"
        :key="index"
        :class="['log-entry', log.level.toLowerCase()]"
        @click="selectedLog = log"
      >
        <div class="log-header">
          <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
          <span class="log-trace-id" v-if="log.trace_id">#{{ log.trace_id }}</span>
          <span class="log-level" :style="{ color: getLevelColor(log.level) }">{{ log.level }}</span>
          <span class="log-service">{{ log.service }}</span>
        </div>
        <div class="log-content" v-html="highlightXml(log.content)"></div>
      </div>
    </div>
    <div v-else class="empty-state">
      <el-empty description="暂无日志数据"></el-empty>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="showLogDetail"
      title="日志详情"
      width="80%"
      :before-close="closeLogDetail"
    >
      <div v-if="selectedLog" class="log-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="时间戳">{{ selectedLog.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="线程">{{ selectedLog.thread }}</el-descriptions-item>
          <el-descriptions-item label="TraceID">{{ selectedLog.trace_id }}</el-descriptions-item>
          <el-descriptions-item label="级别" :contentStyle="{ color: getLevelColor(selectedLog.level) }">
            {{ selectedLog.level }}
          </el-descriptions-item>
          <el-descriptions-item label="环境">{{ selectedLog.env }}</el-descriptions-item>
          <el-descriptions-item label="公司">{{ selectedLog.company }}</el-descriptions-item>
          <el-descriptions-item label="服务">{{ selectedLog.service }}</el-descriptions-item>
        </el-descriptions>

        <div class="log-content-detail">
          <h4>内容:</h4>
          <pre>{{ selectedLog.content }}</pre>
        </div>

        <div v-if="selectedLog.parsed_content && selectedLog.parsed_content.data" class="parsed-data">
          <h4>解析的数据:</h4>
          <pre>{{ JSON.stringify(selectedLog.parsed_content.data, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { formatTimestamp, getLevelColor, highlightXml } from '@/utils/logParser'

export default {
  name: 'LogViewer',
  props: {
    logs: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedLog: null,
      showLogDetail: false
    }
  },
  methods: {
    formatTimestamp,
    getLevelColor,
    highlightXml,

    closeLogDetail() {
      this.showLogDetail = false
      this.selectedLog = null
    }
  },
  watch: {
    selectedLog(newVal) {
      if (newVal) {
        this.showLogDetail = true
      }
    }
  }
}
</script>

<style scoped>
.log-viewer {
  width: 100%;
}

.logs-container {
  max-height: 600px;
  overflow-y: auto;
}

.log-entry {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.log-entry:hover {
  border-color: #c6e2ff;
  box-shadow: 0 0 8px rgba(144, 147, 153, 0.2);
  background-color: #f5f7fa;
}

.log-entry.error {
  border-left: 4px solid #f56565;
}

.log-entry.warn {
  border-left: 4px solid #dd6b20;
}

.log-entry.info {
  border-left: 4px solid #38a169;
}

.log-entry.debug {
  border-left: 4px solid #4299e1;
}

.log-header {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
  font-weight: bold;
  font-size: 13px;
}

.log-timestamp {
  color: #909399;
  flex: 1;
}

.log-trace-id {
  color: #409eff;
  font-family: monospace;
}

.log-level {
  font-weight: bold;
}

.log-service {
  color: #606266;
}

.log-content {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #303133;
}

.xml-tag {
  color: #0b7500;
  font-weight: bold;
}

.xml-attr-value {
  color: #cc0000;
}

.xml-content {
  color: #000000;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.log-detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.log-content-detail pre {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
}

.parsed-data pre {
  background-color: #f0f9eb;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
}
</style>