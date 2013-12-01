#! /usr/bin/env python
# -*- coding: utf-8 -*-


# law-to-code -- Extract formulas from laws
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 OpenFisca Team
# https://github.com/openfisca/law-to-code
#
# This file is part of law-to-code.
#
# law-to-code is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# law-to-code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Extract data from OpenFisca parameters files (XML) and upload it to law-to-code."""


import argparse
import json
import logging
import os
import sys
import xml.etree.ElementTree

from biryani1 import baseconv, custom_conv, datetimeconv, states

app_name = os.path.splitext(os.path.basename(__file__))[0]
conv = custom_conv(baseconv, datetimeconv, states)
log = logging.getLogger(app_name)
parameters = []


def generate_openfisca_code(*ancestors):
    return u'.'.join(
        code
        for code in (
            ancestor.get('code')
            for ancestor in reversed(ancestors[:-1])
            )
        if code is not None
        ) or None


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-o', '--openfisca-dir', help = "directory of the openfisca project", required = True)
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    countries_dir = os.path.join(args.openfisca_dir, 'src', 'countries')
    for country_dir_name, country_name in (
            (u'france', u"France"),
            (u'tunisia', u"Tunisia"),
            ):
        country_dir = os.path.join(countries_dir, country_dir_name)
        parameters_dir = os.path.join(country_dir, 'param')
        parameters_file_path = os.path.join(parameters_dir, 'param.xml')
        log.info(u'Parsing parameters from {}'.format(parameters_file_path))
        parameters_tree = xml.etree.ElementTree.parse(parameters_file_path)
        root_element = parameters_tree.getroot()
        parse_element(root_element)

    print unicode(json.dumps(parameters, ensure_ascii = False, indent = 2)).encode('utf-8')

    return 0


def parse_element(element, *ancestors):
    if element.tag == 'BAREME':
        scale_infos = conv.check(conv.struct(
            dict(
                code = conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                description = conv.cleanup_line,
                option = conv.test_in([
                    'contrib',
                    'noncontrib',
                    ]),
                taille = conv.test_in([
                    'plusde20',
                    ]),
                type = conv.test_in(['monetary']),
                ),
            ))(element.attrib, state = conv.default_state)
        scale_infos['comment'] = conv.check(conv.pipe(
            conv.cleanup_line,
            conv.function(lambda value: value.strip(u'#')),
            conv.cleanup_line,
            ))(element.text, state = conv.default_state)
        assert len(element) > 0, list(element)
        for scale_child in element:
            if scale_child.tag == 'TRANCHE':
                scale_child_infos = conv.check(conv.struct(
                    dict(
                        code = conv.cleanup_line,
                        ),
                    ))(scale_child.attrib, state = conv.default_state)
                scale_child_infos['comment'] = conv.check(conv.pipe(
                    conv.cleanup_line,
                    conv.function(lambda value: value.strip(u'#')),
                    conv.cleanup_line,
                    ))(scale_child.text, state = conv.default_state)
                assert len(scale_child) > 0, list(scale_child)
                for slice_child in scale_child:
                    if slice_child.tag in ('ASSIETTE', 'SEUIL', 'TAUX'):
                        slice_child_infos = conv.check(conv.struct(
                            dict(
                                ),
                            ))(slice_child.attrib, state = conv.default_state)
                        slice_child_infos['comment'] = conv.check(conv.pipe(
                            conv.cleanup_line,
                            conv.function(lambda value: value.strip(u'#')),
                            conv.cleanup_line,
                            ))(slice_child.text, state = conv.default_state)
                        assert len(slice_child) > 0, list(slice_child)
                        values = parse_value_elements(slice_child, slice_child_infos, scale_child_infos, scale_infos,
                            *ancestors)
                    else:
                        raise KeyError('Unexpected element {} in {} in {}'.format(
                            xml.etree.ElementTree.tostring(slice_child, encoding = 'utf-8'),
                            xml.etree.ElementTree.tostring(scale_child, encoding = 'utf-8'),
                            xml.etree.ElementTree.tostring(element, encoding = 'utf-8'),
                            ))
            else:
                raise KeyError('Unexpected element {} in {}'.format(
                    xml.etree.ElementTree.tostring(scale_child, encoding = 'utf-8'),
                    xml.etree.ElementTree.tostring(element, encoding = 'utf-8'),
                    ))
    elif element.tag == 'CODE':
        code = conv.check(conv.struct(
            dict(
                code = conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                description = conv.cleanup_line,
                format = conv.test_in([
                    'bool',
                    'float',
                    'integer',
                    'percent',
                    ]),
                taille = conv.test_in([
                    'moinsde20',
                    'plusde20',
                    ]),
                type = conv.test_in([
                    'age',
                    'days',
                    'hours',
                    'monetary',
                    'months',
                    ]),
                ),
            ))(element.attrib, state = conv.default_state)
        code['comment'] = conv.check(conv.pipe(
            conv.cleanup_line,
            conv.function(lambda value: value.strip(u'#')),
            conv.cleanup_line,
            ))(element.text, state = conv.default_state)
        assert len(element) > 0, list(element)
        values = parse_value_elements(element, code, *ancestors)
        for value in values:
            parameter = value.copy()
            if code['description'] is not None:
                parameter[u'description'] = code['description']
                parameter[u'openfisca_code'] = generate_openfisca_code(code, *ancestors)
            parameters.append(parameter)
    elif element.tag == 'NODE':
        node = conv.check(conv.struct(
            dict(
                code = conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                description = conv.cleanup_line,
                ),
            ))(element.attrib, state = conv.default_state)
        node['comment'] = conv.check(conv.pipe(
            conv.cleanup_line,
            conv.function(lambda value: value.strip(u'#')),
            conv.cleanup_line,
            ))(element.text, state = conv.default_state)
        for child in element:
            parse_element(child, node, *ancestors)
    else:
        raise KeyError('Unexpected element {}'.format(
            xml.etree.ElementTree.tostring(element, encoding = 'utf-8'),
            ))


def parse_value_elements(element, container, *ancestors):
    values = []
    for child in element:
        if child.tag == 'VALUE':
            value_converter = dict(
                bool = conv.pipe(
                    conv.cleanup_line,
                    conv.test_in([u'0', u'1']),
                    conv.input_to_bool,
                    ),
                float = conv.pipe(
                    conv.cleanup_line,
                    conv.input_to_float,
                    ),
                integer = conv.pipe(
                    conv.cleanup_line,
                    conv.input_to_int,
                    ),
                percent = conv.pipe(
                    conv.cleanup_line,
                    conv.input_to_float,
                    ),
                )[container.get('format') or 'float']
            value_infos = conv.check(conv.struct(
                dict(
                    code = conv.cleanup_line,
                    deb = conv.pipe(
                        conv.iso8601_input_to_date,
                        conv.date_to_iso8601_str,
                        conv.not_none,
                        ),
                    fin = conv.pipe(
                        conv.iso8601_input_to_date,
                        conv.date_to_iso8601_str,
                        conv.not_none,
                        ),
                    format = conv.pipe(
                        conv.test_equals(element.get('format')),
                        conv.translate(dict(
                            percent = u'rate',
                            )),
                        conv.default(u'float'),
                        ),
                    type = conv.pipe(
                        conv.test_equals(element.get('type')),
                        conv.translate(dict(
                            age = u'year',
                            days = u'day',
                            hours = u'hour',
                            monetary = u'currency',
                            months = u'month',
                            )),
                        ),
                    valeur = value_converter,
                    ),
                ))(child.attrib, state = conv.default_state)
            value_infos['comment'] = conv.check(conv.pipe(
                conv.cleanup_line,
                conv.function(lambda value: value.strip(u'#')),
                conv.cleanup_line,
                ))(child.tail, state = conv.default_state)
            assert len(child) == 0, list(child)
            values.append(dict(
                (
                    dict(
                        code = u'openfisca_code',
                        comment = u'comment',
                        deb = u'start_date',
                        fin = u'stop_date',
                        format = u'format',
                        type = u'unit',
                        valeur = u'value',
                        )[key],
                    value,
                    )
                for key, value in value_infos.iteritems()
                if value is not None
                ))
        else:
            raise KeyError('Unexpected element {} in {}'.format(
                xml.etree.ElementTree.tostring(child, encoding = 'utf-8'),
                xml.etree.ElementTree.tostring(element, encoding = 'utf-8'),
                ))
    return values


if __name__ == "__main__":
    sys.exit(main())
