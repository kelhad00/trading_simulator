import os
os.environ['APP_MODE'] = 'config'
os.environ['APP_PORT'] = '8050'

from app import run  # noqa: E402

if __name__ == '__main__':
    run()
