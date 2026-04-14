<template>
  <div class="knowledge-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span>专属知识库管理</span>
          <div class="header-actions">
            <el-button type="primary" icon="Upload" @click="uploadDialogVisible = true">
              上传新文档
            </el-button>
          </div>
        </div>
      </template>

      <div class="toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="检索文档名称..."
          prefix-icon="Search"
          clearable
          style="width: 320px"
        />
        <el-select v-model="statusFilter" placeholder="处理状态" clearable style="width: 120px; margin-left: 12px">
          <el-option label="已入库" value="success" />
          <el-option label="处理中" value="processing" />
        </el-select>
      </div>

      <el-table :data="filteredList" style="width: 100%" v-loading="loading">
        <el-table-column label="文档名称" min-width="250">
          <template #default="scope">
            <div class="doc-name">
              <el-icon :size="20" :color="getFileColor(scope.row.type)"><Document /></el-icon>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="uploadTime" label="上传时间" width="160" />
        <el-table-column label="向量化状态" width="140">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'success'" type="success" effect="light">已入库 (Vectorized)</el-tag>
            <el-tag v-else-if="scope.row.status === 'processing'" type="warning" effect="light">分块处理中...</el-tag>
            <el-tag v-else type="danger" effect="light">处理失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handlePreview(scope.row)">预览</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="上传知识文档" width="500px" destroy-on-close>
      <el-upload
        class="knowledge-uploader"
        drag
        action="/api/knowledge/upload"
        multiple
        :auto-upload="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或 <em>点击上传</em></div>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUploadSubmit">开始解析入库</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const uploadDialogVisible = ref(false)

const documentList = ref([
  { id: 1, name: 'EduAgent系统操作手册.pdf', type: 'pdf', size: '2.4 MB', uploadTime: '2026-04-14 10:00', status: 'success' },
  { id: 2, name: 'Python机器学习进阶课件.docx', type: 'word', size: '1.1 MB', uploadTime: '2026-04-13 15:30', status: 'success' },
  { id: 3, name: '深度学习算法公式推导.md', type: 'markdown', size: '45 KB', uploadTime: '2026-04-14 11:05', status: 'processing' },
])

// 增加前端过滤逻辑
const filteredList = computed(() => {
  return documentList.value.filter(doc => {
    const matchName = doc.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchStatus = statusFilter.value ? doc.status === statusFilter.value : true
    return matchName && matchStatus
  })
})

const getFileColor = (type: string) => {
  const colorMap: Record<string, string> = { pdf: '#ef4444', word: '#3b82f6', markdown: '#10b981', txt: '#64748b' }
  return colorMap[type] || '#64748b'
}

const handleUploadSubmit = () => {
  ElMessage.success('文档已提交给后端，正在进行切分和嵌入...')
  uploadDialogVisible.value = false
}

// --- 新增的交互逻辑 ---

const handlePreview = (row: any) => {
  ElMessage.info(`正在生成【${row.name}】的在线预览...`)
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要从向量数据库中删除 "${row.name}" 吗？相应的知识问答将不再包含此内容。`,
    '删除确认',
    { confirmButtonText: '删除', cancelButtonText: '取消', type: 'error' }
  ).then(() => {
    documentList.value = documentList.value.filter(item => item.id !== row.id)
    ElMessage.success('文档已从知识库移除')
  }).catch(() => {})
}
</script>

<style lang="scss" scoped>
.knowledge-container {
  .toolbar { display: flex; margin-bottom: 20px; }
  .doc-name { display: flex; align-items: center; gap: 10px; font-weight: 500; color: #1e293b; }
}
.knowledge-uploader :deep(.el-upload-dragger) {
  border-radius: 8px; background: #f8fafc; transition: all 0.3s;
  &:hover { background: #f0f7ff; border-color: var(--primary-color); }
}
</style>
