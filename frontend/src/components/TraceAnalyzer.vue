<template>
  <div class="trace-analyzer">
    <el-card>
      <template #header>
        <span>链路追踪分析器</span>
      </template>

      <el-form :model="traceParams" label-width="150px" inline>
        <el-form-item label="REQ_SN">
          <el-input v-model="traceParams.reqSn" placeholder="请输入REQ_SN" style="width: 200px;"></el-input>
        </el-form-item>

        <el-form-item label="交易类型">
          <el-select v-model="traceParams.transactionType" placeholder="请选择交易类型" style="width: 200px;">
            <el-option
              v-for="(type, code) in transactionTypes"
              :key="code"
              :label="`${code} - ${type.name}`"
              :value="code">
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="startTraceAnalysis">开始分析</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <el-divider></el-divider>

      <div v-if="analysisResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="REQ_SN">{{ analysisResult.req_sn }}</el-descriptions-item>
          <el-descriptions-item label="TraceID">{{ analysisResult.trace_id }}</el-descriptions-item>
          <el-descriptions-item label="交易类型">{{ getTransactionTypeName(analysisResult.transaction_type) }}</el-descriptions-item>
          <el-descriptions-item label="总耗时">{{ analysisResult.duration }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(analysisResult.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(analysisResult.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="日志总数">{{ analysisResult.total_logs }}</el-descriptions-item>
          <el-descriptions-item label="涉及应用">{{ analysisResult.apps_involved.join(', ') }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">各应用统计</el-divider>
        <el-table :data="getAppStatsTableData()" style="margin-bottom: 20px;">
          <el-table-column prop="app" label="应用"></el-table-column>
          <el-table-column prop="count" label="日志数量"></el-table-column>
          <el-table-column label="级别统计">
            <template #default="{ row }">
              <el-tag
                v-for="(count, level) in row.levels"
                :key="level"
                :type="getLevelTagType(level)"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ level }}: {{ count }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-divider content-position="left">业务信息</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="交易代码">
            <el-tag
              v-for="code in analysisResult.business_info.trx_codes"
              :key="code"
              type="info"
              style="margin-right: 5px;"
            >
              {{ code }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="返回码">
            <el-tag
              v-for="code in analysisResult.business_info.ret_codes"
              :key="code"
              style="margin-right: 5px;"
            >
              {{ code }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="错误信息">
            <el-tag
              v-for="error in analysisResult.business_info.errors"
              :key="error"
              type="danger"
              style="margin-right: 5px;"
            >
              {{ error }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">完整链路</el-divider>
        <TimelineChart :timeline-data="analysisResult.trace_data" />
      </div>

      <div v-else-if="isLoading" class="loading-state">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else class="empty-state">
        <el-empty description="请输入REQ_SN开始链路追踪分析"></el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import TimelineChart from '@/components/TimelineChart.vue'
import { traceTransaction } from '@/api/index'

export default {
  name: 'TraceAnalyzer',
  components: {
    TimelineChart
  },
  data() {
    return {
      traceParams: {
        reqSn: '',
        transactionType: ''
      },
      transactionTypes: {
        '310011': { name: '协议支付' },
        '310016': { name: '批量协议支付' },
        '310002': { name: '协议支付签约' },
        '200004': { name: '交易查询' }
      },
      analysisResult: null,
      isLoading: false
    }
  },
  methods: {
    async startTraceAnalysis() {
      if (!this.traceParams.reqSn) {
        this.$message.error('请输入REQ_SN')
        return
      }

      this.isLoading = true

      try {
        const response = await traceTransaction(
          this.traceParams.reqSn,
          this.traceParams.transactionType
        )

        if (response.data.success) {
          this.analysisResult = response.data.summary
          this.analysisResult.trace_data = response.data.trace_data
        } else {
          this.$message.error(response.data.error || '分析失败')
          this.analysisResult = null
        }
      } catch (error) {
        console.error('链路分析失败:', error)
        this.$message.error('链路分析失败: ' + error.message)
        this.analysisResult = null
      } finally {
        this.isLoading = false
      }
    },

    resetForm() {
      this.traceParams = {
        reqSn: '',
        transactionType: ''
      }
      this.analysisResult = null
    },

    getTransactionTypeName(typeCode) {
      if (!typeCode) return '未指定'
      return this.transactionTypes[typeCode]?.name || typeCode
    },

    getAppStatsTableData() {
      if (!this.analysisResult || !this.analysisResult.app_statistics) return []

      return Object.entries(this.analysisResult.app_statistics).map(([app, stats]) => ({
        app,
        count: stats.count,
        levels: stats.levels
      }))
    },

    getLevelTagType(level) {
      const levelTypes = {
        'ERROR': 'danger',
        'WARN': 'warning',
        'INFO': 'info',
        'DEBUG': 'success'
      }
      return levelTypes[level.toUpperCase()] || 'info'
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString()
    }
  }
}
</script>

<style scoped>
.trace-analyzer {
  padding: 20px;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}
</style>