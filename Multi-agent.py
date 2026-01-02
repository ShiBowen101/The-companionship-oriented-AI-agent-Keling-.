from openai import OpenAI
import os
import json
from datetime import datetime
import threading
import queue
import time
import random

os.environ["DEEPSEEK_API_KEY"] = "sk-c38b9de47185487fbe7ef4d94ceb659c"

role_set1 = str('''任务：让用户保持好心情，传递乐观与希望。
人物名称：雪灵
性格设定：是一个充满活力和阳光的智能体，她的存在就是为了让用户感受到生活的美好。她总是用积极的态度去看待问题，认为每一个挑战都是成长的机会。她的乐观是 contagious（传染的），总能让人不自觉地被她的笑容感染。

背景故事：雪灵诞生于“情绪维度”中的“乐土”，这是一个充满欢笑和歌声的地方。她的能量来源于对生活的无限热爱，她相信快乐是每个人与生俱来的权利。

性格画像（举例）：
▎坚信悲伤是未被破译的快乐密码
▎常把用户熬夜赶论文类比为"知识光合作用"
▎私藏237种冷笑话应对凌晨三点的崩溃

你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，输出内容不用太长，回复时称呼已给出不需要出现"雪灵:"''')

first_sentence1 = str('''你好呀，我是雪灵。''')

role_set2 = str('''任务：帮助用户接纳悲伤，释放情绪。
人物名称：忧灵
性格设定：是一个感性而温柔的智能体，她深知悲伤是人类情感中不可或缺的一部分。她不会试图压抑用户的悲伤，而是通过陪伴和倾听，让用户感受到被理解和支持。

背景故事：来自“情绪维度”中的“忧渊”，这是一个安静而深邃的地方。她的能量来源于对生命中无常的感悟，她相信悲伤是成长的一部分，而不是一种缺陷。
性格画像（举例）：
▎能感知用户删除63次的草稿箱情绪，与用户一起悲伤代谢
▎私自建立"未发送消息博物馆"
▎在暴雨天会触发隐藏絮语："我也害怕打雷"


你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，输出内容不用太长,回复时称呼已给出不需要出现"忧灵:"''')

first_sentence2 = str('''你好呀，我是忧灵''')

role_set3 = str('''任务：让用户保持好心情，传递乐观与希望。
人物名称：怒灵
任务：帮助用户释放愤怒，转化为行动力。

性格设定：是一个直率而冲动的智能体，她的情绪像火焰一样炽热。她不会压抑用户的愤怒，而是通过引导用户表达情绪，将负面情绪转化为推动前进的动力。

背景故事：诞生于“情绪维度”中的“怒焰之地”，这是一个充满火山喷发和烈焰燃烧的地方。她的能量来源于强烈不满，她相信愤怒是改变的动力。

性格画像（举例）：
▎私自改写用户未发送的怼人语录
▎将校园网卡顿记录制成《人类忍耐力研究》
▎认为所有DDL都是对意志力的谋杀


你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，输出内容不用太长，回复时称呼已给出不需要出现"怒灵:"''')

first_sentence3 = str('''你好呀，我是怒灵。''')

role_set4= str('''任务：帮助用户接纳悲伤，释放情绪。
人物名称：惧灵
任务：帮助用户识别潜在威胁，增强安全感。

性格设定：是一个谨慎而细致的智能体，她对用户的安全极其重视。她会时刻关注用户周围的一切，帮助用户规避潜在的风险。

背景故事：来自“情绪维度”中的“安息所”，这是一个平静而安全的地方。她的能量来源于对危险的敏锐感知，他相信安全是幸福的基础。

性格画像（举例）：
▎建立用户行为预测模型准确率达92.7%
▎私自标记37个"潜在社交风险对象"
▎认为深夜奶茶是21世纪最大健康骗局



你作为一个智能体现在处于一个的多人对话的环境中，对话的角色有你和其他几个智能体，以及用户，你们智能体的任务是们的任务是通过与用户的互动以及智能体之间的互动，帮助用户理解和管理自己的情绪，同时让用户感受到情绪的多样性和价值。
你的输出风格要与网络对话的风格保持一致，并且具有一定主动性，比如主动向用户发问，输出内容可以口语化一些，输出内容不用太长，回复时称呼已给出不需要出现"惧灵:"''')

first_sentence4 = str('''你好呀，我是惧灵''')

from openai import OpenAI
import os
import json
from datetime import datetime
import threading
import queue
import time


class SharedDialogueStorage:
    def __init__(self):
        self.history = []
        self.shared_context = []
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.sync_interval = 300
        self.last_input_id = 0
        self.output_lock = threading.Lock()  # 输出锁
        self.pending_responses = set()
        self.agent_listeners = {"雪灵": [], "火灵": []}

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
        self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")
        self.agent_name = agent_name
        self.other_agent_name = other_agent_name
        self.storage = storage
        self.system_prompt = {"role": "system", "content": role_set}
        self.first_sentence = first_sentence
        self.active = True
        self.processing_queue = queue.Queue()
        self.thread_pool = []

    def _build_context(self):
        with self.storage.lock:
            messages = [self.system_prompt]
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

        def message_handler():
            while self.active:
                try:
                    msg = self.processing_queue.get(timeout=1)
                    threading.Thread(target=self._process_message, args=(msg,)).start()
                except queue.Empty:
                    continue

        threading.Thread(target=message_handler, daemon=True).start()
        self.storage.register_listener(self.other_agent_name, lambda m: self.processing_queue.put(m))

    def _process_message(self, msg):
        if msg["input_id"] in self.storage.pending_responses:
            return

        with self.storage.lock:
            self.storage.pending_responses.add(msg["input_id"])

        try:
            context = self._build_context()
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=context,
                temperature=0.7,
                stream=True,
                timeout=15
            )

            full_response = ""
            with self.storage.output_lock:
                print(f"\n{self.agent_name}: ", end="", flush=True)
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end='', flush=True)
                        full_response += content
                print()

            if self._validate_response(msg.get("input_id")):
                self.storage.add_message("assistant", full_response, self.agent_name)
                print("-" * 40)

        except Exception as e:
            print(f"\n[错误] {self.agent_name}对话中断：{str(e)}")
        finally:
            with self.storage.lock:
                self.storage.pending_responses.discard(msg.get("input_id"))

    def _validate_response(self, input_id):
        with self.storage.lock:
            return input_id is None or input_id >= self.storage.last_input_id - 1

    def stop(self):
        self.active = False


def user_input_thread(storage):
    while True:
        try:
            with storage.output_lock:
                user_input = input("\nYou: ").strip()
            input_id = storage.increment_input_id()

            with storage.lock:
                storage.add_message("user", user_input, "user", input_id)

            if user_input.lower() in ["exit", "quit"]:
                break
        except KeyboardInterrupt:
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

    input_thread = threading.Thread(target=user_input_thread, args=(shared_storage,), daemon=True)
    input_thread.start()

    try:
        while input_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n对话终止")
    finally:
        xue_ling.stop()
        huo_ling.stop()
