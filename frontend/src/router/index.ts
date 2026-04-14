import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/views/Agents.vue'),
        meta: { title: '智能体管理' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识管理' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/Courses.vue'),
        meta: { title: '课程管理' }
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('@/views/Students.vue'),
        meta: { title: '学生管理' }
      },
      {
        path: 'grading',
        name: 'Grading',
        component: () => import('@/views/Grading.vue'),
        meta: { title: '作业批改' }
      },
      {
        path: 'warning',
        name: 'Warning',
        component: () => import('@/views/Warning.vue'),
        meta: { title: '学情预警' }
      },
      {
        path: 'exercise',
        name: 'Exercise',
        component: () => import('@/views/Exercise.vue'),
        meta: { title: '练习管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'EduAgent'} - EduAgent Platform`
  next()
})

export default router
