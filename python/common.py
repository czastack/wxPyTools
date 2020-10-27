import os
import sys


EXEC_DIR = os.path.dirname(sys.executable)
DATA_DIR = os.path.join(EXEC_DIR, 'data')
CONF_DIR = os.path.join(DATA_DIR, 'config')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

if not os.path.exists(CONF_DIR):
    os.mkdir(CONF_DIR)
