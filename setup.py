#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name='jiradump',
      version='1.1.2',
      description='Dump JIRA issues from a filter, including custom fields, ' +
                  'as delimited text',
      author='Erskin Cherry',
      author_email='erskin@eldritch.org',
      url='https://github.com/frobnic8/jiradump',
      download_url='https://github.com/frobnic8/jiradump/tree/master/dist',
      packages=['jiradump'],
      entry_points={'console_scripts': ['jiradump = jiradump:main']},
      long_description=open('README.md').read(),
      install_requires=[
          'jira-python >= 0.16',
      ],
      provides=[
          'jiradump',
      ],
      )
