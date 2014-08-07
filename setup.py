#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name='jiradump',
      version='1.1.0',
      description='Dump JIRA issues from a filter, including custom fields, ' +
                  'as delimited text',
      author='Erskin Cherry',
      author_email='erskin.cherry@opower.com',
      url='https://github.va.opower.it/erskin-cherry/jiradump',
      download_url='https://github.va.opower.it/erskin-cherry/jiradump/tree/master/dist',
      packages=['jiradump'],
      scripts=['bin/jiradump'],
      long_description=open('README.md').read(),
      install_requires=[
          'jira-python >= 0.16',
      ],
      provides=[
          'jiradump',
      ],
      )
