<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-content">
          <h1 class="logo">📊 交易日志链路追踪系统</h1>
          <el-menu
            mode="horizontal"
            :router="true"
            :default-active="activeMenu"
            class="nav-menu"
            background-color="#409EFF"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/log-query">日志追踪查询</el-menu-item>
            <el-menu-item index="/transaction-trace">交易类型追踪</el-menu-item>
            <el-sub-menu index="config-group">
              <template #title>配置管理</template>
              <el-menu-item index="/transaction-types">交易类型管理</el-menu-item>
              <el-menu-item index="/app-log-config">应用日志配置</el-menu-item>
              <el-menu-item index="/config">系统配置</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    activeMenu() {
      return this.$route.path
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

.main-container {
  height: 100%;
}

.main-header {
  background-color: #409EFF;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.nav-menu {
  border-bottom: none;
  background-color: #409EFF;
}

.nav-menu .el-menu-item {
  font-size: 14px;
}

.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  background-color: #66b1ff;
}

.main-content {
  background-color: #f0f2f5;
  padding: 0;
  overflow-y: auto;
}
</style>
