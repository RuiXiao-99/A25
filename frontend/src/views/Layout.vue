<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="layout-aside">
      <div class="logo">
        <el-icon :size="28" class="logo-icon"><School /></el-icon>
        <span v-show="!isCollapse" class="logo-text">EduAgent</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        class="layout-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><Monitor /></el-icon>
          <template #title>智能体管理</template>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Collection /></el-icon>
          <template #title>知识管理</template>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon><Reading /></el-icon>
          <template #title>课程管理</template>
        </el-menu-item>
        <el-menu-item index="/students">
          <el-icon><User /></el-icon>
          <template #title>学生管理</template>
        </el-menu-item>
        <el-menu-item index="/grading">
          <el-icon><Edit /></el-icon>
          <template #title>作业批改</template>
        </el-menu-item>
        <el-menu-item index="/warning">
          <el-icon><Warning /></el-icon>
          <template #title>学情预警</template>
        </el-menu-item>
        <el-menu-item index="/exercise">
          <el-icon><Document /></el-icon>
          <template #title>练习管理</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="layout-header">
        <div class="header-left">
          <div class="collapse-btn" @click="isCollapse = !isCollapse">
            <el-icon :size="22">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </div>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item class="current-bread">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="36" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
              <div class="user-detail" v-if="!isCollapse">
                <span class="username">管理员</span>
                <span class="role">超级权限</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item icon="User">个人设置</el-dropdown-item>
                <el-dropdown-item divided icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isCollapse = ref(false)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '工作台')
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  display: flex;
}

.layout-aside {
  background: var(--bg-color-sidebar);
  transition: width 0.3s cubic-bezier(0.2, 0, 0, 1);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
  display: flex;
  flex-direction: column;

  .logo {
    height: var(--header-height);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 20px;
    font-weight: 700;
    gap: 12px;
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);

    .logo-icon {
      color: var(--primary-color);
    }
    .logo-text {
      white-space: nowrap;
      letter-spacing: 1px;
    }
  }

  .layout-menu {
    border-right: none;
    background: transparent;
    flex: 1;
    padding-top: 10px;

    :deep(.el-menu-item) {
      color: var(--text-color-sidebar);
      margin: 4px 12px;
      border-radius: 8px;
      height: 48px;
      line-height: 48px;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #fff;
      }

      &.is-active {
        background: var(--primary-color);
        color: #fff;
        box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
      }
    }
  }
}

.main-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.layout-header {
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px); // 毛玻璃效果
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.04);
  z-index: 5;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .collapse-btn {
      cursor: pointer;
      color: #64748b;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 6px;
      transition: all 0.2s;

      &:hover {
        background: #f1f5f9;
        color: var(--primary-color);
      }
    }

    .current-bread {
      font-weight: 600;
      color: #1e293b;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 4px 12px;
      border-radius: 24px;
      transition: background 0.2s;

      &:hover {
        background: #f1f5f9;
      }

      .user-detail {
        display: flex;
        flex-direction: column;
        line-height: 1.2;
        
        .username {
          font-size: 14px;
          font-weight: 600;
          color: #334155;
        }
        .role {
          font-size: 12px;
          color: #94a3b8;
        }
      }
    }
  }
}

.layout-main {
  background: var(--bg-color-main);
  padding: 24px;
  height: calc(100vh - var(--header-height));
  overflow-y: auto;
  overflow-x: hidden;
}

/* 页面切换高级过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(15px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}
</style>
