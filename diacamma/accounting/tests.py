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
from datetime import date, timedelta
from base64 import b64decode
from django.utils import six

from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.CORE.views import StatusMenu
from lucterios.contacts.views import CustomFieldAddModify

from diacamma.accounting.views import ThirdList, ThirdAdd, ThirdSave, ThirdShow, AccountThirdAddModify, AccountThirdDel, ThirdListing, ThirdDisable, ThirdEdit, ThirdSearch
from diacamma.accounting.views_admin import Configuration, ConfigurationAccountingSystem, JournalAddModify, JournalDel, FiscalYearAddModify, FiscalYearActive, FiscalYearDel
from diacamma.accounting.views_other import ModelEntryList, ModelEntryAddModify, ModelLineEntryAddModify
from diacamma.accounting.test_tools import initial_contacts, fill_entries_fr, initial_thirds_fr, create_third, fill_accounts_fr, fill_thirds_fr, default_compta_fr, set_accounting_system, add_models
from diacamma.accounting.models import FiscalYear, Third
from diacamma.accounting.system import get_accounting_system, accounting_system_ident
from diacamma.accounting.tools import current_system_account, clear_system_account
from diacamma.accounting.views_entries import EntryAccountModelSelector
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import CustomField


class ThirdTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        initial_contacts()
        rmtree(get_user_dir(), True)
        clear_system_account()

    def test_add_abstract(self):
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 0)

        self.factory.xfer = ThirdAdd()
        self.calljson('/diacamma.accounting/thirdAdd', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(('SELECT', 'modelname'), 'contacts.AbstractContact', (2, 0, 3, 1))
        self.assert_select_equal('modelname', 3)  # nb=3
        self.assert_count_equal('abstractcontact', 8)

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 1)
        self.assert_json_equal('', 'third/@0/contact', 'Dalton Joe')
        self.assert_json_equal('', 'third/@0/accountthird_set', '')

    def test_add_legalentity(self):
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 0)

        self.factory.xfer = ThirdAdd()
        self.calljson('/diacamma.accounting/thirdAdd', {'modelname': 'contacts.LegalEntity'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(('SELECT', 'modelname'), 'contacts.LegalEntity', (2, 0, 3, 1))
        self.assert_grid_equal('legal_entity', {"name": "nom", "tel1": "tel1", "tel2": "tel2", "email": "courriel"}, 3)  # nb=4

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'legal_entity', 'legal_entity': 7, 'new_account': '401'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 1)
        self.assert_json_equal('', 'third/@0/contact', 'Minimum')
        self.assert_json_equal('', 'third/@0/accountthird_set', '401')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_json_equal('', '#show/action/extension', 'lucterios.contacts')
        self.assert_json_equal('', '#show/action/action', 'legalEntityShow')
        self.assert_json_equal('', '#show/action/params/legal_entity', 7)

    def test_add_individual(self):
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 0)

        self.factory.xfer = ThirdAdd()
        self.calljson('/diacamma.accounting/thirdAdd', {'modelname': 'contacts.Individual'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(('SELECT', 'modelname'), 'contacts.Individual', (2, 0, 3, 1))
        self.assert_grid_equal('individual', {"firstname": "prénom", "lastname": "nom", "tel1": "tel1", "tel2": "tel2", "email": "courriel"}, 5)  # nb=5

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'individual', 'individual': 3, 'new_account': '401;411'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 1)
        self.assert_json_equal('', 'third/@0/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@0/accountthird_set', '401{[br/]}411')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Dalton William')
        self.assert_json_equal('', '#show/action/extension', 'lucterios.contacts')
        self.assert_json_equal('', '#show/action/action', 'individualShow')
        self.assert_json_equal('', '#show/action/params/individual', 3)

    def test_check_double(self):
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 0)

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assertEqual(self.response_json['action']['action'], 'thirdShow')
        self.assertEqual(self.response_json['action']['params']['third'], 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 1)

    def test_show(self):
        create_third([3])
        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertEqual(len(self.json_actions), 2)
        self.assertTrue('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4)
        self.assert_json_equal('LABELFORM', 'contact', 'Dalton William')
        self.assert_json_equal('LABELFORM', 'status', 'Actif')
        self.assert_grid_equal('accountthird', {'code': "code", 'total_txt': "total"}, 0)  # nb=2
        self.assert_count_equal('accountthird', 0)
        self.assert_json_equal('LABELFORM', 'total', '0.00€')

        self.factory.xfer = AccountThirdAddModify()
        self.calljson('/diacamma.accounting/accountThirdAddModify', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'accountThirdAddModify')
        self.assert_count_equal('', 2)
        self.assert_json_equal('EDIT', 'code', '')

        self.factory.xfer = AccountThirdAddModify()
        self.calljson('/diacamma.accounting/accountThirdAddModify', {'SAVE': 'YES', "third": 1, 'code': '411'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'accountThirdAddModify')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('accountthird', 1)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@0/total_txt', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('LABELFORM', 'total', '0.00€')

        self.factory.xfer = AccountThirdDel()
        self.calljson('/diacamma.accounting/accountThirdDel', {'CONFIRME': 'YES', "accountthird": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'accountThirdDel')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('accountthird', 0)

        fill_thirds_fr()
        default_compta_fr()

        self.factory.xfer = AccountThirdAddModify()
        self.calljson('/diacamma.accounting/accountThirdAddModify', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'accountThirdAddModify')
        self.assert_count_equal('', 2)
        self.assert_json_equal('SELECT', 'code', '401')

    def test_show_withdata(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 4 + 3)
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_json_equal('LABELFORM', 'status', 'Actif')
        self.assert_grid_equal('accountthird', {'code': "code", 'total_txt': "total"}, 2)  # nb=2
        self.assert_json_equal('', 'accountthird/@0/id', '5')
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@0/total_txt', '{[font color="blue"]}Débit: 34.01€{[/font]}')
        self.assert_json_equal('', 'accountthird/@1/id', '6')
        self.assert_json_equal('', 'accountthird/@1/code', '401')
        self.assert_json_equal('', 'accountthird/@1/total_txt', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('LABELFORM', 'total', '-34.01€')

        self.assert_json_equal('SELECT', 'lines_filter', '0')
        self.assert_select_equal('lines_filter', 3)  # nb=3
        self.assert_count_equal('entryline', 3)
        self.assert_json_equal('', 'entryline/@0/entry.num', '2')
        self.assert_json_equal('', 'entryline/@0/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry.num', '3')
        self.assert_json_equal('', 'entryline/@1/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@1/debit', '{[font color="blue"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@2/entry.num', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}34.01€{[/font]}')

        self.factory.xfer = AccountThirdDel()
        self.calljson('/diacamma.accounting/accountThirdDel', {"accountthird": 5}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'accountThirdDel')
        self.assert_json_equal('', 'message', "Ce compte n'est pas soldé !")

        self.factory.xfer = AccountThirdDel()
        self.calljson('/diacamma.accounting/accountThirdDel', {"accountthird": 6}, False)
        self.assert_observer('core.dialogbox', 'diacamma.accounting', 'accountThirdDel')

    def test_show_withdata_linesfilter(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4, 'lines_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 4 + 3)
        self.assert_json_equal('SELECT', 'lines_filter', '0')
        self.assert_select_equal('lines_filter', 3)  # nb=3
        self.assert_grid_equal('entryline', {"entry.num": "N°", "entry.date_entry": "date d'écriture", "entry.date_value": "date de pièce", "designation_ref": "nom",
                                             "entry_account": "compte", 'debit': 'débit', 'credit': 'crédit', "costaccounting": "comptabilité analytique", "entry.link": "lettrage"}, 3)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4, 'lines_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 4 + 3)
        self.assert_json_equal('SELECT', 'lines_filter', '1')
        self.assert_select_equal('lines_filter', 3)  # nb=3
        self.assert_count_equal('entryline', 1)

        default_compta_fr()

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4, 'lines_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 4 + 3)
        self.assert_json_equal('SELECT', 'lines_filter', '0')
        self.assert_select_equal('lines_filter', 3)  # nb=3
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4, 'lines_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 4 + 3)
        self.assert_json_equal('SELECT', 'lines_filter', '2')
        self.assert_select_equal('lines_filter', 3)  # nb=3
        self.assert_count_equal('entryline', 3)

    def test_list(self):
        fill_thirds_fr()
        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'legal_entity', 'legal_entity': 7, 'new_account': '421;451'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'individual', 'individual': 3, 'new_account': '421'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('', 6)
        self.assert_grid_equal('third', {'contact': "contact", 'accountthird_set': "compte"}, 7)  # nb=2
        self.assert_json_equal('', 'third/@0/contact', 'Dalton Avrel')
        self.assert_json_equal('', 'third/@0/accountthird_set', '401')
        self.assert_json_equal('', 'third/@1/contact', 'Dalton Jack')
        self.assert_json_equal('', 'third/@1/accountthird_set', '411')
        self.assert_json_equal('', 'third/@2/contact', 'Dalton Joe')
        self.assert_json_equal('', 'third/@2/accountthird_set', '411')
        self.assert_json_equal('', 'third/@3/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@3/accountthird_set', '411{[br/]}421')
        self.assert_json_equal('', 'third/@4/contact', 'Luke Lucky')
        self.assert_json_equal('', 'third/@4/accountthird_set', '411{[br/]}401')
        self.assert_json_equal('', 'third/@5/contact', 'Maximum')
        self.assert_json_equal('', 'third/@5/accountthird_set', '401')
        self.assert_json_equal('', 'third/@6/contact', 'Minimum')
        self.assert_json_equal('', 'third/@6/accountthird_set', '411{[br/]}401{[br/]}421{[br/]}451')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'GRID_ORDER%third': '1', 'GRID_ORDER%third+': '-'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 7)
        self.assert_json_equal('', 'third/@0/contact', 'Dalton Avrel')
        self.assert_json_equal('', 'third/@1/contact', 'Dalton Jack')
        self.assert_json_equal('', 'third/@2/contact', 'Dalton Joe')
        self.assert_json_equal('', 'third/@3/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@4/contact', 'Luke Lucky')
        self.assert_json_equal('', 'third/@5/contact', 'Maximum')
        self.assert_json_equal('', 'third/@6/contact', 'Minimum')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'GRID_ORDER%third': '1', 'GRID_ORDER%third+': '+'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 7)
        self.assert_json_equal('', 'third/@6/contact', 'Dalton Avrel')
        self.assert_json_equal('', 'third/@5/contact', 'Dalton Jack')
        self.assert_json_equal('', 'third/@4/contact', 'Dalton Joe')
        self.assert_json_equal('', 'third/@3/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@2/contact', 'Luke Lucky')
        self.assert_json_equal('', 'third/@1/contact', 'Maximum')
        self.assert_json_equal('', 'third/@0/contact', 'Minimum')

    def test_list_withfilter(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)

        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'legal_entity', 'legal_entity': 7, 'new_account': '421;451'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.factory.xfer = ThirdSave()
        self.calljson('/diacamma.accounting/thirdSave', {'pkname': 'individual', 'individual': 3, 'new_account': '421'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdSave')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'filter': 'dalton joe'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('', 6)
        self.assert_grid_equal('third', {'contact': "contact", 'accountthird_set': "compte"}, 1)  # nb=2
        self.assert_json_equal('', 'third/@0/contact', 'Dalton Joe')
        self.assert_json_equal('', 'third/@0/accountthird_set', '411')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'thirdtype': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 5)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'thirdtype': 2}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 4)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'thirdtype': 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'thirdtype': 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 2)

    def test_list_display(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('', 6)
        self.assert_grid_equal('third', {'contact': "contact", 'accountthird_set': "compte", 'total': "total"}, 7)  # nb=3
        self.assert_count_equal('third', 7)
        self.assert_json_equal('', 'third/@1/contact', 'Dalton Jack')
        self.assert_json_equal('', 'third/@1/accountthird_set', '411')
        self.assert_json_equal('', 'third/@1/total', '0.00€')
        self.assert_json_equal('', 'third/@3/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@3/accountthird_set', '411')
        self.assert_json_equal('', 'third/@3/total', '-125.97€')
        self.assert_json_equal('', 'third/@6/contact', 'Minimum')
        self.assert_json_equal('', 'third/@6/accountthird_set', '411{[br/]}401')
        self.assert_json_equal('', 'third/@6/total', '-34.01€')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'show_filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('', 6)
        self.assert_grid_equal('third', {'contact': "contact", 'accountthird_set': "compte", 'total': "total"}, 3)  # nb=3
        self.assert_json_equal('', 'third/@0/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@0/accountthird_set', '411')
        self.assert_json_equal('', 'third/@0/total', '-125.97€')
        self.assert_json_equal('', 'third/@1/contact', 'Maximum')
        self.assert_json_equal('', 'third/@1/accountthird_set', '401')
        self.assert_json_equal('', 'third/@1/total', '78.24€')
        self.assert_json_equal('', 'third/@2/contact', 'Minimum')
        self.assert_json_equal('', 'third/@2/accountthird_set', '411{[br/]}401')
        self.assert_json_equal('', 'third/@2/total', '-34.01€')

    def test_listing(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        self.factory.xfer = ThirdListing()
        self.calljson('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('', 4)
        self.assert_comp_equal(('SELECT', 'PRINT_MODE'), "3", (1, 0, 1, 1))
        self.assert_select_equal('PRINT_MODE', 2)  # nb=2
        self.assert_comp_equal(('SELECT', 'MODEL'), "5", (1, 1, 1, 1))
        self.assert_select_equal('MODEL', 1)  # nb=1
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = ThirdListing()
        self.calljson('/diacamma.accounting/thirdListing',
                      {'PRINT_MODE': '4', 'MODEL': 5}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'thirdListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 14, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton Avrel";"401";"0.00€";')
        self.assertEqual(content_csv[5].strip(), '"Dalton Jack";"411";"0.00€";')
        self.assertEqual(content_csv[6].strip(), '"Dalton Joe";"411";"0.00€";')
        self.assertEqual(content_csv[7].strip(), '"Dalton William";"411";"-125.97€";')
        self.assertEqual(content_csv[8].strip(), '"Luke Lucky";"411 401";"0.00€";')
        self.assertEqual(content_csv[9].strip(), '"Maximum";"401";"78.24€";')
        self.assertEqual(content_csv[10].strip(), '"Minimum";"411 401";"-34.01€";')

        self.factory.xfer = ThirdListing()
        self.calljson('/diacamma.accounting/thirdListing', {'PRINT_MODE': '4', 'MODEL': 5, 'filter': 'joe'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'thirdListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 8, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton Joe";"411";"0.00€";')

        self.factory.xfer = ThirdListing()
        self.calljson('/diacamma.accounting/thirdListing', {'PRINT_MODE': '4', 'MODEL': 5, 'show_filter': '2'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'thirdListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton William";"411";"-125.97€";')
        self.assertEqual(content_csv[5].strip(), '"Maximum";"401";"78.24€";')
        self.assertEqual(content_csv[6].strip(), '"Minimum";"411 401";"-34.01€";')

    def test_list_disable(self):
        fill_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 7)

        self.factory.xfer = ThirdDisable()
        self.calljson('/diacamma.accounting/thirdDisable', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdDisable')
        self.assert_count_equal('', 2)

        self.factory.xfer = ThirdDisable()
        self.calljson('/diacamma.accounting/thirdDisable', {'limit_date': '2015-02-18'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdDisable')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 4)

    def test_with_customize(self):
        CustomField.objects.create(modelname='accounting.Third', name='categorie', kind=4, args="{'list':['---','petit','moyen','gros']}")
        CustomField.objects.create(modelname='accounting.Third', name='value', kind=1, args="{'min':0,'max':100}")
        create_third([3])
        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assertEqual(len(self.json_actions), 3)
        self.assertTrue('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 9 + 4 + 2)
        self.assert_json_equal('LABELFORM', 'contact', 'Dalton William')
        self.assert_json_equal('LABELFORM', 'status', 'Actif')
        self.assert_grid_equal('accountthird', {'code': "code", 'total_txt': "total"}, 0)  # nb=2
        self.assert_json_equal('LABELFORM', 'total', '0.00€')
        self.assert_json_equal('LABELFORM', 'custom_1', "---")
        self.assert_json_equal('LABELFORM', 'custom_2', "0")

        self.factory.xfer = ThirdEdit()
        self.calljson('/diacamma.accounting/thirdEdit', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdEdit')
        self.assert_count_equal('', 2 + 2)
        self.assert_json_equal('LABELFORM', 'contact', 'Dalton William')
        self.assert_json_equal('SELECT', 'custom_1', "0")
        self.assert_select_equal('custom_1', 4)  # nb=4
        self.assert_json_equal('FLOAT', 'custom_2', "0")

        self.factory.xfer = ThirdEdit()
        self.calljson('/diacamma.accounting/thirdEdit', {"third": 1, 'custom_1': '2', 'custom_2': '27', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdEdit')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Dalton William')
        self.assert_json_equal('LABELFORM', 'custom_1', "moyen")
        self.assert_json_equal('LABELFORM', 'custom_2', "27")

        my_third = Third.objects.get(id=1)
        self.assertEqual("moyen", my_third.get_custom_by_name("categorie"))
        self.assertEqual(27, my_third.get_custom_by_name("value"))
        self.assertEqual(None, my_third.get_custom_by_name("truc"))

    def test_search(self):
        CustomField.objects.create(modelname='accounting.Third', name='categorie', kind=4, args="{'list':['---','petit','moyen','gros']}")
        CustomField.objects.create(modelname='accounting.Third', name='value', kind=1, args="{'min':0,'max':100}")
        search_field_list = Third.get_search_fields()
        self.assertEqual(8 + 2 + 2, len(search_field_list), search_field_list)

        fill_thirds_fr()
        self.factory.xfer = ThirdSearch()
        self.calljson('/diacamma.accounting/thirdSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdSearch')
        self.assert_count_equal('third', 7)

    def test_print_model(self):
        CustomField.objects.create(modelname='accounting.Third', name='categorie', kind=4, args="{'list':['---','petit','moyen','gros']}")
        CustomField.objects.create(modelname='accounting.Third', name='value', kind=1, args="{'min':0,'max':100}")
        print_field_list = Third.get_all_print_fields()
        self.assertEqual(13, len(print_field_list), print_field_list)


class AdminTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.calljson('/CORE/statusMenu', {}, False)
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_json_equal('LABELFORM', 'accountingtitle', "{[center]}{[u]}{[b]}Comptabilité{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'accounting_error', "{[center]}Pas d'exercice défini !{[/center]}")
        self.assert_action_equal('#accounting_conf/action',
                                 ("conf.", None, 'diacamma.accounting', 'configuration', 0, 1, 1))

    def test_default_configuration(self):
        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assertTrue('__tab_4' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_5' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 4 + 5 + 2 + 7)
        self.assert_grid_equal('fiscalyear', {"begin": "début", "end": "fin", "status": "status", "is_actif": "actif"}, 0)  # nb=4

        self.assert_grid_equal('journal', {'name': "nom"}, 5)  # nb=1
        self.assert_json_equal('', 'journal/@0/name', 'Report à nouveau')
        self.assert_json_equal('', 'journal/@1/name', 'Achats')
        self.assert_json_equal('', 'journal/@2/name', 'Ventes')
        self.assert_json_equal('', 'journal/@3/name', 'Règlement')
        self.assert_json_equal('', 'journal/@4/name', 'Opérations diverses')

        self.assert_json_equal('LABELFORM', 'accounting-devise', '€')
        self.assert_json_equal('LABELFORM', 'accounting-devise-iso', 'EUR')
        self.assert_json_equal('LABELFORM', 'accounting-devise-prec', '2')
        self.assert_json_equal('LABELFORM', 'accounting-sizecode', '3')
        self.assert_json_equal('LABELFORM', 'accounting-needcost', 'Non')
        self.assert_json_equal('LABELFORM', 'accounting-code-report-filter', '')
        self.assert_grid_equal('custom_field', {'name': "nom", 'kind_txt': "type"}, 0)  # nb=2

    def test_configuration_accountsystem(self):
        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_select_equal('account_system', {'': '---', 'diacamma.accounting.system.french.FrenchSystemAcounting': 'Plan comptable générale Français', 'diacamma.accounting.system.belgium.BelgiumSystemAcounting': 'Plan comptable Belge'})

        self.factory.xfer = ConfigurationAccountingSystem()
        self.calljson('/diacamma.accounting/configurationAccountingSystem', {'account_system': 'diacamma.accounting.system.french.FrenchSystemAcounting'}, False)
        self.assert_observer('core.dialogbox', 'diacamma.accounting', 'configurationAccountingSystem')

        self.factory.xfer = ConfigurationAccountingSystem()
        self.calljson('/diacamma.accounting/configurationAccountingSystem', {'account_system': 'diacamma.accounting.system.french.FrenchSystemAcounting', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'configurationAccountingSystem')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_json_equal('LABELFORM', 'account_system', 'Plan comptable générale Français')

    def test_configuration_journal(self):
        self.factory.xfer = JournalAddModify()
        self.calljson('/diacamma.accounting/journalAddModify', {'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'journalAddModify')
        self.assert_count_equal('', 2)
        self.assert_json_equal('EDIT', 'name', 'Achats')

        self.factory.xfer = JournalAddModify()
        self.calljson('/diacamma.accounting/journalAddModify', {'SAVE': 'YES', 'journal': '2', 'name': 'Dépense'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('journal', 5)
        self.assert_json_equal('', 'journal/@1/id', 2)
        self.assert_json_equal('', 'journal/@1/name', 'Dépense')

        self.factory.xfer = JournalAddModify()
        self.calljson('/diacamma.accounting/journalAddModify', {'SAVE': 'YES', 'name': 'Caisse'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('journal', 6)
        self.assert_json_equal('', 'journal/@5/id', '6')
        self.assert_json_equal('', 'journal/@5/name', 'Caisse')

        self.factory.xfer = JournalDel()
        self.calljson('/diacamma.accounting/journalDel', {'journal': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'journalDel')
        self.assert_json_equal('', 'message', 'journal réservé !')

        self.factory.xfer = JournalDel()
        self.calljson('/diacamma.accounting/journalDel', {'CONFIRME': 'YES', 'journal': '6'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalDel')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('journal', 5)

    def test_configuration_fiscalyear(self):
        to_day = date.today()
        try:
            to_day_plus_1 = date(to_day.year + 1, to_day.month, to_day.day) - timedelta(days=1)
        except ValueError:
            to_day_plus_1 = date(to_day.year + 1, to_day.month, to_day.day - 1)

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_json_equal('', 'message', "Système comptable non défini !")

        set_accounting_system()

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('', 4)
        self.assert_json_equal('LABELFORM', 'status', 'en création')
        self.assert_json_equal('DATE', 'begin', to_day.isoformat())
        self.assert_json_equal('DATE', 'end', to_day_plus_1.isoformat())

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {'SAVE': 'YES', 'begin': '2015-07-01', 'end': '2016-06-30'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_grid_equal('fiscalyear', {"begin": "début", "end": "fin", "status": "status", "is_actif": "actif"}, 1)  # nb=4
        self.assert_json_equal('', 'fiscalyear/@0/begin', '2015-07-01')
        self.assert_json_equal('', 'fiscalyear/@0/end', '2016-06-30')
        self.assert_json_equal('', 'fiscalyear/@0/status', "en création")
        self.assert_json_equal('', 'fiscalyear/@0/is_actif', "1")

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('', 4)
        self.assertEqual(self.json_context['begin'], "2016-07-01")
        self.assert_json_equal('LABELFORM', 'status', 'en création')
        self.assert_json_equal('LABELFORM', 'begin', '1 juillet 2016')
        self.assert_json_equal('DATE', 'end', '2017-06-30')

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {'SAVE': 'YES', 'begin': '2016-07-01', 'end': '2017-06-30'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('fiscalyear', 2)
        self.assert_json_equal('', 'fiscalyear/@1/begin', '2016-07-01')
        self.assert_json_equal('', 'fiscalyear/@1/end', '2017-06-30')
        self.assert_json_equal('', 'fiscalyear/@1/status', "en création")
        self.assert_json_equal('', 'fiscalyear/@1/is_actif', "0")

        self.factory.xfer = FiscalYearActive()
        self.calljson('/diacamma.accounting/fiscalYearActive', {'fiscalyear': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearActive')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('fiscalyear', 2)
        self.assert_json_equal('', 'fiscalyear/@0/is_actif', "0")
        self.assert_json_equal('', 'fiscalyear/@1/is_actif', "1")

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_json_equal('', 'message', "Cet exercice n'est pas le dernier !")

        self.factory.xfer = FiscalYearAddModify()
        self.calljson('/diacamma.accounting/fiscalYearAddModify', {'fiscalyear': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('', 4)
        self.assert_json_equal('LABELFORM', 'status', 'en création')
        self.assert_json_equal('LABELFORM', 'begin', '1 juillet 2016')
        self.assert_json_equal('DATE', 'end', '2017-06-30')

    def test_confi_delete(self):
        year1 = FiscalYear.objects.create(
            begin='2014-07-01', end='2015-06-30', status=2, is_actif=False, last_fiscalyear=None)
        year2 = FiscalYear.objects.create(
            begin='2015-07-01', end='2016-06-30', status=1, is_actif=False, last_fiscalyear=year1)
        FiscalYear.objects.create(begin='2016-07-01', end='2017-06-30', status=0,
                                  is_actif=True, last_fiscalyear=year2)
        set_accounting_system()
        initial_thirds_fr()
        fill_accounts_fr()
        fill_entries_fr(3)

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('fiscalyear', 3)

        self.factory.xfer = FiscalYearDel()
        self.calljson(
            '/diacamma.accounting/fiscalYearDel', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_json_equal('', 'message', "Cet exercice n'est pas le dernier !")

        self.factory.xfer = FiscalYearDel()
        self.calljson(
            '/diacamma.accounting/fiscalYearDel', {'fiscalyear': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_json_equal('', 'message', "Cet exercice n'est pas le dernier !")

        self.factory.xfer = FiscalYearDel()
        self.calljson('/diacamma.accounting/fiscalYearDel', {'CONFIRME': 'YES', 'fiscalyear': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearDel')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('fiscalyear', 2)

        self.factory.xfer = FiscalYearDel()
        self.calljson('/diacamma.accounting/fiscalYearDel',
                      {'CONFIRME': 'YES', 'fiscalyear': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearDel')

        self.factory.xfer = FiscalYearDel()
        self.calljson('/diacamma.accounting/fiscalYearDel', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_json_equal('', 'message', "Cet exercice est terminé !")

    def test_system_accounting(self):
        clear_system_account()
        self.assertEqual(get_accounting_system('').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system('accountingsystem.foo.DummySystemAcounting').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system('diacamma.accounting.system.french.DummySystemAcounting').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system('diacamma.accounting.system.french.FrenchSystemAcounting').__class__.__name__, "FrenchSystemAcounting")
        self.assertEqual(get_accounting_system('diacamma.accounting.system.belgium.BelgiumSystemAcounting').__class__.__name__, "BelgiumSystemAcounting")
        self.assertEqual(accounting_system_ident('diacamma.accounting.system.french.DummySystemAcounting'), "---")
        self.assertEqual(accounting_system_ident('diacamma.accounting.system.french.FrenchSystemAcounting'), "french")
        self.assertEqual(accounting_system_ident('diacamma.accounting.system.belgium.BelgiumSystemAcounting'), "belgium")

        self.assertEqual(Params.getvalue("accounting-system"), "")
        self.assertEqual(current_system_account().__class__.__name__, "DefaultSystemAccounting")
        set_accounting_system()
        self.assertEqual(current_system_account().__class__.__name__, "FrenchSystemAcounting")

    def test_configuration_customfield(self):
        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('custom_field', 0)
        self.assert_count_equal('#custom_field/actions', 3)

        self.factory.xfer = CustomFieldAddModify()
        self.calljson('/lucterios.contacts/customFieldAddModify', {"SAVE": "YES", 'name': 'aaa', 'modelname': 'accounting.Third', 'kind': '0', 'args_multi': 'n', 'args_min': '0', 'args_max': '0', 'args_prec': '0', 'args_list': ''}, False)
        self.assert_observer('core.acknowledge', 'lucterios.contacts', 'customFieldAddModify')

        self.factory.xfer = Configuration()
        self.calljson('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('custom_field', 1)


class ModelTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        initial_thirds_fr()
        rmtree(get_user_dir(), True)
        clear_system_account()
        default_compta_fr()

    def test_add(self):
        self.factory.xfer = ModelEntryList()
        self.calljson('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('', 3)
        self.assert_grid_equal('modelentry', {'journal': "journal", 'designation': "nom", 'total': "total"}, 0)  # nb=3

        self.factory.xfer = ModelEntryAddModify()
        self.calljson('/diacamma.accounting/modelEntryAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryAddModify')
        self.assert_count_equal('', 4)
        self.assert_select_equal('journal', 4)  # nb=4
        self.assert_select_equal('costaccounting', 1)  # nb=1

        self.factory.xfer = ModelEntryAddModify()
        self.calljson('/diacamma.accounting/modelEntryAddModify', {'SAVE': 'YES', 'journal': '2', 'designation': 'foo'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelEntryAddModify')

        self.factory.xfer = ModelEntryList()
        self.calljson('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('', 3)
        self.assert_grid_equal('modelentry', {'journal': "journal", 'designation': "nom", 'total': "total"}, 1)  # nb=3
        self.assert_json_equal('', 'modelentry/@0/journal', "Achats")
        self.assert_json_equal('', 'modelentry/@0/designation', "foo")
        self.assert_json_equal('', 'modelentry/@0/total', "0.00€")

    def test_addline(self):
        self.factory.xfer = ModelEntryAddModify()
        self.calljson('/diacamma.accounting/modelEntryAddModify', {'SAVE': 'YES', 'journal': '2', 'designation': 'foo'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelEntryAddModify')

        self.factory.xfer = ModelLineEntryAddModify()
        self.calljson('/diacamma.accounting/modelLineEntryAddModify',
                      {'modelentry': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelLineEntryAddModify')
        self.assert_count_equal('', 4)
        self.assert_json_equal('EDIT', 'code', '')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')

        self.factory.xfer = ModelLineEntryAddModify()
        self.calljson('/diacamma.accounting/modelLineEntryAddModify',
                      {'modelentry': '1', 'code': '411'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelLineEntryAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '411')
        self.assert_json_equal('SELECT', 'third', '0')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')

        self.factory.xfer = ModelLineEntryAddModify()
        self.calljson('/diacamma.accounting/modelLineEntryAddModify',
                      {'SAVE': 'YES', 'model': '1', 'modelentry': '1', 'code': '411', 'third': '3', 'credit_val': '19.37', 'debit_val': '0.0'}, False)

        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelLineEntryAddModify')

        self.factory.xfer = ModelEntryList()
        self.calljson('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('', 3)
        self.assert_grid_equal('modelentry', {'journal': "journal", 'designation': "nom", 'total': "total"}, 1)  # nb=3
        self.assert_json_equal('', 'modelentry/@0/journal', "Achats")
        self.assert_json_equal('', 'modelentry/@0/designation', "foo")
        self.assert_json_equal('', 'modelentry/@0/total', "19.37€")

    def test_selector(self):
        add_models()
        self.factory.xfer = EntryAccountModelSelector()
        self.calljson('/diacamma.accounting/entryAccountModelSelector', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assert_count_equal('', 3)
        self.assert_select_equal('model', 3)  # nb=2
        self.assert_json_equal('FLOAT', 'factor', '1.00')

        self.factory.xfer = EntryAccountModelSelector()
        self.calljson('/diacamma.accounting/entryAccountModelSelector', {'journal': 2}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assert_count_equal('', 3)
        self.assert_select_equal('model', 2)  # nb=1
        self.assert_json_equal('FLOAT', 'factor', '1.00')

    def test_insert(self):
        add_models()
        self.factory.xfer = EntryAccountModelSelector()
        self.calljson('/diacamma.accounting/entryAccountModelSelector', {'SAVE': 'YES', 'journal': '2', 'model': 1, 'factor': 2.50}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context['entryaccount'], 1)
        self.assertEqual(self.json_context['journal'], '2')
        self.assertEqual(self.response_json["action"]["id"], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json["action"]["params"]), 1)
        serial_entry = self.response_json["action"]["params"]['serial_entry'].split('\n')
        self.assertEqual(serial_entry[0][-22:], "|1|3|48.430000|0|None|", serial_entry[0])
        self.assertEqual(serial_entry[1][-23:], "|2|0|-48.430000|0|None|", serial_entry[1])

    def test_insert_with_costaccounting(self):
        add_models()
        self.factory.xfer = EntryAccountModelSelector()
        self.calljson('/diacamma.accounting/entryAccountModelSelector', {'SAVE': 'YES', 'journal': '2', 'model': 3, 'factor': 1.00}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context['entryaccount'], 1)
        self.assertEqual(self.json_context['journal'], '2')
        self.assertEqual(self.response_json["action"]["id"], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json["action"]["params"]), 1)
        serial_entry = self.response_json["action"]["params"]['serial_entry'].split('\n')
        self.assertEqual(serial_entry[0][-23:], "|1|3|-37.910000|0|None|", serial_entry[0])
        self.assertEqual(serial_entry[1][-23:], "|11|0|37.910000|2|None|", serial_entry[1])
