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

from collections import namedtuple

from sqlalchemy import sql

from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relation
from sqlalchemy.schema import UniqueConstraint

from spyne.model.complex import table
from spyne.model.complex import Array
from spyne.model.complex import TTableModel
from spyne.model.primitive import Date
from spyne.model.primitive import Integer32
from spyne.model.primitive import String
from spyne.model.primitive import Unicode

from spynepi.const import TABLE_PREFIX

DatabaseHandle = namedtuple("DatabaseHandle", ["db", "Session"])
TableModel = TTableModel()


class Person(TableModel):
    __tablename__ = "%s_person"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)
    person_name = String(256)
    person_email = String(256)


class Distribution(TableModel):
    __tablename__ = "%s_distribution"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)

    # TO-DO Add Content data
    file_name = String(256)
    file_path = String(256)
    dist_download_url = String(256)
    dist_comment = String(256)
    dist_file_type = String(256)
    dist_md5 = String(256)
    py_version = String(10)
    protocol_version = String(10)


class Release(TableModel):
    __tablename__ = "%s_release"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)
    release_cdate = Date
    rdf_about = String(256)
    release_version = String(10)
    meta_version = String(10)
    release_summary = String(256)
    release_platform = String(30)

    distributions = Array(Distribution).store_as(table(right="release_id"))


class Package(TableModel):
    __tablename__ = "%s_package"  % TABLE_PREFIX
    __table_args__ = (
        (UniqueConstraint("package_name"),),
        {"sqlite_autoincrement": True},
    )

    id = Integer32(primary_key=True)
    package_name = String(40)
    package_cdate = Date
    package_description = Unicode
    rdf_about = Unicode(256)
    package_license = Unicode(256)
    package_home_page = String(256)

    owners = Array(Person).store_as(table(right="owner_id"))
    releases = Array(Release).store_as(table(right="package_id"))


def patch_models():
    # this is here because the package_id column is not materialized until the
    # package table is created.
    Release.Attributes.sqla_table.append_constraint(
                            UniqueConstraint("package_id", "release_version"))

    package_m = Package.Attributes.sqla_mapper

    latest_releases = sql.select([sql.func.max(Release.id).label('release_id')],
                                     group_by=[Release.package_id]).alias()

    latest_release = Release.Attributes.sqla_table.select(
                Release.id == latest_releases.c.release_id).alias('latest_release')

    package_m.add_property('latest_release',
        relation(mapper(Release, latest_release, non_primary=True),
                uselist=False, viewonly=True)
    )

patch_models()

def init_database(connection_string):
    db = create_engine(connection_string)

    TableModel.Attributes.sqla_metadata.bind = db
    Session = sessionmaker(bind=db)

    # So that metadata gets updated with table names.
    import spynepi.entity.root
    import spynepi.entity.project

    TableModel.Attributes.sqla_metadata.create_all(checkfirst=True)
    return DatabaseHandle(db=db, Session=Session)
