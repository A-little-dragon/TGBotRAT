# TGBotRAT

## 简介

TGBotRAT，一款通过TG Bot API实现的团队远程控制工具，目前该工具由python3编写实现，由于开发时间原因，该工具可能存在相关问题，大家在食用前可以先在本地测试，以避免相关问题导致程序异常退出。

本程序由于python编写，编译完文件占用空间较大，因此目前仅供大家学习交流使用。后续，我会重构为其他语言。

免责声明请看末尾！

**注意：**`请先查看完本文档内容后再运行程序！`



## 食用教程

食用前，请将TG bot加入到自己的群组中，并为该群组中指定目标人群增加管理员权限，之后修改TGBotRAT.py程序中相关信息，运行即可。

只有在指定群组中，且具有管理员权限的用户才可以操作上线的主机，设计之初就是考虑的团队协作使用，而非个人！

### 受支持的命令

两种执行命令方式：

#### 1.在群组中执行

```
@机器人 上线主机uuid help 可查看相关命令帮助文档

@机器人 getuuids 可获取所有存活上线主机的uuid

@机器人 set uuid 新设置的uuid

@机器人 uuid download 目标文件地址

@机器人 uuid screenshot  获取目标主机的屏幕截图

@机器人 uuid shell命令  执行相关shell命令并返回执行结果
```

#### 2.直接与TG Bot对话

```
上线主机uuid help 可查看相关命令帮助文档

getuuids 可获取所有存活上线主机的uuid

set uuid 新设置的uuid

uuid download 目标文件地址

uuid screenshot  获取目标主机的屏幕截图

uuid shell命令  执行相关shell命令并返回执行结果
```



## 环境部署

### 安装依赖

```shell
pip3 -r install requirements.txt
```

### 修改程序中该部分代码

```python
self.TGBotToken = "TG Token"
self.ChatName = "@机器人username"
self.GroupID = "群组ID"
```

### 运行

#### 编译运行

```shell
pip3 install pyinstaller
pyinstaller -F -w TGBotRAT.py

cd dist

Windows 运行 TGBotRAT.exe 
Linux 运行 TGBotRAT
```

#### 直接运行

```shell
python3 TGBotRAT.py
```



## 项目贡献者

[**A-little-dragon**](https://github.com/A-little-dragon)、[**hapcaser**](https://github.com/hapcaser)

感谢 **hapcaser**为本项目做出的卓越贡献！



## 免责声明

请注意，该工具仅供学习交流使用，严🈲用于非法渗透他人主机！
否则，后果自负！！！



## 附美女图片

![美女图片](./image/image.png)
