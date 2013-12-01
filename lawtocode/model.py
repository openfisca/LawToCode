# -*- coding: utf-8 -*-


# Law-to-Code -- Extract formulas & parameters from laws
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 OpenFisca Team
# https://github.com/openfisca/law-to-code
#
# This file is part of Law-to-Code.
#
# Law-to-Code is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Law-to-Code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""The application's model objects"""


import collections
import datetime
import re

from biryani1 import strings

from . import conv, objects, texthelpers, urls, wsgihelpers


class Account(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.ActivityStreamWrapper):
    admin = False
    api_key = None
    collection_name = 'accounts'
    description = None
    email = None
    full_name = None
    slug = None

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        value.pop('api_key', None)
        return value, None

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                self.email,
                self.full_name,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'accounts', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'accounts', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_admin_class_full_url(ctx, self.slug or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_admin_class_url(ctx, self.slug or self._id, *path, **query)

    def get_title(self, ctx):
        return self.full_name or self.slug or self.email or self._id

    @classmethod
    def make_id_or_slug_or_words_to_instance(cls):
        def id_or_slug_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            id, error = conv.str_to_object_id(value, state = state)
            if error is None:
                self = cls.find_one(id, as_class = collections.OrderedDict)
            else:
                self = cls.find_one(dict(slug = value), as_class = collections.OrderedDict)
            if self is None:
                words = sorted(set(value.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No account with ID, slug or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much accounts with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_slug_or_words_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        value.pop('api_key', None)
        return value, None


class Formula(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.ActivityStreamWrapper):
    collection_name = u'formulas'
    description = None
    slug = None
    title = None

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                texthelpers.textify_html(self.description),
                self.title,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'formulas', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'formulas', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_admin_class_full_url(ctx, self.slug or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_admin_class_url(ctx, self.slug or self._id, *path, **query)

    @classmethod
    def get_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'formulas', *path, **query)

    @classmethod
    def get_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'formulas', *path, **query)

    def get_full_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_class_full_url(ctx, self.slug or self._id, *path, **query)

    def get_title(self, ctx):
        return self.title or self.slug or self._id

    def get_url(self, ctx, *path, **query):
        if self._id is None and self.slug is None:
            return None
        return self.get_class_url(ctx, self.slug or self._id, *path, **query)

    def get_user(self, ctx):
        if self._user is UnboundLocalError:
            self._user = Account.find_one(self.user_id) if self.user_id is not None else None
        return self._user

    @classmethod
    def make_id_or_slug_or_words_to_instance(cls):
        def id_or_slug_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            id, error = conv.str_to_object_id(value, state = state)
            if error is None:
                self = cls.find_one(id, as_class = collections.OrderedDict)
            else:
                self = cls.find_one(dict(slug = value), as_class = collections.OrderedDict)
            if self is None:
                words = sorted(set(value.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No formula with ID, slug or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much formulas with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_slug_or_words_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None


class Parameter(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.ActivityStreamWrapper):
    collection_name = u'parameters'
    comment = None
    description = None
    format = None
    openfisca_code = None
#    slug = None
    start_date = None
    stop_date = None
    title = None
    unit = None
    value = None

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                self.comment,
                texthelpers.textify_html(self.description),
                self.title,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'parameters', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'parameters', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_full_url(ctx, self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_url(ctx, self._id, *path, **query)

    @classmethod
    def get_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'parameters', *path, **query)

    @classmethod
    def get_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'parameters', *path, **query)

    def get_full_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_class_full_url(ctx, self._id, *path, **query)

    def get_title(self, ctx):
        return self.title or self._id

    def get_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_class_url(ctx, self._id, *path, **query)

    def get_user(self, ctx):
        if self._user is UnboundLocalError:
            self._user = Account.find_one(self.user_id) if self.user_id is not None else None
        return self._user

    @classmethod
    def id_or_words_to_instance(cls, value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = conv.default_state
        id, error = conv.str_to_object_id(value, state = state)
        if error is None:
            self = cls.find_one(id, as_class = collections.OrderedDict)
        else:
#            self = cls.find_one(dict(slug = value), as_class = collections.OrderedDict)
            self = None
        if self is None:
            words = sorted(set(value.split(u'-')))
            instances = list(cls.find(
                dict(
                    words = {'$all': [
                        re.compile(u'^{}'.format(re.escape(word)))
                        for word in words
                        ]},
                    ),
                as_class = collections.OrderedDict,
                ).limit(2))
            if not instances:
                return value, state._(u"No parameter with ID, slug or words: {0}").format(value)
            if len(instances) > 1:
                return value, state._(u"Too much parameters with words: {0}").format(u' '.join(words))
            self = instances[0]
        return self, None

    @classmethod
    def json_to_attributes(cls, value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = conv.default_state
        attributes, error = conv.pipe(
            conv.test_isinstance(dict),
            conv.struct(
                dict(
                    comment = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_text,
                        ),
                    description = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_text,
                        ),
                    draft_id = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.input_to_object_id,
                        ),
                    format = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_line,
                        conv.test_in([
                            u'bool',
                            u'float',
                            u'integer',
                            u'rate',
                            ]),
                        ),
                    openfisca_code = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_line,
                        ),
#                    slug = None
                    start_date = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.iso8601_input_to_date,
                        conv.date_to_iso8601_str,
                        ),
                    stop_date = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.iso8601_input_to_date,
                        conv.date_to_iso8601_str,
                        ),
                    title = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_line,
                        ),
                    unit = conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_line,
                        conv.test_in([
                            u'currency',
                            u'day',
                            u'hour',
                            u'month',
                            u'year',
                            ]),
                        ),
                    value = conv.noop,  # Conversion is done below.
                    ),
                ),
            )(value, state = state)
        if error is not None:
            return attributes, error

        value_converter = dict(
            bool = conv.pipe(
                conv.test_isinstance((bool, int)),
                conv.anything_to_bool,
                ),
            float = conv.pipe(
                conv.test_isinstance((float, int)),
                conv.anything_to_float,
                ),
            integer = conv.pipe(
                conv.test_isinstance((float, int)),
                conv.anything_to_int,
                ),
            rate = conv.pipe(
                conv.test_isinstance((float, int)),
                conv.anything_to_float,
                ),
            ).get(attributes['format'], conv.noop)
        return conv.pipe(
            conv.test_isinstance(dict),
            conv.struct(
                dict(
                    value = value_converter,
                    ),
                default = conv.noop,
                ),
            )(attributes, state = state)

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        if value.get('draft_id') is not None:
            value['draft_id'] = unicode(value['draft_id'])
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None


class Session(objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    _user = UnboundLocalError
    collection_name = 'sessions'
    expiration = None
    token = None  # the cookie token
    user_id = None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'sessions', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'sessions', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self.token is None:
            return None
        return self.get_admin_class_full_url(ctx, self.token, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self.token is None:
            return None
        return self.get_admin_class_url(ctx, self.token, *path, **query)

    def get_title(self, ctx):
        user = self.user
        if user is None:
            return ctx._(u'Session {0}').format(self.token)
        return ctx._(u'Session {0} of {1}').format(self.token, user.get_title(ctx))

    @classmethod
    def remove_expired(cls, ctx):
        for self in cls.find(
                dict(expiration = {'$lt': datetime.datetime.utcnow()}),
                as_class = collections.OrderedDict,
                ):
            self.delete(ctx)

    def to_bson(self):
        self_bson = self.__dict__.copy()
        self_bson.pop('_user', None)
        return self_bson

    @property
    def user(self):
        if self._user is UnboundLocalError:
            self._user = Account.find_one(self.user_id) if self.user_id is not None else None
        return self._user

    @classmethod
    def uuid_to_instance(cls, value, state = None):
        if value is None:
            return value, None
        if state is None:
            state = conv.default_state

        # First, delete expired sessions.
        cls.remove_expired(state)

        self = cls.find_one(dict(token = value), as_class = collections.OrderedDict)
        if self is None:
            return value, state._(u"No session with UUID {0}").format(value)
        return self, None


class Status(objects.Mapper, objects.Wrapper):
    collection_name = 'status'
    last_upgrade_name = None


def configure(ctx):
    pass


def get_user(ctx, check = False):
    user = ctx.user
    if user is UnboundLocalError:
        session = ctx.session
        ctx.user = user = session.user if session is not None else None
    if user is None and check:
        raise wsgihelpers.unauthorized(ctx)
    return user


def init(db):
    objects.Wrapper.db = db


def is_admin(ctx, check = False):
    user = get_user(ctx)
    if user is None or not user.admin:
        if user is not None and Account.find_one(dict(admin = True), []) is None:
            # Whem there is no admin, every logged user is an admin.
            return True
        if check:
            raise wsgihelpers.forbidden(ctx, message = ctx._(u"You must be an administrator to access this page."))
        return False
    return True


def setup():
    """Setup MongoDb database."""
    import imp
    import os
    from . import upgrades

    upgrades_dir = os.path.dirname(upgrades.__file__)
    upgrades_name = sorted(
        os.path.splitext(upgrade_filename)[0]
        for upgrade_filename in os.listdir(upgrades_dir)
        if upgrade_filename.endswith('.py') and upgrade_filename != '__init__.py'
        )
    status = Status.find_one(as_class = collections.OrderedDict)
    if status is None:
        status = Status()
        if upgrades_name:
            status.last_upgrade_name = upgrades_name[-1]
        status.save()
    else:
        for upgrade_name in upgrades_name:
            if status.last_upgrade_name is None or status.last_upgrade_name < upgrade_name:
                print 'Upgrading "{0}"'.format(upgrade_name)
                upgrade_file, upgrade_file_path, description = imp.find_module(upgrade_name, [upgrades_dir])
                try:
                    upgrade_module = imp.load_module(upgrade_name, upgrade_file, upgrade_file_path, description)
                finally:
                    if upgrade_file:
                        upgrade_file.close()
                upgrade_module.upgrade(status)

    Account.ensure_index('admin', sparse = True)
    Account.ensure_index('api_key', sparse = True, unique = True)
    Account.ensure_index('email', unique = True)
    Account.ensure_index('slug', unique = True)
    Account.ensure_index('updated')
    Account.ensure_index('words')

#    Formula.ensure_index('slug', unique = True)
    Formula.ensure_index('updated')
    Formula.ensure_index('words')

#    Parameter.ensure_index('slug', unique = True)
    Parameter.ensure_index('updated')
    Parameter.ensure_index('words')

    Session.ensure_index('expiration')
    Session.ensure_index('token', unique = True)
