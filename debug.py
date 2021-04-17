from config import Config


class Debug:
    @staticmethod
    def log(message):
        if Config.DEBUG:
            print(message)
