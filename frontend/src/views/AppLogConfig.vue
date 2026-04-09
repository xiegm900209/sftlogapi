<template>
  <div class="app-log-config">
    <el-page-header @back="$router.go(-1)" content="应用日志目录配置"></el-page-header>

    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>应用日志目录配置</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            新增应用配置
          </el-button>
        </div>
      </template>

      <el-alert
        title="配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>配置每个交易应用的日志文件存放目录，系统将从这些目录读取日志文件进行分析。</p>
        <p>支持绝对路径和相对路径，请确保 nginx worker 用户有读取权限。</p>
      </el-alert>

      <el-table :data="configList" style="width: 100%" border stripe>
        <el-table-column prop="service" label="应用名称" width="200" sortable></el-table-column>
        <el-table-column prop="path" label="日志目录路径" min-width="400">
          <template #default="{ row }">
            <div class="path-cell">
              <span class="path-text">{{ row.path }}</span>
              <el-tag 
                :type="row.exists ? 'success' : 'danger'" 
                size="small"
                class="status-tag"
              >
                {{ row.exists ? '存在' : '不存在' }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }">
            <el-button size="small" @click="openEditDialog(row, $index)">编辑</el-button>
            <el-popconfirm 
              title="确认删除该应用配置吗？" 
              @confirm="deleteConfig($index)"
              width="200"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="save-section">
        <el-button type="primary" @click="saveAllConfig" :loading="saving">保存全部配置</el-button>
        <el-button @click="loadConfig">重置</el-button>
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑应用配置' : '新增应用配置'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="应用名称" prop="service">
          <el-select 
            v-model="formData.service" 
            placeholder="请选择应用"
            :disabled="isEdit"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="service in availableServices"
              :key="service"
              :label="service"
              :value="service"
              :disabled="isServiceUsed(service)"
            ></el-option>
          </el-select>
          <div class="form-tip">应用名称在保存后不可修改</div>
        </el-form-item>

        <el-form-item label="日志目录" prop="path">
          <el-input 
            v-model="formData.path" 
            placeholder="例如：/root/sft/testlogs/sft-aipg"
            maxlength="500"
          >
            <template #append>
              <el-button @click="testPath">测试路径</el-button>
            </template>
          </el-input>
          <div class="form-tip">支持绝对路径或相对路径，请确保有读取权限</div>
        </el-form-item>

        <el-form-item label="路径状态">
          <el-tag :type="pathStatus.type" size="large">
            {{ pathStatus.text }}
          </el-tag>
          <span v-if="pathStatus.detail" class="path-detail">{{ pathStatus.detail }}</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveForm" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'AppLogConfig',
  components: {
    Plus
  },
  data() {
    return {
      configList: [],
      availableServices: [],
      dialogVisible: false,
      isEdit: false,
      editIndex: -1,
      saving: false,
      formData: {
        service: '',
        path: ''
      },
      formRules: {
        service: [
          { required: true, message: '请选择应用名称', trigger: 'change' }
        ],
        path: [
          { required: true, message: '请输入日志目录路径', trigger: 'blur' },
          { pattern: /^\/|^[a-zA-Z]:/, message: '请使用绝对路径', trigger: 'blur' }
        ]
      },
      pathStatus: {
        type: 'info',
        text: '未测试',
        detail: ''
      }
    }
  },
  mounted() {
    this.loadConfig()
    this.loadAvailableServices()
  },
  methods: {
    async loadConfig() {
      try {
        const response = await axios.get('/api/config/log-dirs')
        if (response.data.success) {
          const logDirs = response.data.log_dirs
          this.configList = Object.keys(logDirs).map(key => ({
            service: key,
            path: logDirs[key],
            exists: true // 假设存在，实际应由后端验证
          }))
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        this.$message.error('加载配置失败')
      }
    },

    async loadAvailableServices() {
      try {
        const response = await axios.get('/api/services')
        if (response.data.success) {
          this.availableServices = response.data.services.sort()
        }
      } catch (error) {
        console.error('加载服务列表失败:', error)
      }
    },

    isServiceUsed(service) {
      if (!this.isEdit) {
        return this.configList.some(item => item.service === service)
      }
      return this.configList.some((item, index) => 
        item.service === service && index !== this.editIndex
      )
    },

    openAddDialog() {
      this.isEdit = false
      this.editIndex = -1
      this.formData = { service: '', path: '' }
      this.pathStatus = { type: 'info', text: '未测试', detail: '' }
      this.dialogVisible = true
    },

    openEditDialog(row, index) {
      this.isEdit = true
      this.editIndex = index
      this.formData = {
        service: row.service,
        path: row.path
      }
      this.pathStatus = {
        type: row.exists ? 'success' : 'danger',
        text: row.exists ? '路径存在' : '路径不存在',
        detail: ''
      }
      this.dialogVisible = true
    },

    resetForm() {
      if (this.$refs.formRef) {
        this.$refs.formRef.resetFields()
      }
      this.pathStatus = { type: 'info', text: '未测试', detail: '' }
    },

    async testPath() {
      if (!this.formData.path) {
        this.$message.warning('请先输入路径')
        return
      }

      try {
        const response = await axios.post('/api/config/validate-path', {
          path: this.formData.path
        })
        
        if (response.data.success) {
          this.pathStatus = {
            type: 'success',
            text: '路径存在',
            detail: response.data.detail || ''
          }
          this.$message.success('路径验证通过')
        } else {
          this.pathStatus = {
            type: 'danger',
            text: '路径不存在',
            detail: response.data.message || ''
          }
          this.$message.warning('路径不存在或无权限访问')
        }
      } catch (error) {
        this.pathStatus = {
          type: 'danger',
          text: '验证失败',
          detail: error.message
        }
        this.$message.error('路径验证失败')
      }
    },

    async saveForm() {
      if (!this.$refs.formRef) return

      try {
        await this.$refs.formRef.validate()
      } catch (error) {
        return
      }

      this.saving = true

      try {
        const logDirs = {}
        this.configList.forEach(item => {
          logDirs[item.service] = item.path
        })

        if (!this.isEdit) {
          logDirs[this.formData.service] = this.formData.path
        } else {
          const oldService = this.configList[this.editIndex].service
          delete logDirs[oldService]
          logDirs[this.formData.service] = this.formData.path
        }

        const response = await axios.post('/api/config/log-dirs', logDirs)
        
        if (response.data.success) {
          this.$message.success(this.isEdit ? '更新成功' : '新增成功')
          this.dialogVisible = false
          await this.loadConfig()
        } else {
          this.$message.error(response.data.message || '保存失败')
        }
      } catch (error) {
        console.error('保存失败:', error)
        this.$message.error('保存失败：' + error.message)
      } finally {
        this.saving = false
      }
    },

    async deleteConfig(index) {
      this.configList.splice(index, 1)
      await this.saveAllConfig()
    },

    async saveAllConfig() {
      this.saving = true

      try {
        const logDirs = {}
        this.configList.forEach(item => {
          logDirs[item.service] = item.path
        })

        const response = await axios.post('/api/config/log-dirs', logDirs)
        
        if (response.data.success) {
          this.$message.success('配置保存成功')
          await this.loadConfig()
        } else {
          this.$message.error(response.data.message || '保存失败')
        }
      } catch (error) {
        console.error('保存失败:', error)
        this.$message.error('保存失败：' + error.message)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.app-log-config {
  padding: 20px;
}

.config-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.path-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.path-text {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.status-tag {
  flex-shrink: 0;
}

.save-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.path-detail {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
}
</style>
