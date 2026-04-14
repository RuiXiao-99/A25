# API接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API版本**: v1
- **文档格式**: OpenAPI 3.0

## 认证

使用JWT Token认证，在请求头中添加：

```
Authorization: Bearer <token>
```

## 统一响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": { ... },
    "timestamp": "2025-04-13T10:00:00Z"
}
```

---

## 1. Agent管理接口

### 1.1 获取智能体列表

**GET** `/api/v1/agents`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_id | string | 否 | 课程ID |
| type | string | 否 | 智能体类型 |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认20 |

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": "agent-001",
                "name": "Python课程助手",
                "type": "qa",
                "course_id": "course-001",
                "status": "active",
                "created_at": "2025-04-13T10:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }
}
```

### 1.2 创建智能体

**POST** `/api/v1/agents`

**请求体**:
```json
{
    "name": "Python课程助手",
    "type": "qa",
    "course_id": "course-001",
    "config": {
        "model": "glm-4",
        "temperature": 0.7,
        "max_tokens": 2048
    }
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "agent-001",
        "name": "Python课程助手",
        "type": "qa",
        "course_id": "course-001",
        "status": "active",
        "created_at": "2025-04-13T10:00:00Z"
    }
}
```

### 1.3 获取智能体详情

**GET** `/api/v1/agents/{agent_id}`

### 1.4 更新智能体

**PUT** `/api/v1/agents/{agent_id}`

### 1.5 删除智能体

**DELETE** `/api/v1/agents/{agent_id}`

---

## 2. 智能答疑接口

### 2.1 提问

**POST** `/api/v1/qa/ask`

**请求体**:
```json
{
    "agent_id": "agent-001",
    "question": "什么是Python的装饰器？",
    "context": {
        "session_id": "session-001",
        "history": []
    }
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "answer": "装饰器是Python的一个高级特性...",
        "sources": [
            {
                "knowledge_id": "kp-001",
                "title": "Python装饰器",
                "relevance": 0.95
            }
        ],
        "session_id": "session-001"
    }
}
```

### 2.2 多轮对话

**POST** `/api/v1/qa/chat`

**请求体**:
```json
{
    "agent_id": "agent-001",
    "message": "能给我举个例子吗？",
    "session_id": "session-001"
}
```

---

## 3. 作业批改接口

### 3.1 提交批改

**POST** `/api/v1/grading/submit`

**请求体**:
```json
{
    "assignment_id": "assignment-001",
    "student_id": "student-001",
    "content": "# Python代码\n\ndef fibonacci(n):\n    ...",
    "file_urls": [
        "https://storage.example.com/files/homework.pdf"
    ]
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "submission_id": "submission-001",
        "score": 85.5,
        "annotations": [
            {
                "position": {
                    "line": 5,
                    "column": 10,
                    "length": 20
                },
                "type": "error",
                "content": "此处缺少边界条件检查",
                "suggestion": "建议添加 if n <= 0: return []"
            }
        ],
        "feedback": "整体实现正确，但需要注意边界条件的处理...",
        "graded_at": "2025-04-13T10:05:00Z"
    }
}
```

### 3.2 获取批改结果

**GET** `/api/v1/grading/result/{submission_id}`

### 3.3 获取批注详情

**GET** `/api/v1/grading/annotations/{submission_id}`

---

## 4. 学情预警接口

### 4.1 获取预警列表

**GET** `/api/v1/warning/list`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_id | string | 否 | 课程ID |
| level | string | 否 | 预警级别 (low/medium/high) |
| page | int | 否 | 页码 |

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": "warning-001",
                "student_id": "student-001",
                "student_name": "张三",
                "course_id": "course-001",
                "level": "high",
                "type": "knowledge_gap",
                "description": "在"递归"知识点存在较大差距",
                "knowledge_points": ["递归", "函数调用"],
                "created_at": "2025-04-13T10:00:00Z"
            }
        ],
        "total": 1
    }
}
```

### 4.2 学生风险预测

**GET** `/api/v1/warning/predict/{student_id}`

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "student_id": "student-001",
        "risk_level": "medium",
        "risk_score": 0.65,
        "factors": [
            {
                "factor": "作业完成率低",
                "weight": 0.3,
                "value": 0.6
            },
            {
                "factor": "知识点掌握不足",
                "weight": 0.4,
                "value": 0.7
            }
        ],
        "recommendations": [
            "建议加强"递归"相关知识点的练习",
            "建议按时完成作业"
        ]
    }
}
```

---

## 5. 增量练习接口

### 5.1 生成练习

**POST** `/api/v1/exercise/generate`

**请求体**:
```json
{
    "student_id": "student-001",
    "knowledge_points": ["递归", "函数调用"],
    "difficulty": "medium",
    "count": 5
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "exercises": [
            {
                "id": "exercise-001",
                "type": "coding",
                "title": "实现阶乘函数",
                "content": "请使用递归实现一个计算阶乘的函数...",
                "knowledge_points": ["递归"],
                "difficulty": "medium",
                "hints": [
                    "阶乘的定义是什么？",
                    "递归的终止条件是什么？"
                ]
            }
        ]
    }
}
```

### 5.2 提交练习答案

**POST** `/api/v1/exercise/submit`

**请求体**:
```json
{
    "exercise_id": "exercise-001",
    "student_id": "student-001",
    "answer": "def factorial(n): ..."
}
```

---

## 6. 课程管理接口

### 6.1 获取课程列表

**GET** `/api/v1/courses`

### 6.2 创建课程

**POST** `/api/v1/courses`

### 6.3 获取课程详情

**GET** `/api/v1/courses/{course_id}`

### 6.4 获取知识点列表

**GET** `/api/v1/courses/{course_id}/knowledge-points`

---

## 7. 学生管理接口

### 7.1 获取学生列表

**GET** `/api/v1/students`

### 7.2 获取学生画像

**GET** `/api/v1/students/{student_id}/profile`

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "student_id": "student-001",
        "name": "张三",
        "courses": [
            {
                "course_id": "course-001",
                "course_name": "Python程序设计",
                "mastery": {
                    "overall": 0.72,
                    "knowledge_points": [
                        {
                            "name": "变量与数据类型",
                            "mastery": 0.95
                        },
                        {
                            "name": "函数",
                            "mastery": 0.80
                        },
                        {
                            "name": "递归",
                            "mastery": 0.45
                        }
                    ]
                }
            }
        ]
    }
}
```

---

## 8. 平台适配接口

### 8.1 注册平台适配器

**POST** `/api/v1/adapters`

### 8.2 同步课程数据

**POST** `/api/v1/adapters/{adapter_id}/sync`

### 8.3 Webhook回调

**POST** `/api/v1/webhooks/{platform}`

---

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| SUCCESS | 200 | 成功 |
| CREATED | 201 | 资源创建成功 |
| BAD_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

## 限流策略

- 默认限流: 100次/分钟
- 批改接口: 10次/分钟
- 问答接口: 60次/分钟
