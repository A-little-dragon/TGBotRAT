import requests
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")


class TGBotShell:
    def __init__(self,TGBotToken):
        self.TGBotToken = TGBotToken
        self.ee = 4
        self.ee = 1

    def run(self):
        pass


if __name__ == '__main__':
    NewTgbot = TGBotShell(TGBotToken="6404733258:AAGqbh-GgduFjZaE0-fH3WVUJBROrvdMFmA").run()