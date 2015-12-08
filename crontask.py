#!/kunden/homepages/32/d474424001/htdocs/lab/bin/python
import sys, os
#import cgitb; cgitb.enable()

basepath = '/kunden/homepages/32/d474424001/htdocs/'

sys.path.insert(0, basepath + '.local/lib')
sys.path.insert(0, basepath + 'lab/tweeterbot')

os.environ['DJANGO_SETTINGS_MODULE'] = 'tweeterbot.settings'

venv = '/kunden/homepages/32/d474424001/htdocs/lab/bin/activate_this.py'
execfile(venv, dict(__file__=venv))

import django
from django.core import management

django.setup()
management.call_command('post_tweet')
