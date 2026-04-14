"""
EduAgent Platform - Windows Demo
可嵌入式跨课程AI Agent通用架构平台 - 演示程序

这是一个完整的演示程序，展示了平台的核心功能：
1. 智能体管理
2. 知识库管理
3. 智能答疑
4. 作业批改
5. 学情预警
6. 增量练习

运行方式:
    python demo.py

要求:
    - Python 3.10+
    - 已安装依赖: pip install -r requirements.txt
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.database import init_database, dao_factory, db_manager
from shared.utils import generate_uuid


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.END}")


def print_error(text: str):
    """打印错误"""
    print(f"{Colors.FAIL}✗ {text}{Colors.END}")


def print_json(data: Dict[str, Any], indent: int = 2):
    """打印JSON数据"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


class EduAgentDemo:
    """EduAgent平台演示"""
    
    def __init__(self):
        self.course_id = None
        self.student_id = None
        self.agent_id = None
        self.knowledge_points = []
        
    async def initialize(self):
        """初始化数据库"""
        print_info("初始化数据库...")
        db_path = os.path.join(os.path.dirname(__file__), "data", "eduagent.db")
        await init_database(db_path)
        print_success(f"数据库已初始化: {db_path}")
        
    async def demo_course_management(self):
        """演示课程管理"""
        print_header("1. 课程管理")
        
        dao = dao_factory.course()
        
        # 创建课程
        print_info("创建课程...")
        self.course_id = generate_uuid()
        course_data = {
            "id": self.course_id,
            "name": "Python程序设计",
            "code": "CS101",
            "description": "Python编程基础课程，涵盖基本语法、数据结构和算法",
            "status": "active"
        }
        await dao.insert(course_data)
        print_success(f"创建课程: {course_data['name']} (ID: {self.course_id[:8]}...)")
        
        # 查询课程
        print_info("查询课程...")
        course = await dao.get_by_id(self.course_id)
        print_json({
            "id": course["id"][:8] + "...",
            "name": course["name"],
            "code": course["code"],
            "description": course["description"]
        })
        
    async def demo_knowledge_management(self):
        """演示知识库管理"""
        print_header("2. 知识库管理")
        
        dao = dao_factory.knowledge_point()
        
        # 创建知识点
        print_info("创建知识点...")
        knowledge_data = [
            {"name": "Python基础语法", "description": "变量、数据类型、运算符"},
            {"name": "流程控制", "description": "条件语句、循环语句"},
            {"name": "函数", "description": "函数定义、参数、返回值"},
            {"name": "数据结构", "description": "列表、字典、元组、集合"},
            {"name": "面向对象", "description": "类、对象、继承、多态"},
        ]
        
        for i, data in enumerate(knowledge_data):
            kp_id = generate_uuid()
            self.knowledge_points.append(kp_id)
            await dao.insert({
                "id": kp_id,
                "name": data["name"],
                "description": data["description"],
                "course_id": self.course_id,
                "parent_id": None,
                "tags": ["python", "基础"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            print_success(f"创建知识点: {data['name']}")
        
        # 列出知识点
        print_info("列出所有知识点...")
        points = await dao.list_by_course(self.course_id)
        for p in points:
            print(f"  - {p['name']}: {p.get('description', '')}")
            
    async def demo_agent_management(self):
        """演示智能体管理"""
        print_header("3. 智能体管理")
        
        dao = dao_factory.agent()
        
        # 创建智能体
        print_info("创建AI助教智能体...")
        self.agent_id = generate_uuid()
        agent_data = {
            "id": self.agent_id,
            "name": "Python课程AI助教",
            "type": "teaching_assistant",
            "course_id": self.course_id,
            "config": {
                "model": "glm-4",
                "temperature": 0.7,
                "max_tokens": 2048,
                "system_prompt": "你是一位专业的Python编程助教，擅长解答学生的问题。"
            },
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await dao.insert(agent_data)
        print_success(f"创建智能体: {agent_data['name']} (ID: {self.agent_id[:8]}...)")
        
        # 查询智能体
        print_info("查询智能体...")
        agent = await dao.get_by_id(self.agent_id)
        print_json({
            "name": agent["name"],
            "type": agent["type"],
            "status": agent["status"]
        })
        
    async def demo_student_management(self):
        """演示学生管理"""
        print_header("4. 学生管理")
        
        dao = dao_factory.student()
        
        # 创建学生
        print_info("创建学生...")
        self.student_id = generate_uuid()
        student_data = {
            "id": self.student_id,
            "user_id": "student_001",
            "name": "张三",
            "email": "zhangsan@example.com",
            "profile_data": {
                "major": "计算机科学",
                "grade": "大二",
                "learning_style": "visual"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await dao.insert(student_data)
        print_success(f"创建学生: {student_data['name']} (ID: {self.student_id[:8]}...)")
        
        # 查询学生
        print_info("查询学生...")
        student = await dao.get_by_id(self.student_id)
        print_json({
            "name": student["name"],
            "user_id": student["user_id"],
            "email": student["email"]
        })
        
    async def demo_assignment_and_grading(self):
        """演示作业和批改"""
        print_header("5. 作业与批改")
        
        assignment_dao = dao_factory.assignment()
        submission_dao = dao_factory.submission()
        
        # 创建作业
        print_info("创建作业...")
        assignment_id = generate_uuid()
        assignment_data = {
            "id": assignment_id,
            "course_id": self.course_id,
            "title": "Python基础编程练习",
            "content": "编写一个Python程序，实现计算器功能。",
            "type": "coding",
            "knowledge_points": self.knowledge_points[:2],
            "deadline": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await assignment_dao.insert(assignment_data)
        print_success(f"创建作业: {assignment_data['title']}")
        
        # 创建提交记录
        print_info("创建作业提交...")
        submission_id = generate_uuid()
        submission_data = {
            "id": submission_id,
            "assignment_id": assignment_id,
            "student_id": self.student_id,
            "content": "def add(a, b): return a + b",
            "file_urls": [],
            "annotations": [
                {"line": 1, "type": "info", "content": "建议添加类型注解"}
            ],
            "score": 85.0,
            "feedback": "代码实现正确，建议添加更多注释",
            "status": "graded",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await submission_dao.insert(submission_data)
        print_success(f"创建提交记录，得分: {submission_data['score']}")
        
        # 查询提交
        print_info("查询学生提交...")
        submissions = await submission_dao.list_by_student(self.student_id)
        for s in submissions:
            print(f"  - 作业ID: {s['assignment_id'][:8]}..., 得分: {s.get('score', 'N/A')}")
            
    async def demo_learning_records(self):
        """演示学习记录"""
        print_header("6. 学习记录")
        
        dao = dao_factory.learning_record()
        
        # 创建学习记录
        print_info("创建学习记录...")
        for kp_id in self.knowledge_points[:3]:
            record_id = generate_uuid()
            await dao.insert({
                "id": record_id,
                "student_id": self.student_id,
                "course_id": self.course_id,
                "knowledge_point_id": kp_id,
                "mastery_level": 0.6 + (hash(kp_id) % 30) / 100,  # 随机掌握程度
                "practice_count": 5 + hash(kp_id) % 10,
                "correct_count": 3 + hash(kp_id) % 5,
                "last_practice_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        print_success("创建3条学习记录")
        
        # 查询学习记录
        print_info("查询学习记录...")
        records = await dao.list_by_student(self.student_id, self.course_id)
        for r in records:
            print(f"  - 知识点: {r['knowledge_point_id'][:8]}..., 掌握度: {r.get('mastery_level', 0):.1%}")
            
    async def demo_warnings(self):
        """演示学情预警"""
        print_header("7. 学情预警")
        
        dao = dao_factory.warning()
        
        # 创建预警
        print_info("创建学情预警...")
        warning_id = generate_uuid()
        warning_data = {
            "id": warning_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "level": "medium",
            "type": "low_engagement",
            "description": "学生近期学习活跃度较低，作业提交延迟",
            "knowledge_points": self.knowledge_points[:2],
            "is_resolved": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await dao.insert(warning_data)
        print_success(f"创建预警: {warning_data['description'][:30]}...")
        
        # 查询预警
        print_info("查询学生预警...")
        warnings = await dao.list_by_student(self.student_id)
        for w in warnings:
            print(f"  - 级别: {w['level']}, 类型: {w['type']}, 已解决: {bool(w.get('is_resolved', 0))}")
            
    async def demo_qa_history(self):
        """演示问答历史"""
        print_header("8. 问答历史")
        
        dao = dao_factory.qa_history()
        
        # 创建问答记录
        print_info("创建问答记录...")
        qa_data = [
            {
                "question": "什么是Python的列表推导式？",
                "answer": "列表推导式是Python中一种简洁的创建列表的方式，例如：[x**2 for x in range(10)]"
            },
            {
                "question": "如何定义一个函数？",
                "answer": "使用def关键字定义函数，例如：def my_func(): pass"
            },
            {
                "question": "Python中的装饰器是什么？",
                "answer": "装饰器是一种修改函数行为的语法糖，使用@decorator语法"
            }
        ]
        
        for qa in qa_data:
            await dao.insert({
                "id": generate_uuid(),
                "student_id": self.student_id,
                "course_id": self.course_id,
                "agent_id": self.agent_id,
                "question": qa["question"],
                "answer": qa["answer"],
                "knowledge_points": self.knowledge_points[:1],
                "is_helpful": True,
                "created_at": datetime.utcnow()
            })
            print_success(f"记录问答: {qa['question'][:20]}...")
        
        # 查询问答历史
        print_info("查询问答历史...")
        history = await dao.list_by_student(self.student_id, limit=5)
        for h in history:
            print(f"  Q: {h['question'][:30]}...")
            print(f"  A: {h['answer'][:40]}...")
            print()
            
    async def demo_platform_config(self):
        """演示平台配置"""
        print_header("9. 平台配置")
        
        dao = dao_factory.platform_config()
        
        # 创建平台配置
        print_info("创建平台配置...")
        config_id = generate_uuid()
        await dao.insert({
            "id": config_id,
            "platform": "chaoxing",
            "config": {
                "api_key": "test_key_123",
                "api_secret": "test_secret_456",
                "base_url": "https://api.chaoxing.com",
                "webhook_url": "http://localhost:8003/webhook/chaoxing"
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        print_success("创建超星平台配置")
        
        # 查询配置
        print_info("查询平台配置...")
        config = await dao.get_by_platform("chaoxing")
        if config:
            print_json({
                "platform": config["platform"],
                "is_active": bool(config.get("is_active", 1))
            })
            
    async def show_statistics(self):
        """显示统计数据"""
        print_header("10. 统计数据")
        
        # 统计各表记录数
        tables = [
            ("courses", "课程"),
            ("agents", "智能体"),
            ("knowledge_points", "知识点"),
            ("students", "学生"),
            ("assignments", "作业"),
            ("submissions", "提交记录"),
            ("learning_records", "学习记录"),
            ("warnings", "预警"),
            ("qa_history", "问答历史"),
            ("platform_configs", "平台配置")
        ]
        
        print_info("数据库统计:")
        for table, name in tables:
            sql = f"SELECT COUNT(*) as count FROM {table}"
            async with db_manager.connection.execute(sql) as cursor:
                row = await cursor.fetchone()
                count = row[0] if row else 0
                print(f"  {name}: {count} 条记录")
                
    async def run_all(self):
        """运行所有演示"""
        print_header("EduAgent Platform - Windows Demo")
        print("可嵌入式跨课程AI Agent通用架构平台")
        print("中国大学生服务外包创新创业大赛 A25赛题")
        print()
        
        try:
            # 初始化
            await self.initialize()
            
            # 运行各个演示
            await self.demo_course_management()
            await self.demo_knowledge_management()
            await self.demo_agent_management()
            await self.demo_student_management()
            await self.demo_assignment_and_grading()
            await self.demo_learning_records()
            await self.demo_warnings()
            await self.demo_qa_history()
            await self.demo_platform_config()
            await self.show_statistics()
            
            print_header("演示完成")
            print_success("所有演示已成功运行！")
            print()
            print_info("数据库文件位置: data/eduagent.db")
            print_info("可以使用 SQLite 浏览器查看数据")
            print()
            
        except Exception as e:
            print_error(f"演示出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db_manager.close()


def main():
    """主函数"""
    # 检查Windows系统
    if sys.platform != 'win32':
        print_warning("此演示程序主要针对Windows系统优化")
        print_info("在其他系统上也可以运行，但显示效果可能略有不同")
        print()
    
    # 运行演示
    demo = EduAgentDemo()
    asyncio.run(demo.run_all())
    
    # 等待用户按键
    print()
    input("按回车键退出...")


if __name__ == "__main__":
    main()
