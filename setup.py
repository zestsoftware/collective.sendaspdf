from setuptools import setup, find_packages

setup(name='collective.sendaspdf',
      version='2.10',
      description="An open source product for Plone to download or email a " +
                  "page seen by the user as a PDF file.",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.4",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      keywords='html pdf converter',
      author='Zest Software',
      author_email='v.pretre@zestsoftware.nl',
      url='http://github.com/zestsoftware/collective.sendaspdf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'jquery.pyproxy>=0.3',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
