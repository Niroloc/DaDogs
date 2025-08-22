import os

LOGS = '/.logs'
CONFIG_FILE = '/config.json'
DB_FILE = '/data/db.db'
MIGRATION_FOLDER = '/data/migrations'

if os.getenv("ENVIRONMENT", 'dev') == 'dev':
    LOGS = '~/PycharmProjects/DaDogs/logs/common.logs'
    CONFIG_FILE = '~/PycharmProjects/DaDogs/config/config.json'
    DB_FILE = '~/PycharmProjects/DaDogs/data/db.db'
    MIGRATION_FOLDER = '~/PycharmProjects/DaDogs/data/migrations'