## -*- coding: utf-8 -*-


## law-to-code -- Extract formulas from laws
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 OpenFisca Team
## https://github.com/openfisca/law-to-code
##
## This file is part of law-to-code.
##
## law-to-code is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## law-to-code is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
from lawtocode import model, urls
%>


<%inherit file="/site.mako"/>
<%namespace name="view" file="admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Parameter.get_admin_class_url(ctx)}">${_(u"Parameters")}</a></li>
            <li><a href="${parameter.get_admin_url(ctx)}">${parameter.get_title(ctx)}</a></li>
            <li class="active">${_(u'Delete')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${_(u'Deletion of {}').format(parameter.get_title(ctx))}</h2>
        <p class="confirm">${_(u"Are you sure that you want to delete this parameter?")}</p>
        <form method="post" action="${parameter.get_admin_url(ctx, 'delete')}">
            <%view:view_fields/>
            <button class="btn btn-danger" name="submit" type="submit"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_(u'Delete')} - ${parameter.get_title(ctx)} - ${parent.title_content()}
</%def>

