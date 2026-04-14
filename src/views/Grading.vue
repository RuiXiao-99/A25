<template>
  <div class="grading-container">
    <el-row :gutter="24" class="h-full">
      <el-col :span="8" class="h-full">
        <el-card shadow="never" class="list-card h-full flex-col">
          <template #header>
            <div class="card-header">
              <span>待批改列表 ({{ taskList.length }})</span>
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
            
            <div v-if="taskList.length === 0" class="empty-list">
              <el-icon :size="40" color="#cbd5e1"><Select /></el-icon>
              <p>太棒了！所有作业已批改完毕</p>
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
              <div class="action-area" v-if="currentTask.aiStatus === 'completed'">
                <el-button type="success" icon="Check" @click="handleConfirmScore">确认 AI 评分</el-button>
                <el-button type="warning" icon="EditPen" @click="handleManualEdit">人工修正</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const currentTask = ref<any>(null)

const taskList = ref([
  {
    id: 1,
    studentName: '张三',
    title: 'Python 基础：列表与循环练习',
    submitTime: '10分钟前',
    aiStatus: 'completed',
    aiScore: 85,
    content: "def process_list(items):\n    result = []\n    for i in items:\n        if i > 0:\n            result.append(i)\n    return result",
    aiComment: '代码逻辑基本正确，成功过滤了负数。建议可以使用 Python 的列表推导式 (List Comprehension) 来让代码更加简洁。'
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

// --- 新增的交互逻辑 ---

const handleConfirmScore = () => {
  ElMessageBox.confirm(
    `确认采纳 AI 评分（${currentTask.value.aiScore}分）并提交成绩吗？`,
    '确认成绩',
    { confirmButtonText: '提交', cancelButtonText: '再看看', type: 'success' }
  ).then(() => {
    ElMessage.success(`${currentTask.value.studentName} 的成绩已录入系统！`)
    // 从列表中移除已批改的作业
    taskList.value = taskList.value.filter(t => t.id !== currentTask.value.id)
    // 自动选择下一份作业
    currentTask.value = taskList.value.length > 0 ? taskList.value[0] : null
  }).catch(() => {})
}

const handleManualEdit = () => {
  ElMessageBox.prompt('请输入人工修正后的分数 (0-100)：', '人工修正', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^(100|[1-9]?\d)$/,
    inputErrorMessage: '分数必须在 0 到 100 之间'
  }).then(({ value }) => {
    currentTask.value.aiScore = value
    currentTask.value.aiComment += `\n[教师补充]：已将分数调整为 ${value} 分。`
    ElMessage.success('分数和评语已更新，您可以再次点击"确认评分"提交。')
  }).catch(() => {})
}

onMounted(() => {
  if (taskList.value.length > 0) {
    currentTask.value = taskList.value[0]
  }
})
</script>

<style lang="scss" scoped>
.grading-container {
  height: calc(100vh - 120px);
  .h-full { height: 100%; }
  .flex-col {
    display: flex; flex-direction: column;
    :deep(.el-card__body) { flex: 1; overflow: hidden; display: flex; flex-direction: column; padding: 0; }
  }
}

.list-card .task-list {
  flex: 1; overflow-y: auto; padding: 12px;
  .task-item {
    padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 12px; cursor: pointer; transition: all 0.2s; background: #fff;
    &:hover { border-color: #cbd5e1; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    &.active { border-color: var(--primary-color); background: #f0f7ff; }
    .task-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; .student-name { font-weight: 600; color: #0f172a; } }
    .task-title { font-size: 13px; color: #475569; margin-bottom: 8px; line-height: 1.4; }
    .task-time { font-size: 12px; color: #94a3b8; }
  }
  .empty-list { text-align: center; color: #94a3b8; margin-top: 40px; }
}

.workspace-card {
  .workspace-header { padding: 20px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #fff; h3 { margin: 0 0 4px 0; color: #0f172a; } .subtitle { font-size: 13px; color: #64748b; } }
  .workspace-content {
    flex: 1; overflow-y: auto; padding: 24px; background: #f8fafc;
    .content-section { margin-bottom: 24px; h4 { margin: 0 0 12px 0; color: #334155; display: flex; align-items: center; gap: 8px; } .code-block { background: #1e293b; border-radius: 8px; padding: 16px; pre { margin: 0; color: #e2e8f0; font-family: 'Fira Code', Consolas, monospace; font-size: 14px; white-space: pre-wrap; } } }
    .ai-feedback .feedback-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; .score-display { margin-bottom: 12px; font-size: 16px; .score { font-size: 24px; font-weight: bold; color: var(--primary-color); } } .comment { color: #475569; line-height: 1.6; } }
    .analyzing-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: var(--primary-color); background: #fff; border-radius: 8px; border: 1px dashed #93c5fd; span { margin-top: 12px; } }
  }
  .empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; p { margin-top: 16px; font-size: 15px; } }
}
</style>
