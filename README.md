# webot   wechat:riblab

## CentOS7.6 + Nginx + Gunicorn + webot 部署 Flask 搭建微信公众号后台

#### 



**1.安装python3**

> 由于腾讯云的CentOS自带python3.6.8不需要二次安装
>
> 手动安装指令提前安装python脚手架内置环境
>
> `yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel libffi-devel`
>
> ```linux
> # 下载 python 3.6.8 的安装包
> wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
> 
> # 解压 Python-3.6.8.tgz
> tar -zxvf Python-3.6.8.tgz
> 
> # 创建一个新文件夹用于存放安装文件
> mkdir /usr/local/python3
> 
> # 执行配置文件，编译安装
> cd Python-3.6.8
> ./configure --prefix=/usr/local/python3
> make && make install
> 
> # 建立软连接（相当于 Windows 系统的环境变量）
> ln -s /usr/local/python3/bin/python3.6 /usr/bin/python3
> ln -s /usr/local/python3/bin/pip3.6 /usr/bin/pip3
> ```



**2.添加新用户**

```linux
adduser riblab                # 创建新用户
passwd riblab                 # 给新用户设置密码
usermod -aG wheel riblab      # 给用户获取root权限
su riblab                     # 切换至新用户
```



**3.搭建虚拟环境**

- `riblab` 是我创建的用户名。
- 此时 `/home` 路径下会生成以用户名命名的文件夹
- cd 到 /home/riblab中

```linux
mkdir wechat_rib              # 新建项目文件夹
python3 -m venv env_wp           # 新建虚拟环境
```



> 运行 `ll` 命令确认 `env_wp` 目录权限所有者为用户，而非 `root`。若 `env_wp` 目录权限所有者为`root`却以用户的身份进入虚拟环境，`pip` 安装依赖包或其他操作可能会引起权限报错 `Permission denied`，请务必注意。
>
> 进入虚拟环境，运行 `source ./env_wp/bin/activate`。
>
> 退出虚拟环境，运行 `deactivate`。
>
> 停用环境后需要完全删除环境，则可以运行 `rm -rf env_wp`。



**4.安装项目依赖**

- `pip3 install flask gunicorn werobot cryptography  # 虚拟环境中 安装 gunicorn werobot cryptography`
- 执行pip3 list 可查看依赖安装情况
- 如安装失败，先更新pip版本。
- ` pip3 install --upgrade pip`
- ` pip install --upgrade pip`



**5.安装 Nginx**

- 由于在次级用户下，配置nginx一直报错。
- 此时切换至root用户操作。
- 安装Nginx： `yum install nginx -y`
- 添加Nginx 配置文件 

```linux
sudo vim /etc/nginx/conf.d/wechat_rib.conf
```

```html
server {
    server_name riblab.cn;  # 域名/IP 均可
    listen 80;
 		access_log  /var/log/nginx/access.log;    # 设置正常通信日志
		error_log  /var/log/nginx/error.log;      # 设置报错日志
		
		
    location /wechat_rib/ {
        proxy_pass_header Server;  
        proxy_redirect off;
        proxy_pass http://127.0.0.1:8000; # 反向代理 Gunicorn 本地的服务地址

				proxy_set_header   X-Real-IP           $remote_addr;
        proxy_set_header   Host                $host;
        proxy_set_header   X-Forwarded-For     $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto   $scheme;
    }
}
```





**6.启动 Nginx**

```linux
sudo nginx -t                           # 检查 nginx 的 .conf 配置文件的有效性

# 返回如下信息显示无异常
###########################
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
###########################
```

```linux
sudo systemctl start nginx              # 运行 nginx 服务
sudo systemctl enable nginx             # 启动 nginx 服务
```

```linux
sudo systemctl status nginx             # 查看 nginx 服务状态

# 若返回如下信息则 nginx 无异常
###########################
● nginx.service - The nginx HTTP and reverse proxy server
   Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: disabled)
  Drop-In: /etc/systemd/system/nginx.service.d
           └─override.conf
   Active: active (running) since Thu 2019-11-21 11:54:11 CST; 21s ago
  Process: 10679 ExecStartPost=/bin/sleep 0.1 (code=exited, status=0/SUCCESS)
  Process: 10676 ExecStart=/usr/sbin/nginx (code=exited, status=0/SUCCESS)
  Process: 10672 ExecStartPre=/usr/sbin/nginx -t (code=exited, status=0/SUCCESS)
  Process: 10671 ExecStartPre=/usr/bin/rm -f /run/nginx.pid (code=exited, status=0/SUCCESS)
 Main PID: 10678 (nginx)
   CGroup: /system.slice/nginx.service
           ├─10678 nginx: master process /usr/sbin/nginx
           └─10680 nginx: worker process

Nov 21 11:54:11 simple systemd[1]: Stopped The nginx HTTP and reverse proxy server.
Nov 21 11:54:11 simple systemd[1]: Starting The nginx HTTP and reverse proxy server...
Nov 21 11:54:11 simple nginx[10672]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
Nov 21 11:54:11 simple nginx[10672]: nginx: configuration file /etc/nginx/nginx.conf test is successful
Nov 21 11:54:11 simple systemd[1]: Started The nginx HTTP and reverse proxy server.
###########################
```

- 若停止 Nginx 服务，可使用 `sudo service nginx stop`。
- 即使在 `/etc/nginx/conf.d` 中，也不要重复设置 server ，尤其是同一个 ip ，否则会造成地址冲突，导致服务启动失败。
- 每次修改 nginx 配置文件后，无需 先 `stop` 后 `restart` 再 `enable` ，可直接 `sudo nginx -s reload` 热启动，重新加载新配置文件。
- 若 nginx 服务状态信息倒数第二行出现报错提示 `Failed to read PID from file /run/nginx.pid: Invalid argument`,在网上找到了比较靠谱的解释。产生的原因是 nginx 启动需要一点点时间，而 systemd 在 nginx 完成启动前就去读取 pid file，导致获取失败。解决方法如下。

```linux
# 先退出虚拟环境，切换成 root 管理员
deactivate
su root

# 在该路径新建名为 nginx.service.d 的文件夹
mkdir -p /etc/systemd/system/nginx.service.d

# 在刚刚新建的文件夹中新建名为 override.conf 的配置文件
vim /etc/systemd/system/nginx.service.d/override.conf

# 文件中键入如下内容后，:wq 保存退出
[Service]
ExecStartPost=/bin/sleep 0.1

# 使服务文件生效
systemctl daemon-reload

# 重启 nginx 服务
systemctl restart nginx.service

# 重新查看 nginx 状态, successful
sudo systemctl status nginx
##################
nginx: configuration file /etc/nginx/nginx.conf test is successful
##################
```



**7.写一个简单的 Python 后端**

 vim 一个 python 文件 `sudo vim /home/riblab/webot.py`

```python
import werobot
from flask import Flask
from werobot.contrib.flask import make_view

# 输入微信公众平台请求凭证
robot = werobot.WeRoBot(token='***')         # 写入服务器配置填写的 Token
robot.config["APP_ID"] = "***"               # 写入开发者ID
robot.config["ENCODING_AES_KEY"] = "***"     # 写入服务器配置填写的 EncodingAESKey

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
```

**8.启动 Gunicorin 服务器**

```linux
gunicorn -w 1 -b 127.0.0.1:8000 webot:app

# 参数解释
# -w 1: -w 等价于 --workers, 后接 INT，用于处理工作进程的数量，为正整数，默认为 1
# -b 127.0.0.1:8000: -b 等价于 --bind, 后接 ADDRESS， IP 加端口，绑定运行的主机
# first app: 之前的webot.py文件
# second app: flask 应用
```





**此时如果正确挂载则访问 http://你的ip或域名/wechat_rib/ 即可看到「这是一个 [WeRoBot](https://github.com/whtsky/WeRoBot/) 应用」提示页面**







#### **碰见的问题及解决方案**	

**Q1:python3 及 python2 版本替换**

A1:直接替换 /usr/bin 下的 python

 `rm /usr/bin/python`

 `ln -s /usr/bin/python3.6 /usr/bin/python`

> 此时使用 **yum** 会报错，因为 yum 是使用 Python2 实现的，默认的 python 已经被改成 python3.6 了(上面创建软链接时) ，需要将 yum 使用的 Python 版本改回 python2.7 。 
>
> > ` vim /usr/bin/yum`
> >
> > */usr/bin/python 改为 /usr/bin/python2.7*
> >
> > `vim /usr/libexec/urlgrabber-ext-down`
> >
> > */usr/bin/python 改为 /usr/bin/python2.7*



**Q2:Tree 缺失**

A2: `yum install tree -y`



**Q3:vim 相关**

A3:

> vim操作指南
>
> i：编辑模式
>
> Esc：退出操作模式
>
> 「：」：编辑器命令
>
> wq:保存退出	

**Q4:Nginx 操作相关**



```linux
sudo nginx -t                           # 检查 nginx 的 .conf 配置文件的有效性
sudo systemctl start nginx              # 运行 nginx 服务
sudo systemctl enable nginx             # 启动 nginx 服务
sudo systemctl status nginx             # 查看 nginx 服务状态
sudo service nginx stop                 # 停止 nginx 运行
systemctl restart nginx.service         # 重启 nginx 服务
```



**Q5:Gunicorin 相关**

```
pstree -ap|grep gunicorn           # 查看 gunicorn 进程树
kill -HUP ***(编号)                 # 重启 gunicorn 线程
kill -9 ***(编号)										# 关闭 gunicorn 线程
```
