## -*- coding: utf-8 -*-


## Law-to-Code -- Extract formulas & parameters from laws
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 OpenFisca Team
## https://github.com/openfisca/law-to-code
##
## This file is part of Law-to-Code.
##
## Law-to-Code is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## Law-to-Code is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
from lawtocode import conf, model, texthelpers, urls
%>


<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${conf['realm']}</title>
    <id>${urls.get_full_url(ctx, 'api', '1', 'formulas', **urls.relative_query(inputs))}</id>
    <link href="${model.Formula.get_admin_class_full_url(ctx) if data['target'] is None \
            else model.Formula.get_class_back_url(ctx) if data['target'] == 'back' \
            else model.Formula.get_class_front_url(ctx)}"/>
    <link href="${urls.get_full_url(ctx, 'api', '1', 'formulas', **urls.relative_query(inputs))}" rel="self"/>
##    <author>
##        <name>${_('OpenFisca Team')}</name>
##        <email>${conf['openfisca.email']}</email>
##        <uri>${conf['openfisca.url']}</uri>
##    </author>
##    % for tag in (tags or []):
##          <category term="${tag}"/>
##    % endfor
    <generator uri="https://github.com/openfisca/law-to-code">Law-to-Code</generator>
    <rights>
        This feed is licensed under the Open Licence ${'<http://www.data.gouv.fr/Licence-Ouverte-Open-Licence>'}.
    </rights>
<%
    formulas = list(cursor)
    updated = max(
        formula.updated
        for formula in formulas
        )
%>\
    <updated>${updated}</updated>
    % for formula in formulas:
    <entry>
        <title>${formula.title}</title>
        <id>${formula.get_admin_full_url(ctx)}</id>
        <link href="${formula.get_admin_full_url(ctx) if data['target'] is None \
                else formula.get_back_url(ctx) if data['target'] == 'back' \
                else formula.get_front_url(ctx)}"/>
        <published>${formula.published}</published>
        <updated>${formula.updated}</updated>
        % if formula.description:
        <summary type="html">
            ${texthelpers.clean_html(formula.description)}
        </summary>
        % endif
    </entry>
    % endfor
</feed>
