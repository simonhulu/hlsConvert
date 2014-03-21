'''
Created on 2013-7-19

@author: zhangshijie
'''
from setuptools import setup, find_packages
setup(
      name="hlsConvert",
      version="0.10",
      description="My hlsConvert module",
      author="szhang",
      url="http://www.xueersi.com",
      license="LGPL",
      packages= find_packages(),
      scripts=["hlsConvert.py","Convert.py"],
      )
