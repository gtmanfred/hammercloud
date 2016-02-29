#!/usr/bin/env python
from __future__ import print_function
import setuptools
import os

import distutils.dist
from distutils.command.sdist import sdist

import logging
log = logging.getLogger(__name__)

del os.link


class Sdist(sdist):
    def make_release_tree(self, base_dir, files):
        sdist.make_release_tree(self, base_dir, files)
        import pbr.packaging
        version = pbr.packaging.get_version('git')
        files = [
            'pkgs/PKGBUILD', 'pkgs/hammercloud.spec', 'debian/changelog'
        ]
        for pkgfile in files:
            with open(os.path.join(base_dir, pkgfile), 'r') as tmpfile:
                filedata = tmpfile.read()
            filedata = filedata.replace('XXXX', version)
            with open(os.path.join(base_dir, pkgfile), 'w') as tmpfile:
                print(filedata, file=tmpfile)


class HammercloudDist(distutils.dist.Distribution):
    def __init__(self, attrs=None):
        distutils.dist.Distribution.__init__(self, attrs)
        self.cmdclass.update({'sdist': Sdist})


options = {
    'include_package_data': True,
    'zip_safe': False,
    'setup_requires': ['pbr>=0.8.2'],
    'pbr': True,
}

setuptools.setup(distclass=HammercloudDist, **options)
