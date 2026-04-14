<template>
  <div class="dashboard-container">
    <div class="welcome-section">
      <h2>欢迎回来，管理员 👋</h2>
      <p>这是您今天的 EduAgent 教学智能体运行概况</p>
    </div>

    <el-row :gutter="24" class="stat-cards">
      <el-col :span="6" v-for="stat in statistics" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">
                <el-skeleton v-if="loading" animated :rows="1" style="width: 60px" />
                <span v-else>{{ stat.value }}</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor, color: stat.color }">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="main-content">
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>系统运行趋势</span>
              <el-button type="primary" link>查看详情</el-button>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-skeleton v-if="loading" animated :rows="6" />
            <div v-else class="empty-chart">
              <el-icon :size="48" color="#dcdfe6"><TrendCharts /></el-icon>
              <p>暂无足够的数据生成图表</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="never" class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最新系统动态</span>
            </div>
          </template>
          <el-skeleton v-if="loading" animated :rows="5" />
          <el-timeline v-else>
            <el-timeline-item timestamp="10 分钟前" type="primary">
              批改智能体完成 45 份作业
            </el-timeline-item>
            <el-timeline-item timestamp="1 小时前" type="success">
              新增知识库文档 "Python基础语法.pdf"
            </el-timeline-item>
            <el-timeline-item timestamp="2 小时前" type="warning">
              学情预警：2名学生未按时提交作业
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/api/request' // 引入我们配置好的请求工具

const loading = ref(true)

// 定义前端展示的数据结构
const statistics = ref([
  { title: '活跃智能体', value: '0', icon: 'Monitor', bgColor: '#e6f7ff', color: '#1890ff' },
  { title: '知识库文档', value: '0', icon: 'Collection', bgColor: '#f6ffed', color: '#52c41a' },
  { title: '管理学生', value: '0', icon: 'User', bgColor: '#fffb8f', color: '#faad14' },
  { title: '预警信息', value: '0', icon: 'Warning', bgColor: '#fff1f0', color: '#f5222d' }
])

// 模拟向后端请求 Dashboard 数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 假设你的后端有一个 /api/dashboard 接口
    // const data = await request.get('/dashboard')
    
    // 因为后端可能还没写好这部分，我们用 setTimeout 模拟一次真实的延迟请求
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟后端返回的数据赋值
    statistics.value[0].value = '8'
    statistics.value[1].value = '124'
    statistics.value[2].value = '1,024'
    statistics.value[3].value = '3'
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style lang="scss" scoped>
.welcome-section {
  margin-bottom: 24px;
  h2 {
    font-size: 24px;
    color: #1e293b;
    margin-bottom: 8px;
  }
  p {
    color: #64748b;
  }
}

.stat-cards {
  margin-bottom: 24px;
}

.stat-card {
  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-title {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 8px;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #0f172a;
  }

  .stat-icon {
    width: 54px;
    height: 54px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    transition: transform 0.3s;
  }

  &:hover .stat-icon {
    transform: scale(1.1);
  }
}

.main-content {
  .chart-card, .activity-card {
    height: 400px;
  }

  .chart-placeholder {
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .empty-chart {
      text-align: center;
      color: #94a3b8;
      
      p {
        margin-top: 16px;
      }
    }
  }
}
</style>
