from setuptools import setup, find_packages
import os

version = open(os.path.join("collective",
                            "sendaspdf",
                            "version.txt")).read().strip()

setup(name='collective.sendaspdf',
      version=version,
      description="An open source product for Plone to download or email a " +
                  "page seen by the user as a PDF file.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("collective",
                                         "sendaspdf",
                                         "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Zest Software',
      author_email='v.pretre@zestsoftware.nl',
      url='http://github.com/vincent-psarga/collective.sendaspdf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'jquery.pyproxy',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
