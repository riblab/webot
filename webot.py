import werobot

from flask import Flask
from werobot.contrib.flask import make_view

# 输入微信公众平台请求凭证
robot = werobot.WeRoBot(token='riblab')         # 写入服务器配置填写的 Token
robot.config["APP_ID"] = "******"               # 写入开发者ID
robot.config["ENCODING_AES_KEY"] = "******"     # 写入服务器配置填写的 EncodingAESKey

# 被关注
@robot.subscribe
def subscribe(message):
    return '''欢迎关注'''

# 建立一个消息处理装饰器，当 handler 无论收到何种信息时都运行 hello 函数
@robot.handler
def hello(message):
    return '自动回复'

app = Flask(__name__)
app.add_url_rule(rule='/wechat_rib/',        # WeRoBot 挂载地址，即项目目录名
                 endpoint='webot',            # Flask 的 endpoint
                 view_func=make_view(robot),
                 methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run()
