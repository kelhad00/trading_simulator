import os
import sys
os.environ['APP_MODE'] = 'config'
os.environ['APP_PORT'] = '8050'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trade.app import run

if __name__ == '__main__':
    run()
