/*
 * Law-to-Code -- Extract formulas & parameters from laws
 * By: Emmanuel Raviart <emmanuel@raviart.com>
 *
 * Copyright (C) 2013 OpenFisca Team
 * https://github.com/openfisca/law-to-code
 *
 * This file is part of Law-to-Code.
 *
 * Law-to-Code is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * Law-to-Code is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


$(function() {
    $('.typeahead#user').typeahead({
        name: 'user',
        remote: '/api/1/accounts/typeahead?q=%QUERY'
    });
    $('.typeahead#tag').typeahead({
        name: 'tag',
        remote: '/api/1/tags/typeahead?q=%QUERY'
    });
});

