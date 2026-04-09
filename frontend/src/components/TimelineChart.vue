<template>
  <div class="timeline-chart">
    <div v-if="timelineData && timelineData.length > 0" class="chart-container">
      <!-- 时间轴 -->
      <div class="timeline-axis">
        <div
          v-for="(item, index) in timelineData"
          :key="index"
          class="timeline-item"
          :style="{ left: `${(index / (timelineData.length - 1)) * 100}%` }"
        >
          <div class="event-point" :style="{ borderColor: getLevelColor(item.level) }">
            <i :class="getServiceIcon(item.app)"></i>
          </div>
          <div class="event-info">
            <div class="app-name">{{ item.app }}</div>
            <div class="timestamp">{{ formatTimestamp(item.timestamp) }}</div>
            <div class="level" :style="{ color: getLevelColor(item.level) }">{{ item.level }}</div>
          </div>
        </div>
      </div>

      <!-- 应用列表 -->
      <div class="app-list">
        <div
          v-for="(app, index) in apps"
          :key="app"
          class="app-item"
          :class="{ active: activeApp === app }"
          @click="toggleApp(app)"
        >
          <i :class="getServiceIcon(app)"></i>
          <span>{{ app }}</span>
          <span class="count">({{ getAppCount(app) }})</span>
        </div>
      </div>

      <!-- 详细日志 -->
      <div class="log-details">
        <div
          v-for="(item, index) in filteredTimelineData"
          :key="index"
          class="log-item"
          :class="[item.level.toLowerCase()]"
        >
          <div class="log-header">
            <span class="log-timestamp">{{ formatTimestamp(item.timestamp) }}</span>
            <span class="log-app">{{ item.app }}</span>
            <span class="log-level" :style="{ color: getLevelColor(item.level) }">{{ item.level }}</span>
          </div>
          <div class="log-content" v-html="highlightXml(item.content)"></div>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <el-empty description="暂无时间线数据"></el-empty>
    </div>
  </div>
</template>

<script>
import { formatTimestamp, getLevelColor, highlightXml } from '@/utils/logParser'

export default {
  name: 'TimelineChart',
  props: {
    timelineData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      activeApps: [],
      showAll: true
    }
  },
  computed: {
    apps() {
      const appSet = new Set()
      this.timelineData.forEach(item => {
        appSet.add(item.app)
      })
      return Array.from(appSet)
    },
    filteredTimelineData() {
      if (this.activeApps.length === 0) {
        return this.timelineData
      }
      return this.timelineData.filter(item => this.activeApps.includes(item.app))
    },
    activeApp() {
      return this.activeApps.length > 0 ? this.activeApps[0] : null
    }
  },
  methods: {
    formatTimestamp,
    getLevelColor,
    highlightXml,

    getServiceIcon(appName) {
      // 根据应用名称返回相应的图标类
      const iconMap = {
        'sft-aipg': 'el-icon-position',
        'sft-trxqry': 'el-icon-search',
        'sft-pay': 'el-icon-wallet',
        'sft-batchpay': 'el-icon-files',
        'sft-contract': 'el-icon-document'
      }

      return iconMap[appName] || 'el-icon-monitor'
    },

    toggleApp(app) {
      const index = this.activeApps.indexOf(app)
      if (index > -1) {
        this.activeApps.splice(index, 1)
      } else {
        this.activeApps.push(app)
      }
    },

    getAppCount(app) {
      return this.timelineData.filter(item => item.app === app).length
    }
  },
  mounted() {
    // 默认选中所有应用
    this.activeApps = [...this.apps]
  }
}
</script>

<style scoped>
.timeline-chart {
  width: 100%;
  min-height: 500px;
}

.chart-container {
  position: relative;
  padding: 20px 0;
}

.timeline-axis {
  position: relative;
  height: 100px;
  margin-bottom: 40px;
  border-bottom: 2px solid #e4e7ed;
}

.timeline-item {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  text-align: center;
}

.event-point {
  width: 30px;
  height: 30px;
  border: 2px solid #409eff;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
  font-size: 14px;
}

.event-info {
  font-size: 12px;
  white-space: nowrap;
}

.app-name {
  font-weight: bold;
  color: #303133;
}

.timestamp {
  color: #909399;
}

.level {
  font-weight: bold;
}

.app-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.app-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  background-color: white;
  border: 1px solid #dcdfe6;
}

.app-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.app-item.active {
  border-color: #409eff;
  background-color: #409eff;
  color: white;
}

.count {
  opacity: 0.8;
}

.log-details {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.log-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.log-item:last-child {
  border-bottom: none;
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

.log-app {
  color: #409eff;
}

.log-level {
  font-weight: bold;
}

.log-content {
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #303133;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
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
</style>