
class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    AIRTABLE_KEY = "keyacSDzFPmDJAy3f"

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}
