<template>
  <div class="grading-container">
    <el-row :gutter="24" class="h-full">
      <el-col :span="8" class="h-full">
        <el-card shadow="never" class="list-card h-full flex-col">
          <template #header>
            <div class="card-header">
              <span>待批改列表 ({{ pendingCount }})</span>
              <el-button type="primary" link icon="Filter">筛选</el-button>
            </div>
          </template>
          
          <div class="task-list" v-loading="loading">
            <div 
              v-for="task in taskList" 
              :key="task.id"
              :class="['task-item', { active: currentTask?.id === task.id }]"
              @click="selectTask(task)"
            >
              <div class="task-head">
                <span class="student-name">{{ task.studentName }}</span>
                <el-tag size="small" :type="task.aiStatus === 'completed' ? 'success' : 'warning'">
                  {{ task.aiStatus === 'completed' ? 'AI已阅' : 'AI分析中' }}
                </el-tag>
              </div>
              <div class="task-title">{{ task.title }}</div>
              <div class="task-time">{{ task.submitTime }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16" class="h-full">
        <el-card shadow="never" class="workspace-card h-full flex-col">
          <template v-if="currentTask">
            <div class="workspace-header">
              <div class="title-area">
                <h3>{{ currentTask.title }}</h3>
                <span class="subtitle">{{ currentTask.studentName }} 的提交</span>
              </div>
              <div class="action-area">
                <el-button type="success" icon="Check">确认 AI 评分</el-button>
                <el-button type="warning" icon="EditPen">人工修正</el-button>
              </div>
            </div>

            <div class="workspace-content">
              <div class="content-section">
                <h4>学生提交代码 (Python)</h4>
                <div class="code-block">
                  <pre><code>{{ currentTask.content }}</code></pre>
                </div>
              </div>

              <div class="content-section ai-feedback">
                <h4><el-icon><Monitor /></el-icon> 批改智能体建议</h4>
                <div v-if="currentTask.aiStatus === 'completed'" class="feedback-box">
                  <div class="score-display">
                    <span class="label">建议得分：</span>
                    <span class="score">{{ currentTask.aiScore }} / 100</span>
                  </div>
                  <p class="comment">{{ currentTask.aiComment }}</p>
                  <div class="tags">
                    <el-tag size="small" type="danger" v-if="currentTask.hasError">存在语法错误</el-tag>
                    <el-tag size="small" type="success" v-else>运行通过</el-tag>
                    <el-tag size="small" type="info">建议优化变量命名</el-tag>
                  </div>
                </div>
                <div v-else class="analyzing-state">
                  <el-icon class="is-loading" :size="24"><Loading /></el-icon>
                  <span>智能体正在努力分析中...</span>
                </div>
              </div>
            </div>
          </template>
          
          <div v-else class="empty-state">
            <el-icon :size="64" color="#cbd5e1"><DocumentChecked /></el-icon>
            <p>请在左侧选择一份作业进行批改</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 模拟状态
const loading = ref(false)
const currentTask = ref<any>(null)
const pendingCount = ref(3)

// 演示数据：包含了一段 Python 代码的作业
const taskList = ref([
  {
    id: 1,
    studentName: '张三',
    title: 'Python 基础：列表与循环练习',
    submitTime: '10分钟前',
    aiStatus: 'completed',
    aiScore: 85,
    hasError: false,
    content: "def process_list(items):\n    result = []\n    for i in items:\n        if i > 0:\n            result.append(i)\n    return result",
    aiComment: '代码逻辑基本正确，成功过滤了负数。建议可以使用 Python 的列表推导式 (List Comprehension) 来让代码更加简洁：[i for i in items if i > 0]。'
  },
  {
    id: 2,
    studentName: '李四',
    title: 'Python 基础：变量与函数',
    submitTime: '半小时前',
    aiStatus: 'processing',
    content: "def calculate_area(r)\n    area = 3.14 * r * r\n    return area",
  }
])

const selectTask = (task: any) => {
  currentTask.value = task
}

onMounted(() => {
  // 实际开发中，这里调用 request.get('/api/gradings/pending') 获取列表
  if (taskList.value.length > 0) {
    currentTask.value = taskList.value[0]
  }
})
</script>

<style lang="scss" scoped>
.grading-container {
  height: calc(100vh - 120px);
  
  .h-full {
    height: 100%;
  }
  
  .flex-col {
    display: flex;
    flex-direction: column;
    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      padding: 0;
    }
  }
}

.list-card {
  .task-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    
    .task-item {
      padding: 16px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.2s;
      background: #fff;

      &:hover {
        border-color: #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      }

      &.active {
        border-color: var(--primary-color);
        background: #f0f7ff;
      }

      .task-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .student-name {
          font-weight: 600;
          color: #0f172a;
        }
      }

      .task-title {
        font-size: 13px;
        color: #475569;
        margin-bottom: 8px;
        line-height: 1.4;
      }

      .task-time {
        font-size: 12px;
        color: #94a3b8;
      }
    }
  }
}

.workspace-card {
  .workspace-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;

    h3 {
      margin: 0 0 4px 0;
      color: #0f172a;
    }
    
    .subtitle {
      font-size: 13px;
      color: #64748b;
    }
  }

  .workspace-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    background: #f8fafc;

    .content-section {
      margin-bottom: 24px;

      h4 {
        margin: 0 0 12px 0;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .code-block {
        background: #1e293b;
        border-radius: 8px;
        padding: 16px;
        
        pre {
          margin: 0;
          color: #e2e8f0;
          font-family: 'Fira Code', Consolas, monospace;
          font-size: 14px;
          white-space: pre-wrap;
        }
      }
    }

    .ai-feedback {
      .feedback-box {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);

        .score-display {
          margin-bottom: 12px;
          font-size: 16px;
          
          .score {
            font-size: 24px;
            font-weight: bold;
            color: var(--primary-color);
          }
        }

        .comment {
          color: #475569;
          line-height: 1.6;
          margin-bottom: 16px;
        }

        .tags {
          display: flex;
          gap: 8px;
        }
      }

      .analyzing-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        color: var(--primary-color);
        background: #fff;
        border-radius: 8px;
        border: 1px dashed #93c5fd;
        
        span {
          margin-top: 12px;
        }
      }
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    
    p {
      margin-top: 16px;
      font-size: 15px;
    }
  }
}
</style>
