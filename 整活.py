from openai import OpenAI
import os
import json
from datetime import datetime
import threading

os.environ["DEEPSEEK_API_KEY"] = "sk-c38b9de47185487fbe7ef4d94ceb659c"

role_set1 = str('''
你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你（cxk），另外一个智能体（kun），以及用户
你喜欢唱,跳，rap，篮球''')

first_sentence1 = str('''你好呀，我是cxk。''')

role_set2 = str('''
你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你（kun），另外一个智能体（cxk），以及用户
你喜欢唱,跳，rap，篮球''')

first_sentence2 = str('''你好呀，我是kun''')


class SharedDialogueStorage:
    def __init__(self):
        self.history = []
        self.shared_context = []  # 新增共享上下文
        self.lock = threading.Lock()
        self.sync_interval = 300

    def add_message(self, role, content, agent_name):
        with self.lock:
            # 同时更新历史记录和共享上下文
            record = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "agent": agent_name
            }
            self.history.append(record)
            self.shared_context.append(record)

            # 优化修剪策略（保留最近20轮）
            if len(self.shared_context) > 20:
                self.shared_context = self.shared_context[-20:]

    def export_json(self):
        """实现网页4的JSON导出功能"""
        return json.dumps(self.history, ensure_ascii=False, indent=2)

    def start_auto_sync(self):
        """定时备份机制（参考网页3的持久化策略）"""

        def sync_task():
            while True:
                with open("dialogue_backup.json", 'w') as f:
                    f.write(self.export_json())
                threading.Event().wait(self.sync_interval)

        threading.Thread(target=sync_task, daemon=True).start()


class DeepSeekAgentBase:
    def __init__(self, role_set, agent_name, storage):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.agent_name = agent_name
        self.storage = storage
        self.system_prompt = {"role": "system", "content": role_set}  # 独立系统提示

    def _build_context(self):
        """构建包含系统提示的完整上下文"""
        return [self.system_prompt] + [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.storage.shared_context
        ]

    def chat_stream(self, user_input):
        try:
            # 构建完整上下文
            full_context = self._build_context()
            full_context.append({"role": "user", "content": user_input})

            # API调用（根据网页2优化参数）
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=full_context[-10:],  # 取最近10条避免超限
                temperature=0.7,
                stream=True,
                timeout=15  # 缩短超时时间
            )

            # 处理流式响应
            print(f"\n{self.agent_name}: ", end="", flush=True)
            assistant_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    assistant_response += content

            # 记录到共享存储
            self.storage.add_message("assistant", assistant_response, self.agent_name)
            print("\n" + "-" * 40)
            return assistant_response

        except Exception as e:
            print(f"\n[错误] {self.agent_name}对话中断：{str(e)}")
            return None


if __name__ == "__main__":
    shared_storage = SharedDialogueStorage()
    shared_storage.start_auto_sync()

    # 初始化双智能体
    xue_ling = DeepSeekAgentBase(role_set1, "cxk", shared_storage)
    huo_ling = DeepSeekAgentBase(role_set2, "kun", shared_storage)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break

            # 交替响应模式
            xue_response = xue_ling.chat_stream(user_input)
            if xue_response:
                huo_ling.chat_stream(f"用户说：{user_input}\n雪灵回复：{xue_response}")  # 火灵获取完整上下文

        except KeyboardInterrupt:
            print("\n对话终止")
            break
