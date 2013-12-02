#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Law-to-Code -- Extract formulas & parameters from laws
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 OpenFisca Team
# https://github.com/openfisca/LawToCode
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


"""Extract parameters from IPP's "Barèmes des prélèvements sociaux" and upload them to Law-to-Code.

IPP = Institut des politiques publiques
http://www.ipp.eu/fr/outils/baremes-prelevements-sociaux/
http://www.ipp.eu/fr/outils/taxipp-simulation/
"""


import argparse
import collections
import ConfigParser
import itertools
import json
import logging
import os
import sys
import urlparse

from biryani1 import baseconv, custom_conv, datetimeconv, states
import requests
import xlrd

app_name = os.path.splitext(os.path.basename(__file__))[0]
conv = custom_conv(baseconv, datetimeconv, states)
log = logging.getLogger(app_name)
N_ = lambda message: message
parameters = []


currency_converter = conv.first_match(
    conv.pipe(
        conv.test_isinstance(basestring),
        conv.cleanup_line,
        conv.test_none(),
        ),
    conv.pipe(
        conv.test_isinstance(tuple),
        conv.test(lambda couple: len(couple) == 2, error = N_(u"Invalid couple length")),
        conv.struct(
            (
                conv.pipe(
                    conv.test_isinstance((float, int)),
                    conv.not_none,
                    ),
                conv.pipe(
                    conv.test_isinstance(basestring),
                    conv.test_in([
                        u'EUR',
                        u'FRF',
                        ]),
                    ),
                ),
            ),
        ),
    )


pss_converters = collections.OrderedDict((
    (u"Date d'effet", conv.pipe(
        conv.test_isinstance(basestring),
        conv.iso8601_input_to_date,
        conv.date_to_iso8601_str,
        conv.not_none,
        )),
    (u'Plafond de la Sécurité sociale (mensuel)', currency_converter),
    (u'Plafond de la Sécurité sociale (annuel)', currency_converter),
    (u'Référence législative', conv.pipe(
        conv.test_isinstance(basestring),
        conv.cleanup_line,
        )),
    (u'Parution au JO', conv.pipe(
        conv.test_isinstance(basestring),
        conv.iso8601_input_to_date,
        conv.date_to_iso8601_str,
        )),
    (u'Notes', conv.pipe(
        conv.test_isinstance(basestring),
        conv.cleanup_line,
        )),
    (None, conv.pipe(
        conv.test_isinstance(basestring),
        conv.cleanup_line,
        conv.test_none(),
        )),
    ))


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = 'path of configuration file')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    config_parser = ConfigParser.SafeConfigParser(dict(
        here = os.path.dirname(os.path.abspath(os.path.normpath(args.config))),
        ))
    config_parser.read(args.config)
    conf = conv.check(conv.pipe(
        conv.test_isinstance(dict),
        conv.struct(
            {
                'law_to_code.api_key': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                'law_to_code.site_url': conv.pipe(
                    conv.make_input_to_url(error_if_fragment = True, error_if_path = True, error_if_query = True,
                        full = True),
                    conv.not_none,
                    ),
                'user_agent': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                },
            default = 'drop',
            ),
        conv.not_none,
        ))(dict(config_parser.items('Law-to-Code-TAXIPP-Harvester')), conv.default_state)

    response = requests.get('http://www.ipp.eu/wp-content/uploads/2012/01/IPP-prelevements-sociaux-avril2012.xls')
    book = xlrd.open_workbook(file_contents = response.content, formatting_info = True)
    sheet_names = book.sheet_names()
    assert sheet_names == [
        u'Sommaire',
        u'PSS',
        u'SMIG',
        u'SMIC',
        u'GMR',
        u'CSG-1',
        u'CSG-2',
        u'CRDS',
        u'SS',
        u'MMID',
        u'MMID-AM',
        u'CNAV',
        u'VEUVAGE',
        u'CSA',
        u'FAMILLE',
        u'CSS_RED',
        u'CHOMAGE',
        u'ASF',
        u'AGFF',
        u'AGS',
        u'ARRCO',
        u'AGIRC',
        u'APEC',
        u'CET',
        u'DECES_CADRES',
        u'ASSIETTE PU',
        u'MMID-Etat',
        u'MMID-CL',
        u'RP',
        u'CI',
        u'RAFP',
        u'CNRACL',
        u'IRCANTEC',
        u'FDS',
        u'TAXSAL',
        u'CONSTRUCTION',
        u'FNAL',
        u'ACCIDENTS',
        u'FORMATION',
        u'APPRENTISSAGE',
        u'VT',
        u'PREVOYANCE',
        u'AUBRY I',
        u'ALLEG_GEN',
        u'AUBRYII',
        u'SFT',
        u'INDICE_FP',
        ], str((sheet_names,))

    sheet = book.sheet_by_name(u'PSS')
    sheet_data = [
        [
            transform_xls_cell_to_json(book, cell_type, cell_value, sheet.cell_xf_index(row_index, column_index))
            for column_index, (cell_type, cell_value) in enumerate(itertools.izip(sheet.row_types(row_index),
                sheet.row_values(row_index)))
            ]
        for row_index in range(sheet.nrows)
        ]
    taxipp_names = sheet_data[0]
    labels = sheet_data[1]
    assert labels == pss_converters.keys(), str((labels,))
    taxipp_name_by_label = dict(zip(labels, taxipp_names))
    description_lines = []
    entries = []
    state = None
    for row_index, row in enumerate(itertools.islice(sheet_data, 2, None)):
        if all(cell in (None, u'') for cell in row):
            state = 'description'
        if state is None:
            entry = conv.check(conv.struct(pss_converters))(dict(zip(labels, row)), state = conv.default_state)
            entries.append(entry)
        else:
            description_line = u' '.join(
                cell.strip()
                for cell in row
                if cell is not None
                )
            description_lines.append(description_line)
    description = u'\n'.join(description_lines) or None

    parameters = []
    for entry in entries:
        value_label = u'Plafond de la Sécurité sociale (mensuel)'
        parameters.append(dict(
            comment = entry[u"Notes"],
            description = description,
            format = u'float',
            legislative_reference = entry[u'Référence législative'],
            official_publication_date = entry[u'Parution au JO'],
            start_date = entry[u"Date d'effet"],
            taxipp_code = taxipp_name_by_label[value_label],
            title = value_label,
            unit = entry[value_label][1]
                if entry[value_label] is not None
                else None,
            value = entry[value_label][0]
                if entry[value_label] is not None
                else None,
            ))
        value_label = u'Plafond de la Sécurité sociale (annuel)'
        parameters.append(dict(
            comment = entry[u"Notes"],
            description = description,
            format = u'float',
            legislative_reference = entry[u'Référence législative'],
            official_publication_date = entry[u'Parution au JO'],
            start_date = entry[u"Date d'effet"],
            taxipp_code = taxipp_name_by_label[value_label],
            title = value_label,
            unit = entry[value_label][1] if entry[value_label] is not None else None,
            value = entry[value_label][0] if entry[value_label] is not None else None,
            ))

    parameter_upsert_url = urlparse.urljoin(conf['law_to_code.site_url'], 'api/1/parameters/upsert')
    for parameter in parameters:
        response = requests.post(parameter_upsert_url,
            data = unicode(json.dumps(dict(
                api_key = conf['law_to_code.api_key'],
                value = parameter,
                ), ensure_ascii = False, indent = 2)).encode('utf-8'),
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': conf['user_agent']
                }
            )
        if not response.ok:
            print response.json()
            response.raise_for_status()

    return 0


def transform_xls_cell_to_json(book, type, value, xf_index):
    """Convert an XLS cell (type & value) to an unicode string.

    Code taken from http://code.activestate.com/recipes/546518-simple-conversion-of-excel-files-into-csv-and-yaml/

    Type Codes:
    EMPTY   0
    TEXT    1 a Unicode string
    NUMBER  2 float
    DATE    3 float
    BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
    ERROR   5
    """
    if type == 0:
        value = None
    elif type == 1:
        if not value:
            value = None
    elif type == 2:
        # NUMBER
        value_int = int(value)
        if value_int == value:
            value = value_int
        xf = book.xf_list[xf_index] # gets an XF object
        format_key = xf.format_key
        format = book.format_map[format_key] # gets a Format object
        format_str = format.format_str # this is the "number format string"
        if format_str.endswith(ur'\ "€"'):
            return (value, u'EUR')
        if format_str.endswith(ur'\ [$FRF]'):
            return (value, u'FRF')
        print value, format_str
        TODO
    elif type == 3:
        # DATE
        y, m, d, hh, mm, ss = xlrd.xldate_as_tuple(value, book.datemode)
        date = u'{0:04d}-{1:02d}-{2:02d}'.format(y, m, d) if any(n != 0 for n in (y, m, d)) else None
        value = u'T'.join(
            fragment
            for fragment in (
                date,
                u'{0:02d}:{1:02d}:{2:02d}'.format(hh, mm, ss)
                    if any(n != 0 for n in (hh, mm, ss)) or date is None
                    else None,
                )
            if fragment is not None
            )
    elif type == 4:
        value = bool(value)
    elif type == 5:
        # ERROR
        value = xlrd.error_text_from_code[value]
    return value


if __name__ == "__main__":
    sys.exit(main())
