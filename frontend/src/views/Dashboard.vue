<template>
  <div class="dashboard">
    <el-row :gutter="24" class="stat-row">
      <el-col :span="6" v-for="stat in statistics" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="28">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="content-row">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>学习趋势</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-icon :size="48" color="#1890ff"><TrendCharts /></el-icon>
            <p>学习趋势图表区域</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="warning-card">
          <template #header>
            <div class="card-header">
              <span>最近预警</span>
              <el-button type="primary" link>查看全部</el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="warning in recentWarnings"
              :key="warning.id"
              :type="warning.level === 'high' ? 'danger' : warning.level === 'medium' ? 'warning' : 'info'"
              :timestamp="warning.time"
              placement="top"
            >
              <el-card>
                <div class="warning-item">
                  <span class="student-name">{{ warning.student }}</span>
                  <el-tag :type="warning.level === 'high' ? 'danger' : warning.level === 'medium' ? 'warning' : 'info'" size="small">
                    {{ warning.level === 'high' ? '高风险' : warning.level === 'medium' ? '中风险' : '低风险' }}
                  </el-tag>
                </div>
                <p class="warning-desc">{{ warning.description }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="table-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近作业提交</span>
            </div>
          </template>
          <el-table :data="recentSubmissions" stripe>
            <el-table-column prop="student" label="学生" width="120" />
            <el-table-column prop="assignment" label="作业" />
            <el-table-column prop="score" label="分数" width="100">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.score"
                  :color="row.score >= 80 ? '#52c41a' : row.score >= 60 ? '#faad14' : '#f5222d'"
                  :show-text="false"
                />
                <span>{{ row.score }}分</span>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="提交时间" width="180" />
            <el-table-column label="操作" width="120">
              <template #default>
                <el-button type="primary" link>查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const statistics = ref([
  { title: '活跃智能体', value: 12, icon: 'Monitor', color: '#1890ff' },
  { title: '注册课程', value: 8, icon: 'Reading', color: '#52c41a' },
  { title: '学生总数', value: 256, icon: 'User', color: '#722ed1' },
  { title: '预警学生', value: 15, icon: 'Warning', color: '#faad14' }
])

const recentWarnings = ref([
  { id: 1, student: '张三', level: 'high', description: '递归知识点掌握不足', time: '10分钟前' },
  { id: 2, student: '李四', level: 'medium', description: '作业完成率下降', time: '1小时前' },
  { id: 3, student: '王五', level: 'low', description: '学习活跃度降低', time: '2小时前' }
])

const recentSubmissions = ref([
  { student: '张三', assignment: 'Python基础练习', score: 85, time: '2025-04-13 10:30' },
  { student: '李四', assignment: '数据结构作业', score: 72, time: '2025-04-13 10:15' },
  { student: '王五', assignment: '算法实现实验', score: 90, time: '2025-04-13 09:45' },
  { student: '赵六', assignment: 'Python基础练习', score: 65, time: '2025-04-13 09:30' }
])
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-row {
    margin-bottom: 24px;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
      }

      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #333;
        }

        .stat-title {
          font-size: 14px;
          color: #999;
          margin-top: 4px;
        }
      }
    }
  }

  .content-row {
    margin-bottom: 24px;
  }

  .chart-card {
    height: 380px;

    .chart-placeholder {
      height: 280px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #999;

      p {
        margin-top: 16px;
      }
    }
  }

  .warning-card {
    height: 380px;
    overflow-y: auto;

    .warning-item {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .student-name {
        font-weight: 500;
      }
    }

    .warning-desc {
      margin: 8px 0 0;
      font-size: 12px;
      color: #666;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
  }
}
</style>
