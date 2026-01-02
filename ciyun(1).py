import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 读取Excel文件
df = pd.read_excel('心理健康_合.xlsx')

# 提取评论内容列并强制转换为字符串
comments = df['Column4'].astype(str).tolist()  # 强制类型转换

# 自定义停用词列表（根据数据特点补充）
stopwords = set(['的', '了', '在', '是', '我', '你', '他', '我们', '他们', '自己', '这个',
                 '一种', '没有', '什么', '就是', '可以', '因为', '如果', '怎么', '还是',
                 '可能', '真的', '不要', '这个', '这样', '一个', '吗', '啊', '呢', '哦', 'nan',
                 '但是', '现在', '时候', '知道', '这种', '很多', '觉得', '其实', '只是', '一次', 'doge',
                 '有点', '是不是', '还有', '突然', '并且', '最后', '然后', '感觉', '觉得', '然后', '知道', '这些',
                 '这种', '那种', '特别', '而且', '知道', '时候', '现在', '但是', '一些', '其实', '一点', '这么', '已经',
                 '之后', '喜欢', 'up', '一下', '的话', '或者', '所以', '那个', '虽然', '不是', '出来', '一样', '开始',
                 '孩子'])


# 数据清洗和分词
def process_text(text):
    # 处理浮点数的nan字符串和特殊字符
    text = text.replace('_x000D_', '').replace('\r', '').replace('\n', '')
    text = text.strip()  # 移除首尾空白
    # 过滤空内容和无效字符串
    if text in ['', 'nan', 'None']:
        return []
    # 分词处理
    words = jieba.cut(text)
    # 过滤停用词和单字词
    return [word for word in words if len(word) > 1 and word not in stopwords]


# 生成所有词语列表
all_words = []
for comment in comments:
    all_words.extend(process_text(comment))

# 统计词频（过滤低频词）
word_counts = Counter(all_words)
top_words = {k: v for k, v in word_counts.items() if v > 2}  # 仅保留出现3次以上的词

# 生成词云
font_path = 'msyh.ttc'
wc = WordCloud(
    font_path=font_path,
    background_color='white',
    max_words=200,
    width=1000,
    height=700,
    collocations=False
)

wc.generate_from_frequencies(top_words)

# 显示并保存词云
plt.figure(figsize=(12, 8))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig('wordcloud.png', dpi=300)
plt.show()
