
class Config:
    SECRET_KEY = 'this is secret string'
    SEND_FILE_MAX_AGE_DEFAULT = 0

    @staticmethod
    def init_app(app):
        pass


config = Config()
