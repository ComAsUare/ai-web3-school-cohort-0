"""
步骤 3: 交互式问答

加载向量库 → 用户输入问题 → 检索 + 生成答案
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qa_chain import interactive_qa


if __name__ == "__main__":
    interactive_qa()
