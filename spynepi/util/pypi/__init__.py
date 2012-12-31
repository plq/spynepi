# encoding: utf8
#
# (C) Copyright Arskom Ltd. <info@arskom.com.tr>
#               Uğurcan Ergün <ugurcanergn@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#


import logging
logger = logging.getLogger(__name__)

import os
import sys
import shutil
import tempfile
import subprocess

from glob import glob

from pkg_resources import Requirement

from setuptools.archive_util import unpack_archive
from setuptools.package_index import PackageIndex

from spyne.error import ValidationError
from spyne.error import ArgumentError
from spynepi.const import REPO_NAME


def _generate_pypirc(own_url):
    import ConfigParser

    rc = os.path.join(os.environ['HOME'], '.pypirc')
    config = ConfigParser.ConfigParser()

    if os.path.exists(rc):
        config.read(rc)

    try:
        config.add_section(REPO_NAME)

        config.set(REPO_NAME, 'repository', own_url)
        config.set(REPO_NAME, 'username', 'x')
        config.set(REPO_NAME, 'password', 'y')

    except ConfigParser.DuplicateSectionError:
        pass

    try:
        config.add_section('distutils')
    except ConfigParser.DuplicateSectionError:
        pass

    try:
        index_servers = config.get('distutils', 'index-servers')
        index_servers = index_servers.split('\n')
        if 'spynepi' not in index_servers:
            index_servers.append(REPO_NAME)

    except ConfigParser.NoOptionError:
        index_servers = [REPO_NAME]

    config.set('distutils', 'index-servers', '\n'.join(index_servers))

    config.write(open(rc,'w'))


def cache_package(spec, own_url):
    try:
        spec = Requirement.parse(spec)

    except ValueError:
        raise ArgumentError("Not a URL, existing file, or requirement spec: %r"
                                                                      % (spec,))

    try:
        # download and unpack source package
        path = tempfile.mkdtemp('.spynepi')
        logger.info("Downloading %r" % spec)
        dist = PackageIndex().fetch_distribution(spec, path, force_scan=True, source=True)
        archive_path = dist.location
        logger.info("Unpacking %r" % archive_path)
        unpack_archive(dist.location, path)

        # generate pypirc if possible
        if os.environ.has_key('HOME'):
            _generate_pypirc(own_url)
        else: # FIXME: ??? No idea. Hopefully setuptools knows better.
            pass # raise NotImplementedError("$HOME not defined, .pypirc not found.")

        # find setup.py in package. plagiarized from setuptools.
        setups = glob(os.path.join(path, '*', 'setup.py'))
        if not setups:
            raise ValidationError(
                "Couldn't find a setup script in %r editable distribution: %r" %
                                                    (spec, os.path.join(path,'*'))
            )

        if len(setups)>1:
            raise ValidationError(
                "Multiple setup scripts in found in %r editable distribution: %r" %
                                                    (spec, setups)
            )

        # self-register the package.
        lib_dir = os.path.dirname(setups[0])
        command = ["python", "setup.py", "register", "-r", REPO_NAME]
        logger.info('calling %r', command)
        subprocess.call(command, cwd=lib_dir, stdout=sys.stdout)

        # self-upload the package
        command = ["python", "-m", "spynepi.util.pypi.upload", archive_path]
        logger.info('calling %r', command)
        subprocess.call(command, cwd=lib_dir, stdin=sys.stdin, stdout=sys.stdout)

    finally:
        shutil.rmtree(path)
