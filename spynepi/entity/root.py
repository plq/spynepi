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

from spynepi.util.description import process_description
import logging
logger = logging.getLogger(__name__)

import os
import datetime

from sqlalchemy import sql

from spyne.decorator import rpc
from spyne.error import ArgumentError
from spyne.model.primitive import String
from spyne.model.primitive import Unicode
from spyne.service import ServiceBase

from spyne.model.binary import File
from spyne.protocol.http import HttpPattern

from spynepi.db import Package
from spynepi.db import Release
from spynepi.db import Distribution
from spynepi.db import Person


class RootService(ServiceBase):
    FILES_ROOT = None # To be set by main()

    @rpc(Unicode,#name
        Unicode, #license
        Unicode, #author
        Unicode, #home_page
        File,    #content
        Unicode, #comment
        Unicode, #download_url
        Unicode, #platform
        Unicode, #description
        Unicode, #metadata_version
        Unicode, #author_email
        Unicode, #md5_digest
        Unicode, #filetype
        Unicode, #pyversion
        Unicode, #summary
        Unicode, #version
        Unicode, #protocol_version
        String(encoding='ascii'), #action
        _patterns=[HttpPattern("/",verb="POST")],
        _in_variable_names={'action': ':action'})

    def register(ctx, name, license, author, home_page, content, comment,
            download_url, platform, description, metadata_version, author_email,
            md5_digest, filetype, pyversion, summary, version, protcol_version, # <= this is not a typo
            action):

        pth = os.path.join(name, version)

        def generate_package():
            return Package(
                    package_name=name,
                    package_cdate=datetime.date.today(),
                    package_description=process_description(description, 'utf8'),
                    rdf_about=os.path.join("/", name),
                    package_license=license,
                    package_home_page=home_page
                )

        def generate_person():
            return Person(person_name=author,
                    person_email=author_email,
                )

        def generate_release():
            return Release(
                    rdf_about=os.path.join("/", name, version),
                    release_version=version,
                    release_cdate=datetime.date.today(),
                    release_summary=summary ,
                    meta_version=metadata_version,
                    release_platform=platform,
                )

        def write_package_content(file_path):
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(file_path))

            f = open(file_path,"w")

            for d in content.data:
                f.write(d)
            f.close()

        package = ctx.udc.session.query(Package).filter_by(package_name=name).first()
        release = None
        if package is not None:
            release = ctx.udc.session.query(Release).join(Package).filter(
                sql.and_(
                    Package.package_name == name,
                    Release.release_version == version,
                )).first()

        if action == "submit":
            if package is None:
                package = generate_package()
                package.owners.append(generate_person())
                ctx.udc.session.add(package)

            if release is None:
                package.releases.append(generate_release())

            ctx.udc.session.commit()

        elif action == "file_upload":
            content.name = os.path.basename(content.name)
            path = os.path.join(RootService.FILES_ROOT, pth)
            file_path = os.path.join(path, content.name)

            if package is None:
                package = generate_package()
                package.owners.append(generate_person())
                ctx.udc.session.add(package)

            if release is None:
                release = generate_release()
                package.releases.append(release)

            release.distributions.append(Distribution(
                    file_name=content.name,
                    file_path=pth,
                    dist_download_url=download_url,
                    dist_comment=comment,
                    dist_file_type=filetype,
                    dist_md5=md5_digest,
                    py_version=pyversion,
                    protocol_version=protcol_version,
                ))

            ctx.udc.session.flush()

            if os.path.isfile(file_path):
                raise ArgumentError((name, version  ))

            write_package_content(file_path)

            ctx.udc.session.commit()
