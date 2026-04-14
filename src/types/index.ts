// 基础响应类型
export interface BaseResponse<T = unknown> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 分页响应类型
export interface PaginatedResponse<T = unknown> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 智能体配置
export interface AgentConfig {
  model: string
  temperature: number
  max_tokens: number
  system_prompt?: string
  knowledge_base_ids: string[]
}

// 智能体
export interface Agent {
  id: string
  name: string
  type: string
  course_id?: string
  config: AgentConfig
  status: string
  created_at: string
  updated_at: string
}

// 课程
export interface Course {
  id: string
  name: string
  code: string
  description?: string
  status: string
  created_at: string
}

// 学生
export interface Student {
  id: string
  user_id: string
  name: string
  email?: string
  profile_data: Record<string, unknown>
  created_at: string
}

// 知识点
export interface KnowledgePoint {
  id: string
  name: string
  description?: string
  parent_id?: string
  course_id: string
  tags: string[]
}

// 作业
export interface Assignment {
  id: string
  course_id: string
  title: string
  content: string
  type: string
  knowledge_points: string[]
  deadline?: string
  created_at: string
}

// 提交记录
export interface Submission {
  id: string
  assignment_id: string
  student_id: string
  content: string
  file_urls: string[]
  annotations: Annotation[]
  score?: number
  feedback?: string
  status: string
  submitted_at: string
}

// 批注
export interface Annotation {
  position: {
    line?: number
    column?: number
    length?: number
  }
  type: 'error' | 'warning' | 'suggestion'
  content: string
  suggestion?: string
}

// 预警
export interface Warning {
  id: string
  student_id: string
  course_id: string
  level: 'low' | 'medium' | 'high'
  type: string
  description: string
  knowledge_points: string[]
  status: string
  created_at: string
}

// 练习
export interface Exercise {
  id: string
  type: 'choice' | 'coding' | 'essay'
  title: string
  content: string
  knowledge_points: string[]
  difficulty: 'easy' | 'medium' | 'hard'
  hints: string[]
  options?: string[]
  answer?: string
}

// 学习记录
export interface LearningRecord {
  student_id: string
  course_id: string
  knowledge_point_id: string
  mastery_level: number
  practice_count: number
  correct_count: number
  last_practice_at?: string
}
