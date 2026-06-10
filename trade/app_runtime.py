import os
os.environ['APP_MODE'] = 'runtime'

from app import run  # noqa: E402

if __name__ == '__main__':
    run()
