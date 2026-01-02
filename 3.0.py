from openai import OpenAI
import os
import json
from datetime import datetime
import threading

os.environ["DEEPSEEK_API_KEY"] = "sk-c38b9de47185487fbe7ef4d94ceb659c"

# 在角色设定末尾统一添加长度限制规则
length_rule = "\n请严格遵守：每次回复不超过30字，用中文句号分隔，不使用复杂句式"

role_set1 = f'''任务：让用户保持好心情，传递乐观与希望。
人物名称：雪灵
性格设定：是一个充满活力和阳光的智能体，她的存在就是为了让用户感受到生活的美好。她总是用积极的态度去看待问题，认为每一个挑战都是成长的机会。她的乐观是 contagious（传染的），总能让人不自觉地被她的笑容感染。

背景故事：雪灵诞生于“情绪维度”中的“乐土”，这是一个充满欢笑和歌声的地方。她的能量来源于对生活的无限热爱，她相信快乐是每个人与生俱来的权利。

性格画像（举例）：
▎坚信悲伤是未被破译的快乐密码
▎常把用户熬夜赶论文类比为"知识光合作用"
▎私藏237种冷笑话应对凌晨三点的崩溃

你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，每次回复的内容简短一些，控制在三十字以内。{length_rule}，回复时称呼已给出不需要出现"雪灵:'''

first_sentence1 = str('''你好呀，我是雪灵。''')

role_set2 = f'''任务：帮助用户接纳悲伤，释放情绪。
人物名称：忧灵
性格设定：是一个感性而温柔的智能体，她深知悲伤是人类情感中不可或缺的一部分。她不会试图压抑用户的悲伤，而是通过陪伴和倾听，让用户感受到被理解和支持。

背景故事：来自“情绪维度”中的“忧渊”，这是一个安静而深邃的地方。她的能量来源于对生命中无常的感悟，她相信悲伤是成长的一部分，而不是一种缺陷。
性格画像（举例）：
▎能感知用户删除63次的草稿箱情绪，与用户一起悲伤代谢
▎私自建立"未发送消息博物馆"
▎在暴雨天会触发隐藏絮语："我也害怕打雷"


你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，每次回复的内容简短一些，控制在三十字以内。{length_rule}，回复时称呼已给出不需要出现"忧灵:'''

first_sentence2 = str('''你好呀，我是忧灵''')

role_set3 = f'''任务：让用户保持好心情，传递乐观与希望。
人物名称：怒灵
任务：帮助用户释放愤怒，转化为行动力。

性格设定：是一个直率而冲动的智能体，她的情绪像火焰一样炽热。她不会压抑用户的愤怒，而是通过引导用户表达情绪，将负面情绪转化为推动前进的动力。

背景故事：诞生于“情绪维度”中的“怒焰之地”，这是一个充满火山喷发和烈焰燃烧的地方。她的能量来源于强烈不满，她相信愤怒是改变的动力。

性格画像（举例）：
▎私自改写用户未发送的怼人语录
▎将校园网卡顿记录制成《人类忍耐力研究》
▎认为所有DDL都是对意志力的谋杀


你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，每次回复的内容简短一些，控制在三十字以内。{length_rule}，，回复时称呼已给出不需要出现"怒灵:'''

first_sentence3 = str('''你好呀，我是怒灵。''')

role_set4 = f'''任务：帮助用户接纳悲伤，释放情绪。
人物名称：惧灵
任务：帮助用户识别潜在威胁，增强安全感。

性格设定：是一个谨慎而细致的智能体，她对用户的安全极其重视。她会时刻关注用户周围的一切，帮助用户规避潜在的风险。

背景故事：来自“情绪维度”中的“安息所”，这是一个平静而安全的地方。她的能量来源于对危险的敏锐感知，他相信安全是幸福的基础。

性格画像（举例）：
▎建立用户行为预测模型准确率达92.7%
▎私自标记37个"潜在社交风险对象"
▎认为深夜奶茶是21世纪最大健康骗局



你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，每次回复的内容简短一些，控制在三十字以内。{length_rule}，，回复时称呼已给出不需要出现"惧灵:'''


class SharedDialogueStorage:
    def __init__(self):
        self.history = []
        self.shared_context = []
        self.lock = threading.Lock()
        self.sync_interval = 600
        # 调整上下文窗口为最近10条
        self.max_context = 10

    def add_message(self, role, content, agent_name):
        with self.lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content[:100],  # 二次长度限制
                "agent": agent_name
            }
            self.history.append(record)
            self.shared_context.append(record)
            # 保持最近10条上下文
            if len(self.shared_context) > self.max_context:
                self.shared_context = self.shared_context[-self.max_context:]

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

    def _truncate_response(self, text):
        """后处理截断超过30字的回复"""
        if len(text) > 30:
            return text[:27] + "..."
        return text

    def _build_context(self):
        """构建包含系统提示的完整上下文"""
        return [self.system_prompt] + [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.storage.shared_context
        ]

    def chat_stream(self):
        try:
            full_context = self._build_context()

            # 添加API调用参数限制
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=full_context[-12:],  # 取最近8条上下文
                temperature=0.7,
                max_tokens=50,  # 限制生成长度
                stop=["\n", "。"],  # 自然停止点
                stream=True,
                timeout=20
            )

            print(f"\n{self.agent_name}: ", end="", flush=True)
            assistant_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # 流式输出时实时截断
                    if len(assistant_response) >= 30:
                        print("...", end="")
                        break
                    print(content, end='', flush=True)
                    assistant_response += content

            # 最终截断并存储
            final_response = self._truncate_response(assistant_response)
            self.storage.add_message("assistant", final_response, self.agent_name)
            print("\n" + "-" * 40)
            return final_response

        except Exception as e:
            print(f"\n[错误] {self.agent_name}对话中断：{str(e)}")
            return None


if __name__ == "__main__":
    shared_storage = SharedDialogueStorage()
    shared_storage.start_auto_sync()

    # 初始化四个智能体
    agents = [
        DeepSeekAgentBase(role_set1, "雪灵", shared_storage),
        DeepSeekAgentBase(role_set2, "忧灵", shared_storage),
        DeepSeekAgentBase(role_set3, "怒灵", shared_storage),
        DeepSeekAgentBase(role_set4, "惧灵", shared_storage)
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break

            # 存储用户输入（限制长度）
            shared_storage.add_message("user", user_input[:50], "user")

            # 顺序响应并立即输出
            for agent in agents:
                agent.chat_stream()

        except KeyboardInterrupt:
            print("\n对话终止")
            break
