import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import LogQuery from '@/views/LogQuery.vue'
import TransactionTypeManage from '@/views/TransactionTypeManage.vue'
import AppLogConfig from '@/views/AppLogConfig.vue'
import TransactionTrace from '@/views/TransactionTrace.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/log-query',
    name: 'LogQuery',
    component: LogQuery,
    meta: { title: '日志追踪查询' }
  },
  {
    path: '/transaction-trace',
    name: 'TransactionTrace',
    component: TransactionTrace,
    meta: { title: '交易类型日志追踪' }
  },
  {
    path: '/transaction-types',
    name: 'TransactionTypeManage',
    component: TransactionTypeManage,
    meta: { title: '交易类型管理' }
  },
  {
    path: '/app-log-config',
    name: 'AppLogConfig',
    component: AppLogConfig,
    meta: { title: '应用日志配置' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
