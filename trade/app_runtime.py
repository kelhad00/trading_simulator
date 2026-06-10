import os
os.environ['APP_MODE'] = 'runtime'
os.environ['APP_PORT'] = '8051'

from app import run  # noqa: E402

if __name__ == '__main__':
    run()
