import os

LOGS = '/.logs'
CONFIG_FILE = '/config.json'
DB_FILE = '/data/db.db'
MIGRATION_FOLDER = '/data/migrations'
BOT_TOKEN = os.getenv('BOT_TOKEN', None)

if os.getenv("ENVIRONMENT", 'dev') == 'dev':
    LOGS = f'{os.environ["HOME"]}/PycharmProjects/DaDogs/logs/common.logs'
    CONFIG_FILE = f'{os.environ["HOME"]}/PycharmProjects/DaDogs/config/config.json'
    DB_FILE = f'{os.environ["HOME"]}/PycharmProjects/DaDogs/data/db.db'
    MIGRATION_FOLDER = f'{os.environ["HOME"]}/PycharmProjects/DaDogs/data/migrations'