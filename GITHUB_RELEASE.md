# GitHub 发布说明

## 🎉 项目已成功发布到 GitHub

**仓库地址**: https://github.com/xiegm900209/log-tracker

**版本**: v2.3.0  
**发布日期**: 2026-04-09

---

## 📦 发布内容

### 核心功能

1. **日志追踪查询** (`/log-query`)
   - REQ_SN 精准查询
   - 商户号过滤
   - 日志时间定位（YYYYMMDDHH 格式）
   - 自动 TraceID 提取
   - 多 TraceID 分组展示（重复查询场景）
   - CSV 导出
   - 多行日志解析（XML 报文）
   - 多编码支持（GBK/UTF-8）

2. **交易类型日志追踪** (`/transaction-trace`)
   - 交易类型选择（自动加载应用列表）
   - 入口应用提取 TraceID
   - 全链路追踪（所有关联应用）
   - 可视化链路图（步骤条展示）
   - 按应用分组查看
   - 多 TraceID 支持（折叠面板）
   - 压缩文件支持（.gz）
   - 时间范围扩展（前后 1 小时）

3. **配置管理**
   - 交易类型管理 (`/transaction-types`)
   - 应用日志配置 (`/app-log-config`)
   - 系统配置 (`/config`)

### 技术特性

- ✅ 多行日志解析（XML 报文完整解析）
- ✅ 多编码支持（GBK/GB18030/UTF-8 自动检测）
- ✅ Gzip 压缩文件直接读取
- ✅ 大文件流式处理（避免内存溢出）
- ✅ TraceID 索引加速
- ✅ 时间范围日志文件定位

---

## 📊 项目统计

- **代码行数**: 11,648 行
- **文件数量**: 53 个文件
- **文档数量**: 14 个 Markdown 文档
- **功能模块**: 5 个主要页面
- **API 接口**: 12 个 RESTful 接口

---

## 🏷️ Git 标签

- **v2.3.0** - 首发版本（当前）
- **main** - 主分支

---

## 📁 项目结构

```
log-tracker/
├── backend/                 # Flask 后端
│   ├── app_main.py          # 应用入口
│   ├── models/              # 数据模型
│   └── requirements.txt     # Python 依赖
├── frontend/                # Vue 前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── router/          # 路由配置
│   │   └── App.vue          # 根组件
│   └── package.json         # Node 依赖
├── config/                  # 配置文件
│   └── *.sample             # 配置示例
├── README.md                # 项目说明
├── CHANGELOG.md             # 更新日志
├── LICENSE                  # MIT 许可证
└── .gitignore               # Git 忽略文件
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:xiegm900209/log-tracker.git
cd log-tracker
```

### 2. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 3. 配置日志目录

编辑 `config/log_dirs.json`：

```json
{
  "sft-aipg": "/root/sft/testlogs/sft-aipg",
  "sft-trxqry": "/root/sft/testlogs/sft-trxqry"
}
```

### 4. 启动服务

```bash
# 后端
cd backend
python app_main.py

# 前端
cd frontend
npm run dev
```

### 5. 访问系统

- **开发环境**: http://localhost:3000
- **生产环境**: http://172.16.2.164:8083

---

## 📝 文档说明

| 文档 | 说明 |
|------|------|
| README.md | 项目主文档，包含安装、使用、API 说明 |
| CHANGELOG.md | 版本更新日志 |
| LICENSE | MIT 许可证 |
| *.md | 各功能模块详细说明文档 |

---

## 🎯 后续计划

### v2.4.0 (计划中)
- [ ] TraceID 对比功能
- [ ] 应用间时间差分析
- [ ] 导出完整链路报告
- [ ] 重复查询告警
- [ ] 异常检测（ERROR 日志标记）

### v2.5.0 (规划中)
- [ ] 用户认证系统
- [ ] 查询历史记录
- [ ] 收藏常用查询
- [ ] 仪表盘统计
- [ ] 告警通知

---

## 📞 联系方式

- **作者**: xiegm900209
- **GitHub**: https://github.com/xiegm900209
- **Issues**: https://github.com/xiegm900209/log-tracker/issues

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

<div align="center">

**Made with ❤️ by Log Tracker Team**

[查看项目](https://github.com/xiegm900209/log-tracker) | [报告问题](https://github.com/xiegm900209/log-tracker/issues)

</div>
