<template>
  <div class="home">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1 class="welcome-title">📊 交易日志链路追踪系统</h1>
      <p class="welcome-subtitle">Log Tracker - 帮助开发和运维团队快速定位分布式系统中的交易流转问题</p>
      <div class="welcome-actions">
        <el-button type="primary" size="large" @click="$router.push('/log-query')">开始查询</el-button>
        <el-button size="large" @click="$router.push('/transaction-trace')">交易追踪</el-button>
      </div>
    </div>

    <!-- 核心功能模块 -->
    <div class="features-section">
      <h2 class="section-title">核心功能模块</h2>
      
      <div class="features-grid">
        <!-- 功能 1: 日志追踪查询 -->
        <el-card class="feature-card feature-primary" shadow="hover">
          <div class="feature-header">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">日志追踪查询</h3>
          </div>
          <p class="feature-desc">
            通过 REQ_SN、商户号、日志时间组合查询交易链路。
            系统自动提取 TraceID，展示完整的交易流转过程。
          </p>
          <el-divider></el-divider>
          <div class="feature-details">
            <h4>主要特性：</h4>
            <ul class="feature-list">
              <li>✓ <strong>REQ_SN 精准查询</strong> - 通过交易序列号定位具体交易</li>
              <li>✓ <strong>商户号过滤</strong> - 按商户号筛选相关交易</li>
              <li>✓ <strong>日志时间定位</strong> - 支持 YYYYMMDDHH 格式快速定位日志文件</li>
              <li>✓ <strong>自动 TraceID 提取</strong> - 智能识别交易链路标识</li>
              <li>✓ <strong>多 TraceID 分组</strong> - 自动识别重复查询场景</li>
              <li>✓ <strong>CSV 导出</strong> - 支持查询结果导出</li>
              <li>✓ <strong>多行日志解析</strong> - 完整解析 XML 报文等多行日志</li>
              <li>✓ <strong>多编码支持</strong> - GBK/UTF-8 自动检测</li>
            </ul>
          </div>
          <el-button type="primary" class="feature-btn" @click="$router.push('/log-query')">进入查询</el-button>
        </el-card>

        <!-- 功能 2: 交易类型日志追踪 -->
        <el-card class="feature-card feature-primary" shadow="hover">
          <div class="feature-header">
            <div class="feature-icon">🔗</div>
            <h3 class="feature-title">交易类型日志追踪</h3>
          </div>
          <p class="feature-desc">
            根据交易类型配置的关联应用，依次展示完整交易链路。
            从入口应用开始，自动追踪所有关联应用的日志。
          </p>
          <el-divider></el-divider>
          <div class="feature-details">
            <h4>主要特性：</h4>
            <ul class="feature-list">
              <li>✓ <strong>交易类型选择</strong> - 自动加载配置的应用列表</li>
              <li>✓ <strong>入口应用提取</strong> - 从第一个应用提取 TraceID</li>
              <li>✓ <strong>全链路追踪</strong> - 依次查询所有关联应用</li>
              <li>✓ <strong>可视化链路图</strong> - 步骤条展示应用流转</li>
              <li>✓ <strong>按应用分组</strong> - Tab 切换查看各应用日志</li>
              <li>✓ <strong>多 TraceID 支持</strong> - 折叠面板展示重复查询</li>
              <li>✓ <strong>压缩文件支持</strong> - 直接读取 .gz 压缩日志</li>
              <li>✓ <strong>时间范围扩展</strong> - 自动查询前后 1 小时日志</li>
            </ul>
          </div>
          <el-button type="primary" class="feature-btn" @click="$router.push('/transaction-trace')">开始追踪</el-button>
        </el-card>

        <!-- 功能 3: 配置管理 -->
        <el-card class="feature-card" shadow="hover">
          <div class="feature-header">
            <div class="feature-icon">⚙️</div>
            <h3 class="feature-title">配置管理</h3>
          </div>
          <p class="feature-desc">
            管理系统配置，包括交易类型、应用日志目录等。
          </p>
          <el-divider></el-divider>
          <div class="feature-details">
            <el-collapse class="feature-collapse">
              <el-collapse-item title="交易类型管理" name="1">
                <p class="sub-desc">配置交易类型及其关联的应用模块</p>
                <ul class="feature-list">
                  <li>✓ 新增/编辑/删除交易类型</li>
                  <li>✓ 配置交易代码和名称</li>
                  <li>✓ 关联多个应用</li>
                  <li>✓ 实时保存到配置文件</li>
                </ul>
                <el-button type="primary" size="small" @click.stop="$router.push('/transaction-types')">管理交易类型</el-button>
              </el-collapse-item>
              
              <el-collapse-item title="应用日志配置" name="2">
                <p class="sub-desc">配置每个交易应用的日志目录路径</p>
                <ul class="feature-list">
                  <li>✓ 新增/编辑/删除应用配置</li>
                  <li>✓ 路径验证功能</li>
                  <li>✓ 实时检测路径状态</li>
                  <li>✓ 支持 34+ 个应用配置</li>
                </ul>
                <el-button type="primary" size="small" @click.stop="$router.push('/app-log-config')">管理日志配置</el-button>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>

        <!-- 功能 4: AI API 能力 -->
        <el-card class="feature-card feature-ai" shadow="hover">
          <div class="feature-header">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">AI API 能力</h3>
          </div>
          <p class="feature-desc">
            为智多星等 AI 系统提供自然语言查询接口，支持完整日志返回和智能分析。
          </p>
          <el-divider></el-divider>
          <div class="feature-details">
            <h4>核心能力：</h4>
            <ul class="feature-list">
              <li>✓ <strong>自然语言查询</strong> - 支持中文自然语言解析</li>
              <li>✓ <strong>自动 TraceID 提取</strong> - 从 REQ_SN 自动提取 TraceID</li>
              <li>✓ <strong>全链路日志</strong> - 返回完整日志（无截断）</li>
              <li>✓ <strong>多服务追踪</strong> - 自动查询所有关联服务</li>
              <li>✓ <strong>智能分析</strong> - 交易状态判断、异常检测</li>
              <li>✓ <strong>知识库集成</strong> - 交易类型、服务描述知识库</li>
              <li>✓ <strong>API Key 鉴权</strong> - 安全的访问控制</li>
              <li>✓ <strong>速率限制</strong> - 100 次/分钟（生产环境）</li>
            </ul>
            
            <el-alert
              title="智多星集成示例"
              type="info"
              :closable="false"
              show-icon
              class="ai-example"
            >
              <div class="example-content">
                <p><strong>用户输入：</strong></p>
                <code class="example-code">"帮我看下 310011 交易的日志，REQ_SN=LX...，时间 2026040809"</code>
                <p style="margin-top: 10px;"><strong>AI 调用：</strong></p>
                <code class="example-code">POST /api/ai/query</code>
                <p style="margin-top: 10px;"><strong>返回：</strong></p>
                <code class="example-code">93 条完整日志 + 智能分析结果</code>
              </div>
            </el-alert>
            
            <div class="api-links">
              <el-button size="small" @click.stop="$router.push('/api/ai/health')">健康检查</el-button>
              <el-tag type="success" size="small" style="margin-left: 10px;">API v1.0</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 技术特性 -->
    <div class="tech-section">
      <h2 class="section-title">技术特性</h2>
      <div class="tech-grid">
        <div class="tech-item">
          <div class="tech-icon">📄</div>
          <h4>多行日志解析</h4>
          <p>完整解析 XML 报文等多行日志，以时间戳开头作为新日志的开始</p>
        </div>
        <div class="tech-item">
          <div class="tech-icon">🔤</div>
          <h4>多编码支持</h4>
          <p>自动检测 GBK、GB18030、UTF-8 编码，中文显示无乱码</p>
        </div>
        <div class="tech-item">
          <div class="tech-icon">🗜️</div>
          <h4>压缩文件支持</h4>
          <p>直接读取 .gz 压缩日志文件，无需解压，节省 8 倍时间</p>
        </div>
        <div class="tech-item">
          <div class="tech-icon">🔍</div>
          <h4>智能 TraceID 提取</h4>
          <p>从日志格式第 3 个参数自动提取 TraceID，支持重复查询识别</p>
        </div>
        <div class="tech-item">
          <div class="tech-icon">⚡</div>
          <h4>大文件流式处理</h4>
          <p>使用生成器逐块读取，避免内存溢出，支持 GB 级日志文件</p>
        </div>
        <div class="tech-item">
          <div class="tech-icon">🎯</div>
          <h4>时间范围定位</h4>
          <p>根据日志文件名中的时间戳快速定位，自动扩展前后 1 小时</p>
        </div>
      </div>
    </div>

    <!-- 快速开始 -->
    <div class="quick-start-section">
      <h2 class="section-title">快速开始</h2>
      <el-steps :active="1" align-center finish-status="success" class="quick-steps">
        <el-step 
          title="选择查询方式" 
          description="日志追踪查询（单应用）或 交易类型追踪（多应用）"
        ></el-step>
        <el-step 
          title="输入查询条件" 
          description="输入 REQ_SN、商户号或选择日志时间"
        ></el-step>
        <el-step 
          title="自动提取 TraceID" 
          description="系统自动识别交易链路标识"
        ></el-step>
        <el-step 
          title="查看完整链路" 
          description="展示所有相关日志，支持导出"
        ></el-step>
      </el-steps>
      
      <div class="start-btn-wrapper">
        <el-button type="primary" size="large" @click="$router.push('/log-query')" class="start-btn">
          开始查询日志
        </el-button>
        <el-button size="large" @click="$router.push('/transaction-trace')" class="start-btn">
          追踪交易链路
        </el-button>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="info-section">
      <el-alert
        title="使用说明"
        type="info"
        :closable="false"
        show-icon
        class="info-alert"
      >
        <div class="info-content">
          <p><strong>📝 日志时间格式</strong>：输入 10 位数字，格式为 <code>YYYYMMDDHH</code>（如：2026040809 表示 2026 年 4 月 8 日 9 时）<strong>（必填，防止系统过载）</strong></p>
          <p><strong>🔖 TraceID 提取</strong>：系统从日志格式的第 3 个参数提取 TraceID，格式为 <code>[时间][线程][TraceID][级别]...</code></p>
          <p><strong>🔄 重复查询识别</strong>：同一个 REQ_SN 可能对应多个 TraceID（重复查询场景），系统会自动分组展示</p>
          <p><strong>📄 多行日志支持</strong>：以时间戳开头作为新日志的开始，中间所有内容都属于同一行日志</p>
          <p><strong>🗜️ 压缩文件支持</strong>：自动识别并读取 .gz 压缩日志文件，无需手动解压</p>
        </div>
      </el-alert>
    </div>

    <!-- 页脚 -->
    <div class="footer-section">
      <div class="footer-content">
        <p>sftlogapi - 交易日志链路追踪系统 v1.0.0</p>
        <p>帮助开发和运维团队快速定位分布式系统中的交易流转问题</p>
        <div class="footer-links">
          <span>技术栈：</span>
          <el-tag size="small">Vue 3</el-tag>
          <el-tag size="small">Vite</el-tag>
          <el-tag size="small">Element Plus</el-tag>
          <el-tag size="small">Flask</el-tag>
          <el-tag size="small">Python 3.9</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
}

.welcome-title {
  font-size: 36px;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.welcome-subtitle {
  font-size: 18px;
  opacity: 0.95;
  margin: 0 0 30px 0;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.welcome-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.welcome-actions .el-button {
  padding: 15px 40px;
  font-size: 16px;
}

/* 功能区域 */
.features-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 28px;
  margin-bottom: 30px;
  color: #303133;
  text-align: center;
  font-weight: 600;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 20px;
}

.feature-card {
  transition: transform 0.3s, box-shadow 0.3s;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.feature-primary {
  border-left: 4px solid #409EFF;
}

.feature-ai {
  border-left: 4px solid #67C23A;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.feature-icon {
  font-size: 48px;
}

.feature-title {
  font-size: 22px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.feature-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 15px;
}

.feature-details {
  margin: 15px 0;
}

.feature-details h4 {
  font-size: 15px;
  color: #303133;
  margin: 0 0 10px 0;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 15px 0;
}

.feature-list li {
  font-size: 13px;
  color: #606266;
  padding: 6px 0;
  line-height: 1.6;
}

.feature-list strong {
  color: #303133;
}

.feature-btn {
  width: 100%;
  margin-top: 15px;
}

.feature-collapse {
  margin-top: 10px;
}

.feature-collapse :deep(.el-collapse-item__header) {
  font-size: 14px;
  font-weight: 500;
}

.feature-collapse :deep(.el-collapse-item__content) {
  padding: 10px 15px;
}

/* AI API 卡片样式 */
.ai-example {
  margin-top: 15px;
  background-color: #f4f4f5 !important;
}

.example-content {
  font-size: 13px;
  line-height: 1.8;
}

.example-code {
  display: block;
  background-color: #f4f4f5;
  padding: 8px 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #303133;
  border-left: 3px solid #409EFF;
}

.api-links {
  margin-top: 15px;
  display: flex;
  align-items: center;
}

.sub-desc {
  font-size: 13px;
  color: #606266;
  margin: 0 0 10px 0;
}

/* 技术特性区域 */
.tech-section {
  margin-bottom: 40px;
  padding: 40px;
  background-color: #f5f7fa;
  border-radius: 10px;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.tech-item {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  transition: transform 0.3s;
}

.tech-item:hover {
  transform: translateY(-3px);
}

.tech-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.tech-item h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 10px 0;
}

.tech-item p {
  font-size: 13px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

/* 快速开始区域 */
.quick-start-section {
  margin-bottom: 40px;
  padding: 40px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  border-radius: 10px;
}

.quick-steps {
  margin-bottom: 30px;
}

.start-btn-wrapper {
  text-align: center;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.start-btn {
  padding: 15px 50px;
  font-size: 16px;
}

/* 使用说明区域 */
.info-section {
  margin-bottom: 20px;
}

.info-alert {
  border-radius: 8px;
}

.info-content {
  font-size: 14px;
  line-height: 2;
}

.info-content p {
  margin: 8px 0;
}

.info-content code {
  background-color: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #d93025;
  font-size: 13px;
}

/* 页脚 */
.footer-section {
  margin-top: 60px;
  padding: 30px;
  background-color: #f5f7fa;
  border-radius: 10px;
  text-align: center;
}

.footer-content p {
  margin: 5px 0;
  color: #606266;
  font-size: 14px;
}

.footer-links {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: center;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-title {
    font-size: 28px;
  }
  
  .welcome-subtitle {
    font-size: 16px;
  }
  
  .welcome-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .tech-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .start-btn-wrapper {
    flex-direction: column;
    align-items: center;
  }
}
</style>
