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
from lawtocode import model, texthelpers, urls
%>


<%inherit file="/object-admin-index.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li class="active">${_(u'Parameters')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No parameter found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Parameter {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Parameters {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single parameter")}</h2>
        % else:
        <h2>${_(u"{} parameters").format(pager.item_count)}</h2>
        % endif
        <%self:pagination object_class="${model.Parameter}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
            % if data['sort'] == 'slug':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
            % else:
                    <th><a href="${model.Parameter.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'slug'))}">${_(u"Title")}</a></th>
            % endif
                    <th>${_(u"Start Date")}</th>
                    <th>${_(u"Stop Date")}</th>
                    <th>${_(u"Value")}</th>
            % if data['sort'] == 'updated':
                    <th>${_(u"Updated")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
            % else:
                    <th><a href="${model.Parameter.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'updated'))}">${_(u"Updated")}</a></th>
            % endif
                </tr>
            </thead>
            <tbody>
        % for parameter in parameters:
                <tr>
                    <td>
                        <h4><a href="${parameter.get_admin_url(ctx)}">${parameter.title}</a></h4>
<%
            description_text = texthelpers.textify_html(parameter.description)
%>\
            % if description_text:
                        ${texthelpers.truncate(description_text, length = 180, whole_word = True)}
            % endif
                    </td>
                    <td>${parameter.start_date or u''}</td>
                    <td>${parameter.stop_date or u''}</td>
                    <td>${parameter.value if parameter.value is not None else u''}</td>
                    <td>${parameter.updated.split('T')[0]}</td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Parameter}" pager="${pager}"/>
    % endif
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${model.Parameter.get_admin_class_url(ctx, 'new')}">${_(u'New')}</a>
        </div>
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Parameter.get_admin_class_url(ctx)}" method="get" role="form">
    % if data['advanced_search']:
            <input name="advanced_search" type="hidden" value="1">
    % endif
            <input name="sort" type="hidden" value="${inputs['sort'] or ''}">
<%
    error = errors.get('term') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="term">${_("Term")}</label>
                <input class="form-control" id="term" name="term" type="text" value="${inputs['term'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${
                _('Search')}</button>
            <a href="${urls.get_url(ctx, 'api', '1', 'parameters', **urls.relative_query(inputs,
                    advanced_search = None, format = 'atom', page = None, sort = None))}">${_('News Feed')}</a>
    % if data['advanced_search']:
            <a class="pull-right" href="${model.Parameter.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = None))}">${_('Simplified Search')}</a>
    % else:
            <a class="pull-right" href="${model.Parameter.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = 1))}">${_('Advanced Search')}</a>
    % endif
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Parameters')} - ${parent.title_content()}
</%def>

