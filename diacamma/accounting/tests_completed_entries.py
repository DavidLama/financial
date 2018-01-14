# -*- coding: utf-8 -*-
'''
Describe test for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from shutil import rmtree
from os.path import exists
from base64 import b64decode
from datetime import date

from django.utils import six, formats

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir, get_user_path
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import StatusMenu

from diacamma.accounting.views_entries import EntryAccountList, EntryAccountListing, EntryAccountEdit, EntryAccountShow, \
    EntryAccountClose, EntryAccountCostAccounting, EntryAccountSearch
from diacamma.accounting.test_tools import default_compta, initial_thirds, fill_entries
from diacamma.accounting.views_other import CostAccountingList, CostAccountingClose, CostAccountingAddModify
from diacamma.accounting.views_reports import FiscalYearBalanceSheet, FiscalYearIncomeStatement, FiscalYearLedger, FiscalYearTrialBalance,\
    CostAccountingTrialBalance, CostAccountingLedger,\
    CostAccountingIncomeStatement
from diacamma.accounting.views_admin import FiscalYearExport
from diacamma.accounting.models import FiscalYear


class CompletedEntryTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        rmtree(get_user_dir(), True)
        fill_entries(1)

    def _goto_entrylineaccountlist(self, journal, filterlist, nb_line):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': journal, 'filter': filterlist}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', nb_line)

    def test_lastyear(self):
        self._goto_entrylineaccountlist(1, 0, 3)
        self.assert_json_equal('', 'entryline/@0/entry.num', '1')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[106] 106')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}1250.38€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@1/debit', '{[font color="blue"]}1135.93€{[/font]}')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[531] 531')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}114.45€{[/font]}')

    def test_buying(self):
        self._goto_entrylineaccountlist(2, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.link', 'C')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}194.08€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[607] 607')

        self.assert_json_equal('', 'entryline/@2/entry.num', '2')
        self.assert_json_equal('', 'entryline/@2/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@2/credit', '{[font color="green"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[602] 602')

        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry.link', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@4/credit', '{[font color="green"]}78.24€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[601] 601')

    def test_selling(self):
        self._goto_entrylineaccountlist(3, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '4')
        self.assert_json_equal('', 'entryline/@0/entry.link', 'E')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}70.64€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry.num', '4')
        self.assert_json_equal('', 'entryline/@1/entry.link', 'E')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[707] 707')

        self.assert_json_equal('', 'entryline/@2/entry.num', '6')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}125.97€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry.num', '6')
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[707] 707')

        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry.link', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[411 Minimum]')
        self.assert_json_equal('', 'entryline/@4/debit', '{[font color="blue"]}34.01€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry.num', '---')
        self.assert_json_equal('', 'entryline/@5/entry.link', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[707] 707')

    def test_payment(self):
        self._goto_entrylineaccountlist(4, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '3')
        self.assert_json_equal('', 'entryline/@0/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[512] 512')

        self.assert_json_equal('', 'entryline/@2/entry.num', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', 'C')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}194.08€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[531] 531')

        self.assert_json_equal('', 'entryline/@4/entry.num', '5')
        self.assert_json_equal('', 'entryline/@4/entry.link', 'E')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[411 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@4/credit', '{[font color="green"]}70.64€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[512] 512')

    def test_other(self):
        self._goto_entrylineaccountlist(5, 0, 2)
        self.assert_json_equal('', 'entryline/@0/entry.num', '7')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}12.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[627] 627')

    def _check_result(self):
        return self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

    def _check_result_with_filter(self):
        return self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 34.01€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 34.01€{[br/]}{[b]}Trésorerie :{[/b]} 70.64€ - {[b]}Validé :{[/b]} 70.64€{[/center]}')

    def test_all(self):
        self._goto_entrylineaccountlist(-1, 0, 23)
        self._check_result()

    def test_noclose(self):
        self._goto_entrylineaccountlist(-1, 1, 8)

    def test_close(self):
        self._goto_entrylineaccountlist(-1, 2, 15)

    def test_letter(self):
        self._goto_entrylineaccountlist(-1, 3, 12)

    def test_noletter(self):
        self._goto_entrylineaccountlist(-1, 4, 11)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.calljson('/CORE/statusMenu', {}, False)
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_json_equal('LABELFORM', 'accounting_year',
                               "{[center]}Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]{[/center]}")
        self.assert_json_equal('LABELFORM', 'accounting_result',
                               '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')
        self.assert_json_equal('LABELFORM', 'accountingtitle', "{[center]}{[u]}{[b]}Comptabilité{[/b]}{[/u]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 30, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste d\'écritures"')
        self.assertEqual(content_csv[3].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[4].strip(), '"1";"%s";"1 février 2015";"[106] 106";"Report à nouveau";"";"1250.38€";"";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[8].strip(), '"---";"---";"13 février 2015";"[607] 607";"depense 2";"194.08€";"";"C";')

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 15, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '2'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 22, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '3'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 19, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '4'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 18, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '4', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 13, str(content_csv))

    def test_search(self):
        self.factory.xfer = EntryAccountSearch()
        self.calljson('/diacamma.accounting/entryAccountSearch',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'entry.year||8||1//account.code||6||7'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountSearch')
        self.assert_count_equal('', 22)
        self.assert_count_equal('entryline', 3)

    def test_listing_search(self):
        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'entry.year||8||1//account.code||6||7'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste d\'écritures"')
        self.assertEqual(content_csv[3].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[4].strip(), '"4";"%s";"21 février 2015";"[707] 707";"vente 1";"";"70.64€";"E";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[6].strip(), '"---";"---";"24 février 2015";"[707] 707";"vente 3";"";"34.01€";"";')

    def test_costaccounting(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 4)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'entryaccount': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 10)
        self.assert_json_equal('LABELFORM', 'designation', 'depense 1')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', 'open')
        self.assert_count_equal('#entrylineaccount/actions', 1)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'entryaccount': '11'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'designation', 'Frais bancaire')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[512] 512')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[627] 627')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', 'close')
        self.assert_count_equal('#entrylineaccount/actions', 0)
        self.assertEqual(len(self.json_actions), 1)

    def test_costaccounting_list(self):
        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('', 5)
        self.assert_count_equal('costaccounting', 1)
        self.assert_json_equal('', 'costaccounting/@0/name', 'open')
        self.assert_json_equal('', 'costaccounting/@0/description', 'Open cost')
        self.assert_json_equal('', 'costaccounting/@0/year', '---')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '258.02€')
        self.assert_json_equal('', 'costaccounting/@0/total_result', '-187.38€')
        self.assert_json_equal('', 'costaccounting/@0/status', 'ouverte')
        self.assert_json_equal('', 'costaccounting/@0/is_default', '1')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

        self.factory.xfer = CostAccountingClose()
        self.calljson('/diacamma.accounting/costAccountingClose',
                      {'costaccounting': 2}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'costAccountingClose')
        self.assert_json_equal('', 'message', 'La comptabilité  "open" a des écritures non validées !')

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', 'journal': '2', "entryline": "8"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = CostAccountingClose()
        self.calljson('/diacamma.accounting/costAccountingClose',
                      {'CONFIRME': 'YES', 'costaccounting': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingClose')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 0)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

    def test_costaccounting_change(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('last_costaccounting', 3)  # nb=3
        self.assert_select_equal('year', 3)  # nb=3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'bbb', 'description': 'bbb', 'year': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 4

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/id', '3')
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/year', 'Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/id', '4')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/year', 'Exercice du 1 janvier 2016 au 31 décembre 2016 [en création]')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/id', '2')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/year', '---')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '258.02€')

        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', '---')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')
        self.assert_count_equal('', 3)
        self.assert_select_equal('cost_accounting_id', {0: None, 2: 'open', 3: 'aaa'})  # nb=3
        self.assert_json_equal('SELECT', 'cost_accounting_id', '2')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '2'}, False)  # -78.24 / +125.97
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'open')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '196.61€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '336.26€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '0'}, False)  # - -194.08 / 0
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', '---')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'aaa')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '125.97€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '272.32€')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'id': '3', 'year': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'costAccountingAddModify')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '4'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'aaa')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '125.97€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '272.32€')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 1, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 2, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': -1, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 0, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 4)

    def test_costaccounting_needed(self):
        Parameter.change_value('accounting-needcost', '1')
        Params.clear()
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'bbb', 'description': 'bbb', 'year': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 4

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')
        self.assert_count_equal('', 3)
        self.assert_select_equal('cost_accounting_id', {2: 'open', 3: 'aaa'})  # nb=2
        self.assert_json_equal('SELECT', 'cost_accounting_id', '2')

    def test_costaccounting_incomestatement(self):
        self.factory.xfer = CostAccountingIncomeStatement()
        self.calljson('/diacamma.accounting/costAccountingIncomeStatement', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingIncomeStatement')
        self.assertFalse('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_grid_equal('report_2', {"name": "Comptabilit\u00e9 analytique", "left": "Charges", "left_n": "Valeur", "left_b": "Budget", "space": "", "right": "Produits", "right_n": "Valeur", "right_b": "Budget"}, 5 + 6 + 2)

        self.factory.xfer = CostAccountingIncomeStatement()
        self.calljson('/diacamma.accounting/costAccountingIncomeStatement', {'costaccounting': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingIncomeStatement')
        self.assertFalse('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_grid_equal('report_1', {"left": "Charges", "left_n": "Valeur", "left_b": "Budget", "space": "", "right": "Produits", "right_n": "Valeur", "right_b": "Budget"}, 5)

    def test_costaccounting_ledger(self):
        self.factory.xfer = CostAccountingLedger()
        self.calljson('/diacamma.accounting/costAccountingLedger', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingLedger')
        self.assertTrue('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_1', 3 * 4)
        self.assert_count_equal('report_2', 3 * 4)

    def test_costaccounting_trialbalance(self):
        self.factory.xfer = CostAccountingTrialBalance()
        self.calljson('/diacamma.accounting/costAccountingTrialBalance', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingTrialBalance')
        self.assertTrue('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_1', 1 + 2)
        self.assert_count_equal('report_2', 1 + 2)

    def test_fiscalyear_balancesheet(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.calljson('/diacamma.accounting/fiscalYearBalanceSheet', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result()

    def test_fiscalyear_balancesheet_filter(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.calljson('/diacamma.accounting/fiscalYearBalanceSheet', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result_with_filter()

    def test_fiscalyear_incomestatement(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.calljson('/diacamma.accounting/fiscalYearIncomeStatement', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result()

    def test_fiscalyear_incomestatement_filter(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.calljson('/diacamma.accounting/fiscalYearIncomeStatement', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result_with_filter()

    def test_fiscalyear_ledger(self):
        self.factory.xfer = FiscalYearLedger()
        self.calljson('/diacamma.accounting/fiscalYearLedger', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result()

    def test_fiscalyear_ledger_filter(self):
        self.factory.xfer = FiscalYearLedger()
        self.calljson('/diacamma.accounting/fiscalYearLedger', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result_with_filter()

    def test_fiscalyear_trialbalance(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result()

    def test_fiscalyear_trialbalance_filter(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result_with_filter()

    def test_export(self):
        self.assertFalse(
            exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))
        self.factory.xfer = FiscalYearExport()
        self.calljson('/diacamma.accounting/fiscalYearExport', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearExport')
        self.assertTrue(exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))
