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


"""Root controllers"""


import logging

from .. import contexts, templates, urls, wsgihelpers
from . import accounts, formulas, parameters, sessions


log = logging.getLogger(__name__)
router = None


@wsgihelpers.wsgify
def index(req):
    ctx = contexts.Ctx(req)
    return templates.render(ctx, '/index.mako')


def make_router():
    """Return a WSGI application that searches requests to controllers """
    global router
    router = urls.make_router(
        ('GET', '^/?$', index),

        (None, '^/admin/accounts(?=/|$)', accounts.route_admin_class),
        (None, '^/admin/formulas(?=/|$)', formulas.route_admin_class),
        (None, '^/admin/sessions(?=/|$)', sessions.route_admin_class),
        (None, '^/admin/parameters(?=/|$)', parameters.route_admin_class),
        (None, '^/api/1/accounts(?=/|$)', accounts.route_api1_class),
        (None, '^/api/1/formulas(?=/|$)', formulas.route_api1_class),
        (None, '^/api/1/parameters(?=/|$)', parameters.route_api1_class),
        ('POST', '^/login/?$', accounts.login),
        ('POST', '^/logout/?$', accounts.logout),
        )
    return router
