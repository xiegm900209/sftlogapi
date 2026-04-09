<template>
  <div class="config">
    <el-page-header @back="$router.go(-1)" content="系统配置"></el-page-header>

    <el-tabs v-model="activeTab" class="config-tabs">
      <el-tab-pane label="应用配置" name="app">
        <el-card>
          <template #header>
            <span>应用配置</span>
          </template>

          <el-form :model="appConfig" label-width="150px" style="max-width: 600px;">
            <el-form-item label="应用名称">
              <el-input v-model="appConfig.app_name"></el-input>
            </el-form-item>

            <el-form-item label="版本号">
              <el-input v-model="appConfig.version"></el-input>
            </el-form-item>

            <el-form-item label="调试模式">
              <el-switch v-model="appConfig.debug"></el-switch>
            </el-form-item>

            <el-form-item label="日志级别">
              <el-select v-model="appConfig.log_level">
                <el-option label="DEBUG" value="DEBUG"></el-option>
                <el-option label="INFO" value="INFO"></el-option>
                <el-option label="WARN" value="WARN"></el-option>
                <el-option label="ERROR" value="ERROR"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="最大文件大小(MB)">
              <el-input-number v-model="appConfig.max_file_size" :min="1" :max="10240"></el-input-number>
            </el-form-item>

            <el-form-item label="索引更新间隔(秒)">
              <el-input-number v-model="appConfig.index_update_interval" :min="60" :max="3600"></el-input-number>
            </el-form-item>

            <el-form-item label="最大搜索结果数">
              <el-input-number v-model="appConfig.max_search_results" :min="10" :max="10000"></el-input-number>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveAppConfig">保存配置</el-button>
              <el-button @click="resetAppConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="交易类型配置" name="transaction">
        <el-card>
          <template #header>
            <span>交易类型配置</span>
            <el-button type="primary" size="small" @click="addTransactionType" style="float: right;">新增</el-button>
          </template>

          <el-table :data="transactionTypesList" style="width: 100%; margin-bottom: 20px;">
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
                <el-popconfirm title="确认删除吗？" @confirm="deleteTransactionType($index)">
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>

          <el-dialog :visible.sync="transactionDialogVisible" title="编辑交易类型">
            <el-form :model="currentTransactionType" label-width="100px">
              <el-form-item label="交易代码">
                <el-input v-model="currentTransactionType.code" :disabled="!!currentTransactionTypeIndex"></el-input>
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
              <el-button @click="transactionDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="saveTransactionType">保存</el-button>
            </template>
          </el-dialog>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="日志目录配置" name="logdirs">
        <el-card>
          <template #header>
            <span>日志目录配置</span>
          </template>

          <el-form :model="logDirsConfig" label-width="150px">
            <el-form-item
              v-for="(path, service) in logDirsConfig"
              :key="service"
              :label="`${service}日志路径`"
            >
              <el-input v-model="logDirsConfig[service]" placeholder="请输入日志目录路径"></el-input>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveLogDirsConfig">保存配置</el-button>
              <el-button @click="resetLogDirsConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Config',
  data() {
    return {
      activeTab: 'app',
      appConfig: {},
      transactionTypes: {},
      transactionTypesList: [],
      logDirsConfig: {},

      // 交易类型编辑相关
      transactionDialogVisible: false,
      currentTransactionType: { code: '', name: '', apps: [] },
      currentTransactionTypeIndex: -1,
      availableServices: []
    }
  },
  mounted() {
    this.loadConfigs();
  },
  methods: {
    async loadConfigs() {
      await this.loadAppConfig();
      await this.loadTransactionTypes();
      await this.loadLogDirsConfig();
      await this.loadAvailableServices();
    },

    async loadAppConfig() {
      try {
        const response = await axios.get('/config/get-app-config');
        if (response.data.success) {
          this.appConfig = response.data.config;
        }
      } catch (error) {
        console.error('加载应用配置失败:', error);
      }
    },

    async loadTransactionTypes() {
      try {
        const response = await axios.get('/config/get-transaction-types');
        if (response.data.success) {
          this.transactionTypes = response.data.transaction_types;
          this.transactionTypesList = Object.keys(response.data.transaction_types).map(key => ({
            code: key,
            ...response.data.transaction_types[key]
          }));
        }
      } catch (error) {
        console.error('加载交易类型配置失败:', error);
      }
    },

    async loadLogDirsConfig() {
      try {
        const response = await axios.get('/config/get-log-dirs');
        if (response.data.success) {
          this.logDirsConfig = response.data.log_dirs;
        }
      } catch (error) {
        console.error('加载日志目录配置失败:', error);
      }
    },

    async loadAvailableServices() {
      try {
        const response = await axios.get('/config/get-available-services');
        if (response.data.success) {
          this.availableServices = response.data.services;
        }
      } catch (error) {
        console.error('加载可用服务失败:', error);
      }
    },

    async saveAppConfig() {
      try {
        const response = await axios.post('/config/update-app-config', this.appConfig);
        if (response.data.success) {
          this.$message.success('应用配置已保存');
        }
      } catch (error) {
        console.error('保存应用配置失败:', error);
        this.$message.error('保存应用配置失败: ' + error.message);
      }
    },

    async saveLogDirsConfig() {
      try {
        // 先验证配置
        const validationResponse = await axios.post('/config/validate-config', {
          log_dirs: this.logDirsConfig
        });

        if (!validationResponse.data.success) {
          this.$message.error('配置验证失败: ' + validationResponse.data.errors.join(', '));
          return;
        }

        const response = await axios.post('/config/update-log-dirs', this.logDirsConfig);
        if (response.data.success) {
          this.$message.success('日志目录配置已保存');
        }
      } catch (error) {
        console.error('保存日志目录配置失败:', error);
        this.$message.error('保存日志目录配置失败: ' + error.message);
      }
    },

    resetAppConfig() {
      this.loadAppConfig();
    },

    resetLogDirsConfig() {
      this.loadLogDirsConfig();
    },

    addTransactionType() {
      this.currentTransactionType = { code: '', name: '', apps: [] };
      this.currentTransactionTypeIndex = -1;
      this.transactionDialogVisible = true;
    },

    editTransactionType(row, index) {
      this.currentTransactionType = { ...row };
      this.currentTransactionTypeIndex = index;
      this.transactionDialogVisible = true;
    },

    deleteTransactionType(index) {
      this.transactionTypesList.splice(index, 1);
      this.updateTransactionTypesFromList();
      this.saveTransactionTypesToServer();
    },

    saveTransactionType() {
      if (!this.currentTransactionType.code || !this.currentTransactionType.name) {
        this.$message.error('交易代码和名称不能为空');
        return;
      }

      if (this.currentTransactionTypeIndex === -1) {
        // 新增
        this.transactionTypesList.push({ ...this.currentTransactionType });
      } else {
        // 编辑
        this.transactionTypesList[this.currentTransactionTypeIndex] = { ...this.currentTransactionType };
      }

      this.updateTransactionTypesFromList();
      this.saveTransactionTypesToServer();

      this.transactionDialogVisible = false;
    },

    updateTransactionTypesFromList() {
      this.transactionTypes = {};
      this.transactionTypesList.forEach(item => {
        this.transactionTypes[item.code] = {
          name: item.name,
          apps: item.apps
        };
      });
    },

    async saveTransactionTypesToServer() {
      try {
        const response = await axios.post('/config/update-transaction-types', this.transactionTypes);
        if (response.data.success) {
          this.$message.success('交易类型配置已保存');
          // 重新加载以确保状态一致
          this.loadTransactionTypes();
        }
      } catch (error) {
        console.error('保存交易类型配置失败:', error);
        this.$message.error('保存交易类型配置失败: ' + error.message);
      }
    }
  }
}
</script>

<style scoped>
.config {
  padding: 20px;
}

.config-tabs {
  margin-top: 20px;
}
</style>