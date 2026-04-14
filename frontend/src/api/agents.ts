import request from './request'
import type { Agent, PaginatedResponse, BaseResponse } from '@/types'

// 获取智能体列表
export function getAgents(params: {
  course_id?: string
  type?: string
  status?: string
  page?: number
  size?: number
}) {
  return request.get<BaseResponse<PaginatedResponse<Agent>>>('/agents', { params })
}

// 创建智能体
export function createAgent(data: {
  name: string
  type: string
  course_id?: string
  config?: Record<string, unknown>
}) {
  return request.post<BaseResponse<Agent>>('/agents', data)
}

// 获取智能体详情
export function getAgent(agentId: string) {
  return request.get<BaseResponse<Agent>>(`/agents/${agentId}`)
}

// 更新智能体
export function updateAgent(
  agentId: string,
  data: {
    name?: string
    config?: Record<string, unknown>
    status?: string
  }
) {
  return request.put<BaseResponse<Agent>>(`/agents/${agentId}`, data)
}

// 删除智能体
export function deleteAgent(agentId: string) {
  return request.delete<BaseResponse<void>>(`/agents/${agentId}`)
}

// 调用智能体
export function invokeAgent(agentId: string, requestData: Record<string, unknown>) {
  return request.post<BaseResponse<unknown>>(`/agents/${agentId}/invoke`, requestData)
}
