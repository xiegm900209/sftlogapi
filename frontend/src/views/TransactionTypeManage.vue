<template>
  <div class="transaction-type-manage">
    <el-page-header @back="$router.go(-1)" content="交易类型管理"></el-page-header>

    <el-card class="manage-card">
      <template #header>
        <div class="card-header">
          <span>交易类型列表</span>
          <div class="header-actions">
            <el-button @click="exportTransactionTypes">
              <el-icon><Download /></el-icon>
              导出全部
            </el-button>
            <el-button type="primary" @click="openAddDialog">
              <el-icon><Plus /></el-icon>
              新增交易类型
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="transactionTypesList" style="width: 100%" border stripe>
        <el-table-column prop="code" label="交易代码" width="150" sortable></el-table-column>
        <el-table-column prop="name" label="交易名称" width="200"></el-table-column>
        <el-table-column label="关联应用" min-width="300">
          <template #default="{ row }">
            <div class="app-tags">
              <el-tag
                v-for="app in row.apps"
                :key="app"
                size="small"
                type="info"
                class="app-tag"
              >
                {{ app }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="应用数量" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.apps.length > 0 ? 'success' : 'warning'">
              {{ row.apps.length }} 个
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row, $index }">
            <el-button size="small" @click="openEditDialog(row, $index)">编辑</el-button>
            <el-button size="small" type="success" @click="cloneTransactionType(row, $index)">复制</el-button>
            <el-popconfirm 
              title="确认删除该交易类型吗？" 
              @confirm="deleteTransactionType($index)"
              width="200"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑交易类型' : '新增交易类型'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="交易代码" prop="code">
          <el-input 
            v-model="formData.code" 
            placeholder="例如：310011"
            :disabled="isEdit"
            maxlength="20"
          ></el-input>
          <div class="form-tip">交易代码在保存后不可修改</div>
        </el-form-item>

        <el-form-item label="交易名称" prop="name">
          <el-input 
            v-model="formData.name" 
            placeholder="例如：协议支付"
            maxlength="100"
          ></el-input>
        </el-form-item>

        <el-form-item label="关联应用" prop="apps">
          <el-select 
            v-model="formData.apps" 
            multiple 
            placeholder="请选择关联应用"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="service in availableServices"
              :key="service"
              :label="service"
              :value="service"
            ></el-option>
          </el-select>
          <div class="form-tip">可多选，按住 Ctrl 选择多个应用</div>
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
import { Plus, Download, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'TransactionTypeManage',
  components: {
    Plus,
    Download,
    CopyDocument
  },
  data() {
    return {
      transactionTypesList: [],
      availableServices: [],
      dialogVisible: false,
      isEdit: false,
      editIndex: -1,
      saving: false,
      formData: {
        code: '',
        name: '',
        apps: []
      },
      formRules: {
        code: [
          { required: true, message: '请输入交易代码', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '交易代码只能包含字母、数字和下划线', trigger: 'blur' }
        ],
        name: [
          { required: true, message: '请输入交易名称', trigger: 'blur' }
        ],
        apps: [
          { type: 'array', min: 1, message: '请至少选择一个关联应用', trigger: 'change' }
        ]
      }
    }
  },
  mounted() {
    this.loadTransactionTypes()
    this.loadAvailableServices()
  },
  methods: {
    async loadTransactionTypes() {
      try {
        const response = await axios.get('/api/transaction-types')
        if (response.data.success) {
          const types = response.data.transaction_types
          this.transactionTypesList = Object.keys(types).map(key => ({
            code: key,
            name: types[key].name,
            apps: types[key].apps || []
          }))
        }
      } catch (error) {
        console.error('加载交易类型失败:', error)
        this.$message.error('加载交易类型失败')
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

    openAddDialog() {
      this.isEdit = false
      this.editIndex = -1
      this.formData = { code: '', name: '', apps: [] }
      this.dialogVisible = true
    },

    openEditDialog(row, index) {
      this.isEdit = true
      this.editIndex = index
      this.formData = {
        code: row.code,
        name: row.name,
        apps: [...row.apps]
      }
      this.dialogVisible = true
    },

    resetForm() {
      if (this.$refs.formRef) {
        this.$refs.formRef.resetFields()
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
        const transactionTypes = {}
        this.transactionTypesList.forEach(item => {
          transactionTypes[item.code] = {
            name: item.name,
            apps: item.apps
          }
        })

        if (!this.isEdit) {
          if (transactionTypes[this.formData.code]) {
            this.$message.error('交易代码已存在')
            this.saving = false
            return
          }
          transactionTypes[this.formData.code] = {
            name: this.formData.name,
            apps: this.formData.apps
          }
        } else {
          transactionTypes[this.formData.code] = {
            name: this.formData.name,
            apps: this.formData.apps
          }
        }

        const response = await axios.post('/api/config/transaction-types', transactionTypes)
        
        if (response.data.success) {
          this.$message.success(this.isEdit ? '更新成功' : '新增成功')
          this.dialogVisible = false
          await this.loadTransactionTypes()
        } else {
          this.$message.error(response.data.message || '保存失败')
        }
      } catch (error) {
        console.error('保存失败:', error)
        this.$message.error('保存失败：' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    },

    async deleteTransactionType(index) {
      const row = this.transactionTypesList[index]
      
      try {
        const transactionTypes = {}
        this.transactionTypesList.forEach((item, i) => {
          if (i !== index) {
            transactionTypes[item.code] = {
              name: item.name,
              apps: item.apps
            }
          }
        })

        const response = await axios.post('/api/config/transaction-types', transactionTypes)
        
        if (response.data.success) {
          this.$message.success('删除成功')
          await this.loadTransactionTypes()
        } else {
          this.$message.error(response.data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除失败:', error)
        this.$message.error('删除失败：' + error.message)
      }
    },

    /**
     * 复制交易类型 - 基于现有配置创建新条目
     */
    cloneTransactionType(row, index) {
      this.isEdit = false
      this.editIndex = -1
      // 复制数据，交易代码添加 _copy 后缀
      this.formData = {
        code: row.code + '_copy',
        name: row.name + ' (副本)',
        apps: [...row.apps]
      }
      this.dialogVisible = true
      this.$message.success('已复制交易类型，请修改交易代码和名称')
    },

    /**
     * 导出交易类型列表为 JSON 文件
     */
    async exportTransactionTypes() {
      if (this.transactionTypesList.length === 0) {
        this.$message.warning('没有可导出的数据')
        return
      }

      try {
        // 构建导出数据结构
        const exportData = {
          export_time: new Date().toISOString(),
          total: this.transactionTypesList.length,
          transaction_types: {}
        }

        this.transactionTypesList.forEach(item => {
          exportData.transaction_types[item.code] = {
            name: item.name,
            apps: item.apps
          }
        })

        // 创建 JSON 文件并下载
        const jsonStr = JSON.stringify(exportData, null, 2)
        const blob = new Blob(['\ufeff' + jsonStr], { type: 'application/json;charset=utf-8' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
        link.download = `transaction-types-${timestamp}.json`
        link.click()
        
        this.$message.success(`已导出 ${this.transactionTypesList.length} 条交易类型配置`)
      } catch (error) {
        console.error('导出失败:', error)
        this.$message.error('导出失败：' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.transaction-type-manage {
  padding: 20px;
}

.manage-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.app-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.app-tag {
  margin: 2px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
