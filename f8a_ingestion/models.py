# Copyright © 2018 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Geetika Batra <gbatra@redhat.com>
#

"""Utility class."""


from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint,
                        create_engine, func, Boolean)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool

from defaults import configuration
from enums import EcosystemBackend


def create_db_scoped_session(connection_string=None):
    """Create scoped session."""
    # we use NullPool, so that SQLAlchemy doesn't pool local connections
    #  and only really uses connections while writing results
    return scoped_session(
        sessionmaker(bind=create_engine(
            connection_string or configuration.POSTGRES_CONNECTION,
            poolclass=NullPool)))


class BayesianModelMixin(object):
    """Subclasses of this class will gain some `by_*` class methods.

    Note, that these should only be used to obtain objects by unique attribute
    (or combination of attributes that make the object unique), since under the
    hood they use SQLAlchemy's `.one()`.

    Also note, that these class methods will raise sqlalchemy.rom.exc.NoResultFound if the object
    is not found.
    """

    def to_dict(self):
        """Convert table to dictionary."""
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)

        return d

    @classmethod
    def _by_attrs(cls, session, **attrs):
        """Get one row with attrs."""
        try:
            return session.query(cls).filter_by(**attrs).one()
        except NoResultFound:
            raise
        except SQLAlchemyError:
            session.rollback()
            raise

    @classmethod
    def by_id(cls, session, id):
        """Get a row with id."""
        try:
            return cls._by_attrs(session, id=id)
        except NoResultFound:
            # What to do here ?
            raise

    @classmethod
    def get_or_create(cls, session, **attrs):
        """Try to get by attrs or create new record if no result found."""
        try:
            return cls._by_attrs(session, **attrs)
        except NoResultFound:
            try:
                o = cls(**attrs)
                try:
                    session.add(o)
                    session.commit()
                except SQLAlchemyError:
                    session.rollback()
                    raise
                return o
            except IntegrityError:  # object was created in the meanwhile by someone else
                return cls._by_attrs(**attrs)


Base = declarative_base(cls=BayesianModelMixin)


class Ecosystem(Base):
    """Table for Ecosystem."""

    __tablename__ = 'ecosystems'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    url = Column(String(255))
    _backend = Column(
        Enum(*[b.name for b in EcosystemBackend], name='ecosystem_backend_enum'))

    packages = relationship('Package', back_populates='ecosystem')

    @property
    def backend(self):
        """Get backend property."""
        return EcosystemBackend[self._backend]

    @backend.setter
    def backend(self, backend):
        """Set backend property."""
        self._backend = EcosystemBackend(backend).name

    def is_backed_by(self, backend):
        """Is this ecosystem backed by specified backend?."""
        return self.backend == backend

    @classmethod
    def by_name(cls, session, name):
        """Get a row with specified name."""
        try:
            return cls._by_attrs(session, name=name)
        except NoResultFound:
            # What to do here ?
            raise


class Package(Base):
    """Table for Package."""

    __tablename__ = 'packages'
    # ecosystem_id together with name must be unique
    __table_args__ = (UniqueConstraint(
        'ecosystem_id', 'name', name='ep_unique'),)

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey(Ecosystem.id))
    name = Column(String(255), index=True)

    ecosystem = relationship(
        Ecosystem, back_populates='packages', lazy='joined')
    versions = relationship('Version', back_populates='package')

    @classmethod
    def by_name(cls, session, name):
        """Get a row with specified name."""
        # TODO: this is dangerous at is does not consider Ecosystem
        try:
            return cls._by_attrs(session, name=name)
        except NoResultFound:
            # What to do here ?
            raise


class Version(Base):
    """Table for Version."""

    __tablename__ = 'versions'
    # package_id together with version identifier must be unique
    __table_args__ = (UniqueConstraint(
        'package_id', 'identifier', name='pv_unique'),)

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey(Package.id))
    identifier = Column(String(255), index=True)

    package = relationship(Package, back_populates='versions', lazy='joined')

    @classmethod
    def by_identifier(cls, session, identifier):
        """Get a row with specified identifier."""
        try:
            return cls._by_attrs(session, identifier=identifier)
        except NoResultFound:
            # What to do here ?
            raise
