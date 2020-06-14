"""
    csw     flask车卫士

    2014.05.13 xiongchen
"""



import os
from app import create_app

print("main.py")

import gevent.monkey
gevent.monkey.patch_all()

cfg = os.getenv('FLASK_CONFIG') or 'default'
print(cfg)

main = create_app(cfg)
main.app_context().push()

if __name__ == '__main__':
    main.run()
