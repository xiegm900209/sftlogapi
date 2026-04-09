<template>
  <div class="config-manager">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本配置" name="basic">
        <el-card>
          <template #header>
            <span>基本配置</span>
          </template>

          <el-form :model="basicConfig" label-width="150px">
            <el-form-item label="应用名称">
              <el-input v-model="basicConfig.appName"></el-input>
            </el-form-item>

            <el-form-item label="版本号">
              <el-input v-model="basicConfig.version"></el-input>
            </el-form-item>

            <el-form-item label="调试模式">
              <el-switch v-model="basicConfig.debug"></el-switch>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveBasicConfig">保存</el-button>
              <el-button @click="resetBasicConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="日志配置" name="logging">
        <el-card>
          <template #header>
            <span>日志配置</span>
          </template>

          <el-form :model="logConfig" label-width="150px">
            <el-form-item label="日志级别">
              <el-select v-model="logConfig.level">
                <el-option label="DEBUG" value="DEBUG"></el-option>
                <el-option label="INFO" value="INFO"></el-option>
                <el-option label="WARN" value="WARN"></el-option>
                <el-option label="ERROR" value="ERROR"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="日志保留天数">
              <el-input-number v-model="logConfig.retentionDays" :min="1" :max="365"></el-input-number>
            </el-form-item>

            <el-form-item label="最大文件大小(MB)">
              <el-input-number v-model="logConfig.maxFileSize" :min="1" :max="1024"></el-input-number>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveLogConfig">保存</el-button>
              <el-button @click="resetLogConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="交易类型配置" name="transactions">
        <el-card>
          <template #header>
            <span>交易类型配置</span>
            <el-button type="primary" size="small" @click="addTransactionType" style="float: right;">新增</el-button>
          </template>

          <el-table :data="transactionTypes" style="width: 100%;">
            <el-table-column prop="code" label="交易代码" width="120"></el-table-column>
            <el-table-column prop="name" label="交易名称"></el-table-column>
            <el-table-column prop="apps" label="关联应用">
              <template #default="{ row }">
                <el-tag
                  v-for="app in row.apps"
                  :key="app"
                  size="small"
                  style="margin-right: 5px;"
                >
                  {{ app }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row, $index }">
                <el-button size="small" @click="editTransactionType(row, $index)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTransactionType($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 编辑对话框 -->
          <el-dialog :visible.sync="editDialogVisible" :title="editingIndex === -1 ? '新增交易类型' : '编辑交易类型'">
            <el-form :model="currentTransactionType" label-width="100px">
              <el-form-item label="交易代码">
                <el-input v-model="currentTransactionType.code" :disabled="editingIndex !== -1"></el-input>
              </el-form-item>
              <el-form-item label="交易名称">
                <el-input v-model="currentTransactionType.name"></el-input>
              </el-form-item>
              <el-form-item label="关联应用">
                <el-select v-model="currentTransactionType.apps" multiple placeholder="请选择关联应用">
                  <el-option
                    v-for="service in availableServices"
                    :key="service"
                    :label="service"
                    :value="service">
                  </el-option>
                </el-select>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="editDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveTransactionType">保存</el-button>
            </template>
          </el-dialog>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
export default {
  name: 'ConfigManager',
  data() {
    return {
      activeTab: 'basic',
      basicConfig: {
        appName: 'Log Tracker',
        version: '1.0.0',
        debug: true
      },
      logConfig: {
        level: 'INFO',
        retentionDays: 30,
        maxFileSize: 100
      },
      transactionTypes: [
        { code: '310011', name: '协议支付', apps: ['sft-aipg', 'sft-trxqry', 'sft-pay'] },
        { code: '310016', name: '批量协议支付', apps: ['sft-aipg', 'sft-trxqry', 'sft-batchpay'] },
        { code: '310002', name: '协议支付签约', apps: ['sft-aipg', 'sft-contract'] },
        { code: '200004', name: '交易查询', apps: ['sft-aipg', 'sft-trxqry'] }
      ],
      editDialogVisible: false,
      currentTransactionType: { code: '', name: '', apps: [] },
      editingIndex: -1,
      availableServices: ['sft-aipg', 'sft-trxqry', 'sft-pay', 'sft-batchpay', 'sft-contract']
    }
  },
  methods: {
    saveBasicConfig() {
      console.log('保存基本配置:', this.basicConfig)
      this.$message.success('基本配置已保存')
    },

    resetBasicConfig() {
      this.basicConfig = {
        appName: 'Log Tracker',
        version: '1.0.0',
        debug: true
      }
    },

    saveLogConfig() {
      console.log('保存日志配置:', this.logConfig)
      this.$message.success('日志配置已保存')
    },

    resetLogConfig() {
      this.logConfig = {
        level: 'INFO',
        retentionDays: 30,
        maxFileSize: 100
      }
    },

    addTransactionType() {
      this.currentTransactionType = { code: '', name: '', apps: [] }
      this.editingIndex = -1
      this.editDialogVisible = true
    },

    editTransactionType(row, index) {
      this.currentTransactionType = { ...row }
      this.editingIndex = index
      this.editDialogVisible = true
    },

    deleteTransactionType(index) {
      this.transactionTypes.splice(index, 1)
      this.$message.success('交易类型已删除')
    },

    saveTransactionType() {
      if (this.editingIndex === -1) {
        // 新增
        this.transactionTypes.push({ ...this.currentTransactionType })
      } else {
        // 修改
        this.transactionTypes[this.editingIndex] = { ...this.currentTransactionType }
      }

      this.editDialogVisible = false
      this.$message.success('交易类型已保存')
    }
  }
}
</script>

<style scoped>
.config-manager {
  padding: 20px;
}
</style>