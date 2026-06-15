"""Debug LLM JSON responses."""
from openai import OpenAI
import json, re
client = OpenAI(api_key='sk-2cb22bb7c7e94285bca26c9077054995', base_url='https://api.deepseek.com/v1')

SYSTEM = """你是意图分类器。分析用户输入，返回纯JSON：
{"type":"business|conversational","scene":"ad_placement|content|create|ecommerce|data_analysis|diagnosis|","reply":"中文回复"}
对话类(reply必须写)：问候、询问你是谁、询问功能、感谢、闲聊。
业务类：用户明确要做什么。只输出JSON。"""

tests = ['你有什么功能', '你好', '检查ROI', '帮我优化投放']
for t in tests:
    r = client.chat.completions.create(model='deepseek-chat',
        messages=[{'role':'system','content':SYSTEM},{'role':'user','content':t}],
        temperature=0.1, max_tokens=200)
    raw = r.choices[0].message.content
    print('---', t, '---')
    print('RAW:', raw[:200])
    try:
        text = raw.strip()
        if '```' in text:
            m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if m: text = m.group(1).strip()
        m2 = re.search(r'\{.*\}', text, re.DOTALL)
        if m2: text = m2.group(0)
        d = json.loads(text)
        print('OK:', d['type'], d.get('scene','-'))
    except Exception as e:
        print('FAIL:', e)
    print()
