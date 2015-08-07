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

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds, default_compta, fill_entries, \
    set_accounting_system, add_entry
from diacamma.accounting.views_accounts import ChartsAccountList, \
     ChartsAccountDel, ChartsAccountShow, ChartsAccountAddModify, \
    FiscalYearBegin, FiscalYearImport, FiscalYearClose, FiscalYearReportLastYear, \
    ChartsAccountListing
from diacamma.accounting.models import FiscalYear
from diacamma.accounting.views_entries import EntryAccountEdit, \
    EntryLineAccountList
from base64 import b64decode
from django.utils import six

class ChartsAccountTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        set_accounting_system()
        initial_thirds()
        default_compta()
        fill_entries(1)
        rmtree(get_user_dir(), True)

    def test_all(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 15)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Resultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

    def test_asset(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 159.98€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 125.97€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="name"]', '512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="blue"]}Débit: 1135.93€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="code"]', '531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="name"]', '531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="last_year_total"]', '{[font color="blue"]}Débit: 114.45€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 79.63€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 114.45€{[/font]}')

    def test_liability(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 78.24€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
    def test_equity(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')

    def test_revenue(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'3'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 230.62€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 196.61€{[/font]}')

    def test_expense(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'4'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '601000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '601000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 78.24€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '602000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="name"]', '602000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 63.94€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 63.94€{[/font]}')

    def test_contraaccounts(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'5'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 0)

    def test_show(self):
        self.factory.xfer = ChartsAccountShow()
        self.call('/diacamma.accounting/chartsAccountShow', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountShow')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/HEADER', 7)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_value"]', '21 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.designation"]', 'vente 1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', 'E')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '6')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_value"]', '21 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.designation"]', 'vente 2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', '125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.date_value"]', '24 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.designation"]', 'vente 3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="credit"]', '34.01€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', '---')

    def test_delete(self):
        self.factory.xfer = ChartsAccountDel()
        self.call('/diacamma.accounting/chartsAccountDel', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'5', 'chartsaccount':'10'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'chartsAccountDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Impossible de supprimer cet enregistrement: il est associé avec d'autres sous-enregistrements")
        self.factory.xfer = ChartsAccountDel()
        self.call('/diacamma.accounting/chartsAccountDel', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'5', 'chartsaccount':'9'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'chartsAccountDel')

    def test_add(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', None)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'2301'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '2301')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', 'Immobilisations en cours')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Actif')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'3015'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '3015!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'abcd'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', 'abcd!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

    def test_modify(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'7061'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '7061')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'3015'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '3015!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'abcd'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', 'abcd!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'6125'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '6125!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Changement non permis!{[/font]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = ChartsAccountListing()
        self.call('/diacamma.accounting/chartsAccountListing', {'year':'1', 'type_of_account':'-1', 'PRINT_MODE':'4', 'MODEL':6}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'chartsAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 21, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de plan comptable"')
        self.assertEqual(content_csv[3].strip(), '"code";"nom";"report à nouveau";"total exercice";"total validé";')
        self.assertEqual(content_csv[4].strip(), '"106000";"106000";"Crédit: 1250.47€";"Crédit: 1250.47€";"Crédit: 1250.47€";')
        self.assertEqual(content_csv[9].strip(), '"512000";"512000";"Débit: 1135.93€";"Débit: 1130.29€";"Débit: 1130.29€";')
        self.assertEqual(content_csv[10].strip(), '"531000";"531000";"Débit: 114.45€";"Crédit: 79.63€";"Débit: 114.45€";')

        self.factory.xfer = ChartsAccountListing()
        self.call('/diacamma.accounting/chartsAccountListing', {'year':'1', 'type_of_account':'4', 'PRINT_MODE':'4', 'MODEL':6}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'chartsAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 11, str(content_csv))

class FiscalYearWorkflowTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        set_accounting_system()
        initial_thirds()
        default_compta()
        fill_entries(1)
        rmtree(get_user_dir(), True)

    def test_begin_simple(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)  # pylint: disable=no-member

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Commencer', 'images/ok.png', 'diacamma.accounting', 'fiscalYearBegin', 0, 1, 1))

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.DialogBox', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_xml_equal('TEXT', "Voulez-vous commencer 'Exercice du 1 janvier 2015 au 31 décembre 2015", True)

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Clôturer', 'images/ok.png', 'diacamma.accounting', 'fiscalYearClose', 0, 1, 1))

    def test_begin_lastyearnovalid(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)  # pylint: disable=no-member
        new_entry = add_entry(1, 1, '2015-04-11', 'Report à nouveau aussi', '-1|1|0|37.61|None|\n-2|2|0|-37.61|None|', False)

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Des écritures de report à nouveau ne sont pas validées!")

        new_entry.closed()

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member

    def test_begin_withbenef(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)  # pylint: disable=no-member
        add_entry(1, 1, '2015-04-11', 'Report à nouveau bénèf', '-1|6|0|123.45|None|\n-2|2|0|123.45|None|', True)

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '110000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 123.45€{[/font]}')

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', "{[i]}Vous avez un bénéfice de 123.45€.{[br/]}", True)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="profit_account"]', '5')
        self.assert_count_equal('COMPONENTS/SELECT[@name="profit_account"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'profit_account':'5', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 1373.92€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '110000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')

    def test_begin_dont_add_report(self):
        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'year':'1', 'journal':'1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal("COMPONENTS/SELECT[@name='journal']/CASE", 4)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '2')

    def test_import_charsaccount(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=FiscalYear.objects.get(id=1))  # pylint: disable=no-member
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)  # pylint: disable=no-member
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)  # pylint: disable=no-member

        self.factory.xfer = FiscalYearImport()
        self.call('/diacamma.accounting/fiscalYearImport', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'fiscalYearImport')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice n'a pas d'exercice précédent!")

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 15)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/ACTIONS/ACTION', 3)

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/ACTIONS/ACTION', 4)
        self.assert_action_equal('COMPONENTS/GRID[@name="chartsaccount"]/ACTIONS/ACTION[4]', ('importer', None, 'diacamma.accounting', 'fiscalYearImport', 0, 1, 1))

        self.factory.xfer = FiscalYearImport()
        self.call('/diacamma.accounting/fiscalYearImport', {'CONFIRME':'YES', 'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearImport')

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 15)

        self.factory.xfer = FiscalYearImport()
        self.call('/diacamma.accounting/fiscalYearImport', {'CONFIRME':'YES', 'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearImport')

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 15)

    def test_close(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)  # pylint: disable=no-member
        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearImport', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'fiscalYearImport')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice n'est pas 'en cours'!")

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearImport', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'fiscalYearImport')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice a des écritures non-validées et pas d'exercice suivant!")

        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=FiscalYear.objects.get(id=1))  # pylint: disable=no-member

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.DialogBox', 'diacamma.accounting', 'fiscalYearClose')
        text_value = self.get_first_xpath('TEXT').text

        self.assertTrue('Voulez-vous cloturer cet exercice?' in text_value, text_value)
        self.assertTrue('4 écritures ne sont pas validées' in text_value, text_value)

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'1', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 23)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Resultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'2', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Resultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')  # pylint: disable=line-too-long

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 2)  # pylint: disable=no-member

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'1', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 18)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 196.61€ - {[b]}Charge:{[/b]} 76.28€ = {[b]}Resultat:{[/b]} 120.33€ | {[b]}Trésorie:{[/b]} 1244.74€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'2', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 8)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 34.01€ - {[b]}Charge:{[/b]} 272.32€ = {[b]}Resultat:{[/b]} -238.31€ | {[b]}Trésorie:{[/b]} -194.08€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')  # pylint: disable=line-too-long

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 17)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[4]/VALUE[@name="code"]', '120')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[4]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 120.33€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[5]/VALUE[@name="code"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[5]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[6]/VALUE[@name="code"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[6]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[7]/VALUE[@name="code"]', '418')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[7]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 125.97€{[/font]}')

    def test_import_lastyear(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=FiscalYear.objects.get(id=1))  # pylint: disable=no-member
        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)  # pylint: disable=no-member
        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 2)  # pylint: disable=no-member
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)  # pylint: disable=no-member

        self.factory.xfer = FiscalYearReportLastYear()
        self.call('/diacamma.accounting/fiscalYearReportLastYear', {'CONFIRME':'YES', 'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)  # pylint: disable=no-member

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'2', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 15)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 34.01€ - {[b]}Charge:{[/b]} 272.32€ = {[b]}Resultat:{[/b]} -238.31€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'2', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 10)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '110')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 120.33€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[4]/VALUE[@name="code"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[4]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 159.98€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[5]/VALUE[@name="code"]', '418')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[5]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')

        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('ACTIONS/ACTION', 2)