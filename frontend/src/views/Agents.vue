<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>智能体管理</span>
          <el-button type="primary" @click="createDialogVisible = true">
            <el-icon><Plus /></el-icon>创建智能体
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="全部类型" clearable>
            <el-option label="问答型" value="qa" />
            <el-option label="批改型" value="grading" />
            <el-option label="预警型" value="warning" />
            <el-option label="练习型" value="exercise" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="活跃" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="agentList" stripe v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="course_id" label="关联课程" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleInvoke(row)">调用</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />
    </el-card>

    <!-- 创建对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建智能体" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="createForm.name" placeholder="请输入智能体名称" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="createForm.type" placeholder="请选择类型">
            <el-option label="问答型" value="qa" />
            <el-option label="批改型" value="grading" />
            <el-option label="预警型" value="warning" />
            <el-option label="练习型" value="exercise" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联课程">
          <el-select v-model="createForm.course_id" placeholder="请选择课程">
            <el-option label="Python程序设计" value="course-1" />
            <el-option label="数据结构" value="course-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="AI模型">
          <el-select v-model="createForm.config.model" placeholder="请选择模型">
            <el-option label="GLM-4" value="glm-4" />
            <el-option label="GLM-3-Turbo" value="glm-3-turbo" />
          </el-select>
        </el-form-item>
        <el-form-item label="温度参数">
          <el-slider v-model="createForm.config.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const createDialogVisible = ref(false)

const searchForm = reactive({
  type: '',
  status: ''
})

const createForm = reactive({
  name: '',
  type: '',
  course_id: '',
  config: {
    model: 'glm-4',
    temperature: 0.7,
    max_tokens: 2048
  }
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const agentList = ref([
  { id: '1', name: 'Python问答助手', type: 'qa', course_id: 'Python程序设计', status: 'active', created_at: '2025-04-13 10:00' },
  { id: '2', name: '代码批改助手', type: 'grading', course_id: '数据结构', status: 'active', created_at: '2025-04-12 15:30' }
])

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    qa: 'primary',
    grading: 'success',
    warning: 'warning',
    exercise: 'info'
  }
  return map[type] || 'info'
}

const getTypeName = (type: string) => {
  const map: Record<string, string> = {
    qa: '问答型',
    grading: '批改型',
    warning: '预警型',
    exercise: '练习型'
  }
  return map[type] || type
}

const handleSearch = () => {
  // TODO: 实现搜索逻辑
  ElMessage.info('搜索功能')
}

const handleReset = () => {
  searchForm.type = ''
  searchForm.status = ''
}

const handleCreate = () => {
  if (!createForm.name || !createForm.type) {
    ElMessage.warning('请填写必填项')
    return
  }
  createDialogVisible.value = false
  ElMessage.success('创建成功')
}

const handleEdit = (row: any) => {
  ElMessage.info(`编辑: ${row.name}`)
}

const handleInvoke = (row: any) => {
  ElMessage.info(`调用: ${row.name}`)
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该智能体吗？', '提示', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  // 加载数据
})
</script>

<style lang="scss" scoped>
.page-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>
