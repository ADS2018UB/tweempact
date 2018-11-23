# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 17:51:13 2018

@author: PC
"""


from flask_script import Manager
from app.app import app

manager = Manager(app)
app.config['DEBUG'] = True # Ensure debugger will load.

if __name__ == '__main__':
  manager.run()
  
  