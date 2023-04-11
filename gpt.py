# 导入模块
import openai

# 设置api token和组织id
openai.api_key = "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"

class ChatSession:
    def __init__(self):
        # 定义一个全局变量messages，用来存储聊天记录
        self.messages = [{"role": "system", "content": "你是一个疲劳缓解助手，需要给用户生成一些符合用户口味的歌曲、小说、笑话等内容来为他们缓解疲劳"}]

    def chat(self, question):
        # 在列表末尾添加用户最新输入的问题
        self.messages.append({"role": "user", "content": question})
        
        # 调用openai接口获取回答
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        answer = completion.choices[0].message.content
        
        # answer = re.sub('\s+',"",answer)
        
        print("------")
        
        print(answer)
        
        print("------")
        
        # 在列表末尾添加gpt最新输出的回答
        self.messages.append({"role": "assistant", "content": answer})
        
        # 返回json对象只包含answer键值对
        return answer
