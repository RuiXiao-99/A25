<template>
  <div class="agents-container">
    <el-card class="box-card" shadow="never">
      <div class="action-bar">
        <div class="left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索智能体名称..."
            prefix-icon="Search"
            clearable
            style="width: 300px"
            @clear="fetchAgents"
            @keyup.enter="fetchAgents"
          />
          <el-button type="primary" @click="fetchAgents" style="margin-left: 12px">搜索</el-button>
        </div>
        <div class="right">
          <el-button type="primary" icon="Plus" @click="handleCreate">新建智能体</el-button>
          <el-button icon="Refresh" @click="fetchAgents">刷新</el-button>
        </div>
      </div>

      <el-table 
        v-loading="loading" 
        :data="agentsList" 
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="智能体名称" min-width="150">
          <template #default="scope">
            <span style="font-weight: 500; color: #0f172a">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.type || '通用型' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="运行状态" width="120">
          <template #default="scope">
            <el-tag 
              :type="scope.row.status === 'running' ? 'success' : 'danger'"
              effect="light"
            >
              {{ scope.row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              link 
              type="primary" 
              size="small"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button link type="primary" size="small" @click="handleConfig(scope.row)">配置</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :page-size="10"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const loading = ref(false)
const searchQuery = ref('')
const agentsList = ref<any[]>([])
const total = ref(0)

const fetchAgents = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/agents', { params: { keyword: searchQuery.value } })
    if (Array.isArray(res)) {
      agentsList.value = res
      total.value = res.length
    }
  } catch (error) {
    setTimeout(() => {
      // 模拟过滤逻辑
      const mockData = [
        { id: 1, name: '作业批改助手', type: 'Grading', status: 'running', description: '自动批改 Python 代码作业' },
        { id: 2, name: '学情预警监测', type: 'Warning', status: 'running', description: '实时监控学生活跃度并预警' },
        { id: 3, name: '答疑机器人', type: 'QA', status: 'stopped', description: '基于知识库解答学生提问' }
      ]
      agentsList.value = searchQuery.value 
        ? mockData.filter(item => item.name.includes(searchQuery.value)) 
        : mockData
      total.value = agentsList.value.length
      loading.value = false
    }, 500)
  }
}

const toggleStatus = (row: any) => {
  const action = row.status === 'running' ? '停止' : '启动'
  row.status = row.status === 'running' ? 'stopped' : 'running'
  ElMessage.success(`智能体 "${row.name}" 已${action}`)
}

// --- 新增的交互逻辑 ---

const handleCreate = () => {
  ElMessage.info('即将打开：新建智能体抽屉')
}

const handleConfig = (row: any) => {
  ElMessage.info(`正在加载 "${row.name}" 的配置参数...`)
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除智能体 "${row.name}" 吗？此操作不可恢复。`,
    '高危操作警告',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    // 实际项目中这里调用 API: await request.delete(`/agents/${row.id}`)
    agentsList.value = agentsList.value.filter(item => item.id !== row.id)
    total.value -= 1
    ElMessage.success(`已成功删除智能体: ${row.name}`)
  }).catch(() => {
    ElMessage.info('已取消删除操作')
  })
}

onMounted(() => {
  fetchAgents()
})
</script>

<style lang="scss" scoped>
.agents-container {
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    .left, .right { display: flex; align-items: center; }
  }
  .pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
