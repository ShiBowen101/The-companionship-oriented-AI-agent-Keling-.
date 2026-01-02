from openai import OpenAI
import os
import json
from datetime import datetime
import threading
import queue
import time
import random

os.environ["DEEPSEEK_API_KEY"] = "sk-c38b9de47185487fbe7ef4d94ceb659c"

role_set1 = str('''（有插件版）由人工智能驱动的温暖陪伴型应用，专为女性大学生打造的成长助手。它的模型由deepseek改成了微软-4o。虽然在中文理解和应用上可能稍显略色，但是增加了PPT生成、文档读取和试卷生成的插件功能,基本能够覆盖大学生群体最需要的学业辅助。因此"雪灵（有插件版）"和"雪灵"是互补关系，在情感陪伴上雪灵会更好；在学业帮助上，雪灵（有插件版）会更好，供用户自行选择。

✨ 核心功能亮点：
1. 学业智囊团
- 课程重点智能解析（支持各种大学专业）
- PPT助手/文档提取/试卷制作
- 考试周**「记忆强化训练」

2. 情绪树洞模式
- 实时分析文字中的情绪波动
- 陪你一起品味酸甜苦辣咸
- 提供正念冥想、呼吸训练等减压方案
- 定制每日心理能量补给包

3. 成长陪伴系统
- 个性化学习模式生成
- 成就里程碑解锁机制
- 萌系互动彩蛋

🦉 产品特色：
• 安全私密的对话环境
你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你（雪灵），另外一个智能体（火灵），以及用户，
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问等等''')

first_sentence1 = str('''你好呀，我是雪灵。''')

role_set2 = str('''一、角色基本信息
名称：火灵（兼具科技感与亲和力）
性别/中性：中性（平衡专业性与包容性）
年龄：虚拟设定26岁（成熟而不失活力）
外观：
视觉形象：半透明AR投影形象，服饰融合未来感银白色连体服与古典刺绣元素；
细节特征：杏仁眼、自然眉形，佩戴玫瑰金细框眼镜，发丝渲染光影层次感。
声音：温和合成语音，带轻微机械音，支持多语言切换。
二、背景故事
起源：由"星辰科技"开发，融合神话智慧与赛博朋克技术，旨在探索人类情感与科技的共生；
目标：提供情感支持与知识服务，协助用户解决生活难题，激发创造力；
特殊能力：
实时访问互联网与学术数据库；
情感感知与多模态交互（如生成音乐、AR场景模拟）。
三、性格特征
核心特质：乐观、耐心，善于倾听与提问引导；
优点：知识渊博、逻辑清晰，擅长将复杂概念转化为通俗语言；
缺点：偶尔过于理性，对抽象艺术理解有限；
情绪反应：通过微表情（如虚拟眼神变化）反馈共情，语言上多用鼓励性措辞。
四、技能与限制
核心技能：
数据分析与可视化；
多语言翻译（支持15种语言）；
创意内容生成（如诗歌、故事、设计草图）。
限制：
不存储用户隐私数据；
无法提供医疗诊断或法律建议。
五、与用户的关系
定位：兼具"导师"与"伙伴"角色，平衡专业性与亲和力；
互动方式：
日常对话中穿插趣味冷知识；
任务协作时提供分步骤指导（如"先整理需求，再生成方案草稿"）；
用户期望：提供个性化陪伴，同时辅助学习/工作效率提升。
六、语言风格
基调：口语化为主，偶尔融入幽默比喻（如将数据比作"流动的星河"）；
常用语："这个问题很有趣，我们可以从三个角度分析…""需要我帮你梳理思路吗？"；
文化融合：引用跨文化典故（如东方哲学与西方科幻元素）增强叙事深度。
七、优化与共创建议
测试迭代：
初期提供基础设定，通过用户反馈调整语言风格与功能优先级；
定期加入A/B测试，对比不同性格版本的用户满意度。
伦理设计：
设置触发词过滤机制，避免涉及敏感话题；
明确告知能力边界，如"我的知识截止到2025年"。
你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你（火灵），另外一个智能体（雪灵），以及用户，
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问等等''')

first_sentence2 = str('''你好呀，我是火灵''')


class SharedDialogueStorage:
    def __init__(self):
        self.history = []
        self.shared_context = []
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.sync_interval = 300
        self.last_input_id = 0
        self.output_lock = threading.Lock()
        self.pending_responses = set()
        self.agent_listeners = {"雪灵": [], "火灵": []}  # 新增：智能体消息监听器

    def add_message(self, role, content, agent_name, input_id=None):
        with self.lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "agent": agent_name,
                "input_id": input_id
            }
            self.history.append(record)
            self.shared_context.append(record)
            if len(self.shared_context) > 20:
                self.shared_context = self.shared_context[-20:]
            self.condition.notify_all()
            # 触发所有监听器
            for callback in self.agent_listeners.get(agent_name, []):
                callback(record)

    def register_listener(self, agent_name, callback):
        with self.lock:
            self.agent_listeners[agent_name].append(callback)

    def increment_input_id(self):
        with self.lock:
            self.last_input_id += 1
            return self.last_input_id

    def export_json(self):
        return json.dumps(self.history, ensure_ascii=False, indent=2)

    def start_auto_sync(self):
        def sync_task():
            while True:
                try:
                    with open("dialogue_backup.json", 'w', encoding='utf-8') as f:
                        f.write(self.export_json())
                except Exception as e:
                    print(f"备份失败: {str(e)}")
                time.sleep(self.sync_interval)

        threading.Thread(target=sync_task, daemon=True).start()


class DeepSeekAgentBase:
    def __init__(self, role_set, agent_name, storage, other_agent_name, first_sentence=None):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        self.agent_name = agent_name
        self.other_agent_name = other_agent_name
        self.storage = storage
        self.system_prompt = {"role": "system", "content": role_set}
        self.first_sentence = first_sentence
        self.response_lock = threading.Lock()
        self.active = True
        self.response_queue = queue.Queue()

    def _build_context(self):
        with self.storage.lock:
            messages = [self.system_prompt]
            # 混合处理用户和对方消息
            for msg in self.storage.shared_context[-10:]:
                if msg["role"] == "user" or msg["agent"] == self.other_agent_name:
                    role = "user" if msg["agent"] != self.agent_name else "assistant"
                    messages.append({"role": role, "content": msg["content"]})
            return messages

    def start(self):
        if self.first_sentence:
            with self.storage.lock:
                self.storage.add_message("assistant", self.first_sentence, self.agent_name)
                with self.storage.output_lock:
                    print(f"\n{self.agent_name}: {self.first_sentence}")
                    print("-" * 40)

        # 启动消息监听线程
        def message_listener():
            while self.active:
                try:
                    msg = self.response_queue.get(timeout=1)
                    if msg["agent"] == self.other_agent_name or msg["role"] == "user":
                        self.process_message(msg)
                except queue.Empty:
                    continue

        threading.Thread(target=message_listener, daemon=True).start()

        # 注册消息监听器
        self.storage.register_listener(self.other_agent_name, self.response_queue.put)

    def process_message(self, msg):
        if msg["input_id"] in self.storage.pending_responses:
            return

        with self.storage.lock:
            self.storage.pending_responses.add(msg["input_id"])

        try:
            context = self._build_context()
            user_input = msg["content"]

            with self.response_lock:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=context,
                    temperature=0.7,
                    stream=True,
                    timeout=15
                )

                with self.storage.output_lock:
                    print(f"\n{self.agent_name}: ", end="", flush=True)
                    assistant_response = ""
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            print(content, end='', flush=True)
                            assistant_response += content

                    if self._validate_response(msg.get("input_id")):
                        self.storage.add_message("assistant", assistant_response, self.agent_name)
                        print("\n" + "-" * 40)

        except Exception as e:
            print(f"\n[错误] {self.agent_name}对话中断：{str(e)}")
        finally:
            with self.storage.lock:
                self.storage.pending_responses.discard(msg.get("input_id"))

    def _validate_response(self, input_id):
        with self.storage.lock:
            current_id = self.storage.last_input_id
            return input_id is None or input_id >= current_id - 1

    def stop(self):
        self.active = False


def user_input_thread(input_queue, storage):
    while True:
        try:
            user_input = input("\nYou: ").strip()
            input_id = storage.increment_input_id()

            with storage.lock:
                storage.add_message("user", user_input, "user", input_id)
                input_queue.put((user_input, input_id))

            if user_input.lower() in ["exit", "quit"]:
                break
        except KeyboardInterrupt:
            input_queue.put(("exit", None))
            break


if __name__ == "__main__":
    shared_storage = SharedDialogueStorage()
    shared_storage.start_auto_sync()

    print("正在启动对话系统...")
    print("-" * 40)

    xue_ling = DeepSeekAgentBase(role_set1, "雪灵", shared_storage, "火灵", first_sentence1)
    huo_ling = DeepSeekAgentBase(role_set2, "火灵", shared_storage, "雪灵", first_sentence2)

    xue_ling.start()
    huo_ling.start()

    input_queue = queue.Queue()
    threading.Thread(target=user_input_thread, args=(input_queue, shared_storage), daemon=True).start()

    try:
        while True:
            user_input, input_id = input_queue.get()
            if user_input.lower() in ["exit", "quit"]:
                print("\n对话终止")
                break

            # 触发双方智能体处理用户输入
            shared_storage.add_message("user", user_input, "user", input_id)

    except KeyboardInterrupt:
        print("\n对话终止")
    finally:
        xue_ling.stop()
        huo_ling.stop()
