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
          <el-button type="primary" icon="Plus">新建智能体</el-button>
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
            <el-button link type="primary" size="small">配置</el-button>
            <el-button link type="danger" size="small">删除</el-button>
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
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// 响应式状态
const loading = ref(false)
const searchQuery = ref('')
const agentsList = ref<any[]>([])
const total = ref(0)

// 获取智能体列表 (真正与后端交互的函数)
const fetchAgents = async () => {
  loading.value = true
  try {
    // 假设你的 agent-framework 微服务提供 /agents 接口
    // 如果你本地跑了后端，它就会真实的去请求 http://localhost:8000/api/agents
    const res: any = await request.get('/agents', {
      params: { keyword: searchQuery.value }
    })
    
    // 适配后端的数据结构，这里假设后端返回一个数组，或者 { list: [], total: x }
    if (Array.isArray(res)) {
      agentsList.value = res
      total.value = res.length
    } else if (res && res.list) {
      agentsList.value = res.list
      total.value = res.total
    }
  } catch (error) {
    console.error('API调用失败，使用演示数据', error)
    // ⚠️ 如果你后端还没启动或者接口没写好，这里自动降级使用演示数据，保证你能看到 UI 效果
    setTimeout(() => {
      agentsList.value = [
        { id: 1, name: '作业批改助手', type: 'Grading', status: 'running', description: '自动批改 Python 代码作业' },
        { id: 2, name: '学情预警监测', type: 'Warning', status: 'running', description: '实时监控学生活跃度并预警' },
        { id: 3, name: '答疑机器人', type: 'QA', status: 'stopped', description: '基于知识库解答学生提问' }
      ]
      total.value = 3
    }, 500)
  } finally {
    loading.value = false
  }
}

// 切换状态按钮操作
const toggleStatus = (row: any) => {
  const action = row.status === 'running' ? '停止' : '启动'
  // 这里可以写向后端发送启动/停止指令的 request 请求
  // await request.post(`/agents/${row.id}/toggle`)
  
  // 前端模拟更新
  row.status = row.status === 'running' ? 'stopped' : 'running'
  ElMessage.success(`智能体 ${row.name} 已${action}`)
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
    
    .left, .right {
      display: flex;
      align-items: center;
    }
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
