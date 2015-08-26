# -*- coding: utf-8 -*-
'''
Describe database model for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
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

from datetime import date, timedelta
from re import match

from django.db import models
from django.db.models.query import QuerySet
from django.db.models.aggregates import Sum, Max
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.models import LucteriosModel, get_value_converted, get_value_if_choices
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.contacts.models import AbstractContact
from diacamma.accounting.tools import get_amount_sum, format_devise, \
    current_system_account, currency_round


class Third(LucteriosModel):
    contact = models.ForeignKey(
        'contacts.AbstractContact', verbose_name=_('contact'), null=False)
    status = models.IntegerField(
        verbose_name=_('status'), choices=((0, _('Enable')), (1, _('Disable'))))

    def __str__(self):
        return six.text_type(self.contact.get_final_child())

    @classmethod
    def get_default_fields(cls):
        return ["contact", "accountthird_set"]

    @classmethod
    def get_other_fields(cls):
        return ["contact", "accountthird_set", (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ["status"]

    @classmethod
    def get_show_fields(cls):
        return {'': ['contact'], _('001@AccountThird information'): ["status", "accountthird_set", ((_('total'), 'total'),)]}

    @classmethod
    def get_print_fields(cls):
        return cls.get_other_fields()

    @classmethod
    def get_search_fields(cls):
        result = []
        for field_name in AbstractContact.get_search_fields():
            if not isinstance(field_name, tuple):
                result.append("contact." + field_name)
        result.extend(["status", "accountthird_set.code"])
        return result

    def get_total(self):
        return get_amount_sum(EntryLineAccount.objects.filter(third=self).aggregate(Sum('amount')))

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    class Meta(object):

        verbose_name = _('third')
        verbose_name_plural = _('thirds')


class AccountThird(LucteriosModel):
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=False, on_delete=models.CASCADE)
    code = models.CharField(_('code'), max_length=50)

    def __str__(self):
        return self.code

    def can_delete(self):
        nb_lines = EntryLineAccount.objects.filter(
            third=self.third, account__code=self.code).count()
        if nb_lines != 0:
            return _('This account has some entries!')
        else:
            return ''

    @classmethod
    def get_default_fields(cls):
        return ["code", (_('total'), 'total_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["code"]

    @property
    def current_charts(self):
        try:
            return ChartsAccount.objects.get(code=self.code, year=FiscalYear.get_current())
        except (ObjectDoesNotExist, LucteriosException):
            return None

    @property
    def total_txt(self):
        chart = self.current_charts
        if chart is not None:
            return format_devise(chart.credit_debit_way() * self.total, 2)
        else:
            return format_devise(0, 2)

    @property
    def total(self):
        return get_amount_sum(EntryLineAccount.objects.filter(third=self.third, account__code=self.code).aggregate(Sum('amount')))

    class Meta(object):

        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = []


class FiscalYear(LucteriosModel):

    begin = models.DateField(verbose_name=_('begin'))
    end = models.DateField(verbose_name=_('end'))
    status = models.IntegerField(verbose_name=_('status'), choices=(
        (0, _('building')), (1, _('running')), (2, _('finished'))), default=0)
    is_actif = models.BooleanField(
        verbose_name=_('actif'), default=False, db_index=True)
    last_fiscalyear = models.ForeignKey('FiscalYear', verbose_name=_(
        'last fiscal year'), related_name='next_fiscalyear', null=True, on_delete=models.SET_NULL)

    def init_dates(self):
        fiscal_years = FiscalYear.objects.order_by(
            'end')
        if len(fiscal_years) == 0:
            self.begin = date.today()
        else:
            last_fiscal_year = fiscal_years[len(fiscal_years) - 1]
            self.begin = last_fiscal_year.end + timedelta(days=1)
        self.end = date(
            self.begin.year + 1, self.begin.month, self.begin.day) - timedelta(days=1)

    def can_delete(self):
        fiscal_years = FiscalYear.objects.order_by(
            'end')
        if (len(fiscal_years) != 0) and (fiscal_years[len(fiscal_years) - 1].id != self.id):
            return _('This fiscal year is not the last!')
        elif self.status == 2:
            return _('Fiscal year finished!')
        else:
            return ''

    def delete(self, using=None):
        self.entryaccount_set.all().delete()
        LucteriosModel.delete(self, using=using)

    def set_has_actif(self):
        all_year = FiscalYear.objects.all()
        for year_item in all_year:
            year_item.is_actif = False
            year_item.save()
        self.is_actif = True
        self.save()

    @classmethod
    def get_default_fields(cls):
        return ['begin', 'end', 'status', 'is_actif']

    @classmethod
    def get_edit_fields(cls):
        return ['status', 'begin', 'end']

    @property
    def total_revenue(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=3, account__year=self,
                                                              entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_expense(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=4, account__year=self,
                                                              entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_cash(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__code__regex=current_system_account().get_cash_mask(),
                                                              account__year=self, entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_cash_close(self):

        return get_amount_sum(EntryLineAccount.objects.filter(entry__close=True, account__code__regex=current_system_account().get_cash_mask(),
                                                              account__year=self, entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_result_text(self):
        value = {}
        value['revenue'] = format_devise(self.total_revenue, 5)
        value['expense'] = format_devise(self.total_expense, 5)
        value['result'] = format_devise(
            self.total_revenue - self.total_expense, 5)
        value['cash'] = format_devise(self.total_cash, 5)
        value['closed'] = format_devise(self.total_cash_close, 5)
        res_text = _(
            '{[b]}Revenue:{[/b]} %(revenue)s - {[b]}Expense:{[/b]} %(expense)s = {[b]}Result:{[/b]} %(result)s | {[b]}Cash:{[/b]} %(cash)s - {[b]}Closed:{[/b]} %(closed)s')
        return res_text % value

    @property
    def has_no_lastyear_entry(self):
        val = get_amount_sum(EntryLineAccount.objects.filter(
            entry__journal__id=1, account__year=self).aggregate(Sum('amount')))
        return abs(val) < 0.0001

    def import_charts_accounts(self):
        if self.last_fiscalyear is None:
            raise LucteriosException(
                IMPORTANT, _("This fiscal year has not a last fiscal year!"))
        if self.status == 2:
            raise LucteriosException(IMPORTANT, _('Fiscal year finished!'))
        for last_charts_account in self.last_fiscalyear.chartsaccount_set.all():
            try:
                self.chartsaccount_set.get(
                    code=last_charts_account.code)
            except ObjectDoesNotExist:
                ChartsAccount.objects.create(year=self, code=last_charts_account.code, name=last_charts_account.name,
                                             type_of_account=last_charts_account.type_of_account)

    def run_report_lastyear(self):
        if self.last_fiscalyear is None:
            raise LucteriosException(
                IMPORTANT, _("This fiscal year has not a last fiscal year!"))
        if self.status != 0:
            raise LucteriosException(
                IMPORTANT, _("This fiscal year is not 'in building'!"))
        current_system_account().import_lastyear(self)

    def getorcreate_chartaccount(self, code, name=None):
        try:
            return self.chartsaccount_set.get(code=code)
        except ObjectDoesNotExist:
            descript, typeaccount = current_system_account().new_charts_account(
                code)
            if name is None:
                name = descript
            return ChartsAccount.objects.create(year=self, code=code, name=name, type_of_account=typeaccount)

    def move_entry_noclose(self):
        if self.status == 1:
            next_ficalyear = FiscalYear.objects.get(
                last_fiscalyear=self)
            for entry_noclose in EntryAccount.objects.filter(close=False, entrylineaccount__account__year=self).distinct():
                for entryline in entry_noclose.entrylineaccount_set.all():
                    entryline.account = next_ficalyear.getorcreate_chartaccount(
                        entryline.account.code, entryline.account.name)
                    entryline.save()
                entry_noclose.year = next_ficalyear
                entry_noclose.date_value = next_ficalyear.begin
                entry_noclose.save()

    @classmethod
    def get_current(cls, select_year=None):
        if select_year is None:
            try:
                year = FiscalYear.objects.get(
                    is_actif=True)
            except ObjectDoesNotExist:
                raise LucteriosException(
                    IMPORTANT, _('No fiscal year define!'))
        else:
            year = FiscalYear.objects.get(
                id=select_year)
        return year

    def get_account_list(self, num_cpt_txt, num_cpt):
        account_list = []
        first_account = None
        current_account = None
        for account in self.chartsaccount_set.all().filter(code__startswith=num_cpt_txt).order_by('code'):
            account_list.append((account.id, six.text_type(account)))
            if first_account is None:
                first_account = account
            if account.id == num_cpt:
                current_account = account
        if current_account is None:
            current_account = first_account

        return account_list, current_account

    def __str__(self):
        status = get_value_if_choices(self.status, self._meta.get_field(
            'status'))
        return _("Fiscal year from %(begin)s to %(end)s [%(status)s]") % {'begin': get_value_converted(self.begin), 'end': get_value_converted(self.end), 'status': status}

    class Meta(object):

        verbose_name = _('fiscal year')
        verbose_name_plural = _('fiscal years')


class CostAccounting(LucteriosModel):

    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.CharField(
        _('description'), max_length=50, unique=True)
    status = models.IntegerField(verbose_name=_('status'), choices=(
        (0, _('opened')), (1, _('closed'))), default=0)
    last_costaccounting = models.ForeignKey('CostAccounting', verbose_name=_(
        'last cost accounting'), related_name='next_costaccounting', null=True, on_delete=models.SET_NULL)
    is_default = models.BooleanField(verbose_name=_('default'), default=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ['name', 'description', (_('total revenue'), 'total_revenue'), (_('total expense'), 'total_expense'),
                        'status', 'is_default']

    @classmethod
    def get_edit_fields(cls):
        return ['name', 'description']

    @property
    def total_revenue(self):
        return format_devise(self.get_total_revenue(), 5)

    def get_total_revenue(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=3, entry__costaccounting=self).aggregate(Sum('amount')))

    @property
    def total_expense(self):
        return format_devise(self.get_total_expense(), 5)

    def get_total_expense(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=4, entry__costaccounting=self).aggregate(Sum('amount')))

    def change_has_default(self):
        if self.status == 0:
            if self.is_default:
                self.is_default = False
                self.save()
            else:
                all_cost = CostAccounting.objects.all(
                )
                for cost_item in all_cost:
                    cost_item.is_default = False
                    cost_item.save()
                self.is_default = True
                self.save()

    class Meta(object):

        verbose_name = _('cost accounting')
        verbose_name_plural = _('costs accounting')
        default_permissions = []


class ChartsAccount(LucteriosModel):
    code = models.CharField(_('code'), max_length=50, db_index=True)
    name = models.CharField(_('name'), max_length=200)
    year = models.ForeignKey('FiscalYear', verbose_name=_(
        'fiscal year'), null=False, on_delete=models.CASCADE, db_index=True)
    type_of_account = models.IntegerField(verbose_name=_('type of account'),
                                          choices=((0, _('Asset')), (1, _('Liability')), (2, _('Equity')), (3, _(
                                              'Revenue')), (4, _('Expense')), (5, _('Contra-accounts'))),
                                          null=True, db_index=True)

    @classmethod
    def get_default_fields(cls):
        return ['code', 'name', (_('total of last year'), 'last_year_total'),
                (_('total current'), 'current_total'), (_('total validated'), 'current_validated')]

    @classmethod
    def get_edit_fields(cls):
        return ['code', 'name', 'type_of_account']

    @classmethod
    def get_show_fields(cls):
        return ['code', 'name', 'type_of_account']

    @classmethod
    def get_print_fields(cls):
        return ['code', 'name', (_('total of last year'), 'last_year_total'),
                (_('total current'), 'current_total'), (_('total validated'), 'current_validated'), 'entrylineaccount_set']

    def __str__(self):
        return "[%s] %s" % (self.code, self.name)

    def get_last_year_total(self):
        return get_amount_sum(self.entrylineaccount_set.filter(entry__journal__id=1).aggregate(Sum('amount')))

    def get_current_total(self):
        return get_amount_sum(self.entrylineaccount_set.all().aggregate(Sum('amount')))

    def get_current_validated(self):
        return get_amount_sum(self.entrylineaccount_set.filter(entry__close=True).aggregate(Sum('amount')))

    def credit_debit_way(self):
        if self.type_of_account in [0, 4]:
            return -1
        else:
            return 1

    @property
    def last_year_total(self):
        return format_devise(self.credit_debit_way() * self.get_last_year_total(), 2)

    @property
    def current_total(self):
        return format_devise(self.credit_debit_way() * self.get_current_total(), 2)

    @property
    def current_validated(self):
        return format_devise(self.credit_debit_way() * self.get_current_validated(), 2)

    @property
    def is_third(self):
        return match(current_system_account().get_third_mask(), self.code) is not None

    @property
    def is_cash(self):
        return match(current_system_account().get_cash_mask(), self.code) is not None

    class Meta(object):

        verbose_name = _('charts of account')
        verbose_name_plural = _('charts of accounts')
        ordering = ['year', 'code']


class Journal(LucteriosModel):
    name = models.CharField(_('name'), max_length=50, unique=True)

    def __str__(self):
        return self.name

    def can_delete(self):
        if self.id in [1, 2, 3, 4, 5]:
            return _('journal reserved!')
        else:
            return ''

    @classmethod
    def get_default_fields(cls):
        return ["name"]

    class Meta(object):

        verbose_name = _('accounting journal')
        verbose_name_plural = _('accounting journals')
        default_permissions = []


class AccountLink(LucteriosModel):

    def __str__(self):
        return self.letter

    @property
    def letter(self):
        year = self.entryaccount_set.all()[0].year
        nb_link = AccountLink.objects.filter(
            entryaccount__year=year, id__lt=self.id).count()
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = ''
        while nb_link >= 26:
            div, mod = divmod(nb_link, 26)
            res = letters[mod] + res
            nb_link = int(div) - 1
        return letters[nb_link] + res

    @classmethod
    def create_link(cls, entries):
        for entry in entries:
            entry.unlink()
        new_link = AccountLink.objects.create()
        for entry in entries:
            entry.link = new_link
            entry.save()

    class Meta(object):

        verbose_name = _('letter')
        verbose_name_plural = _('letters')
        default_permissions = []


class EntryAccount(LucteriosModel):
    year = models.ForeignKey('FiscalYear', verbose_name=_(
        'fiscal year'), null=False, on_delete=models.CASCADE)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    journal = models.ForeignKey('Journal', verbose_name=_(
        'journal'), null=False, default=0, on_delete=models.PROTECT)
    link = models.ForeignKey(
        'AccountLink', verbose_name=_('link'), null=True, on_delete=models.SET_NULL)
    date_entry = models.DateField(verbose_name=_('date entry'), null=True)
    date_value = models.DateField(
        verbose_name=_('date value'), null=False, db_index=True)
    designation = models.CharField(_('name'), max_length=200)
    costaccounting = models.ForeignKey('CostAccounting', verbose_name=_(
        'cost accounting'), null=True, on_delete=models.PROTECT)
    close = models.BooleanField(
        verbose_name=_('close'), default=False, db_index=True)

    @classmethod
    def get_default_fields(cls):
        return ['year', 'close', 'num', 'journal', 'date_entry', 'date_value', 'designation', 'costaccounting']

    @classmethod
    def get_edit_fields(cls):
        return ['journal', 'date_value', 'designation']

    @classmethod
    def get_show_fields(cls):
        return ['num', 'journal', 'date_entry', 'date_value', 'designation']

    def can_delete(self):
        if self.close:
            return _('entry of account closed!')
        else:
            return ''

    def delete(self):
        self.unlink()
        LucteriosModel.delete(self)

    def get_serial(self, entrylines=None):
        if entrylines is None:
            entrylines = self.entrylineaccount_set.all(
            )
        serial_val = ''
        for line in entrylines:
            if serial_val != '':
                serial_val += '\n'
            serial_val += line.get_serial()
        return serial_val

    def get_entrylineaccounts(self, serial_vals):
        res = QuerySet(model=EntryLineAccount)
        res._result_cache = []
        for serial_val in serial_vals.split('\n'):
            if serial_val != '':
                new_line = EntryLineAccount.get_entrylineaccount(serial_val)
                new_line.entry = self
                res._result_cache.append(
                    new_line)
        return res

    def save_entrylineaccounts(self, serial_vals):
        if not self.close:
            self.entrylineaccount_set.all().delete(
            )
            for line in self.get_entrylineaccounts(serial_vals):
                if line.id < 0:
                    line.id = None
                line.save()

    def remove_entrylineaccounts(self, serial_vals, entrylineid):
        lines = self.get_entrylineaccounts(serial_vals)
        line_idx = -1
        for idx in range(len(lines)):
            if lines[idx].id == entrylineid:
                line_idx = idx
        del lines._result_cache[line_idx]
        return self.get_serial(lines)

    def add_new_entryline(self, serial_entry, entrylineaccount, num_cpt, credit_val, debit_val, third, reference):
        if self.journal.id == 1:
            charts = ChartsAccount.objects.get(
                id=num_cpt)
            if match(current_system_account().get_revenue_mask(), charts.code) or \
                    match(current_system_account().get_expence_mask(), charts.code):
                raise LucteriosException(
                    IMPORTANT, _('This kind of entry is not allowed for this journal!'))
        if entrylineaccount != 0:
            serial_entry = self.remove_entrylineaccounts(
                serial_entry, entrylineaccount)
        if serial_entry != '':
            serial_entry += '\n'
        serial_entry += EntryLineAccount.add_serial(
            num_cpt, debit_val, credit_val, third, reference)
        return serial_entry

    def serial_control(self, serial_vals):
        total_credit = 0
        total_debit = 0
        serial = self.get_entrylineaccounts(serial_vals)
        current = self.entrylineaccount_set.all()
        no_change = len(serial) > 0
        if len(serial) == len(current):
            for idx in range(len(serial)):
                total_credit += serial[idx].get_credit()
                total_debit += serial[idx].get_debit()
                no_change = no_change and current[idx].equals(serial[idx])
        else:
            no_change = False
            for idx in range(len(serial)):
                total_credit += serial[idx].get_credit()
                total_debit += serial[idx].get_debit()
        return no_change, max(0, total_credit - total_debit), max(0, total_debit - total_credit)

    def closed(self):
        if (self.year.status != 2) and not self.close:
            self.close = True
            val = self.year.entryaccount_set.all().aggregate(
                Max('num'))
            if val['num__max'] is None:
                self.num = 1
            else:
                self.num = val['num__max'] + 1
            self.date_entry = date.today()
            self.save()

    def unlink(self):
        if (self.year.status != 2) and (self.link is not None):
            for entry in self.link.entryaccount_set.all():
                entry.link = None
                entry.save()
            self.link.delete()
            self.link = None

    def create_linked(self):
        if (self.year.status != 2) and (self.link is None):
            paym_journ = Journal.objects.get(id=4)
            paym_desig = _('payment of %s') % self.designation
            new_entry = EntryAccount.objects.create(
                year=self.year, journal=paym_journ, designation=paym_desig, date_value=date.today())
            serial_val = ''
            for line in self.entrylineaccount_set.all():
                if line.account.is_third:
                    if serial_val != '':
                        serial_val += '\n'
                    serial_val += line.create_clone_inverse()
            AccountLink.create_link([self, new_entry])
            return new_entry, serial_val

    def add_entry_line(self, amount, code, name=None, third=None):
        if abs(amount) > 0.0001:
            new_entry_line = EntryLineAccount()
            new_entry_line.entry = self
            new_entry_line.account = self.year.getorcreate_chartaccount(
                code, name)
            new_entry_line.amount = amount
            new_entry_line.third = third
            new_entry_line.save()
            return new_entry_line

    @property
    def has_third(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_third_mask()).count() > 0

    @property
    def has_customer(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_customer_mask()).count() > 0

    @property
    def has_cash(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_cash_mask()).count() > 0

    class Meta(object):

        verbose_name = _('entry of account')
        verbose_name_plural = _('entries of account')


class EntryLineAccount(LucteriosModel):

    account = models.ForeignKey('ChartsAccount', verbose_name=_(
        'account'), null=False, on_delete=models.PROTECT)
    entry = models.ForeignKey(
        'EntryAccount', verbose_name=_('entry'), null=False, on_delete=models.CASCADE)
    amount = models.FloatField(_('amount'), db_index=True)
    reference = models.CharField(_('reference'), max_length=100, null=True)
    third = models.ForeignKey('Third', verbose_name=_(
        'third'), null=True, on_delete=models.PROTECT, db_index=True)

    @classmethod
    def get_default_fields(cls):
        return [(_('account'), 'entry_account'), (_('debit'), 'debit'), (_('credit'), 'credit'), 'reference']

    @classmethod
    def get_other_fields(cls):
        return ['entry.num', 'entry.date_entry', 'entry.date_value', (_('account'), 'entry_account'),
                'entry.designation', (_('debit'), 'debit'), (_('credit'), 'credit'), 'entry.link', 'entry.costaccounting']

    @classmethod
    def get_edit_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation',
                ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @classmethod
    def get_show_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation',
                ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @classmethod
    def get_print_fields(cls):
        return ['entry', (_('account'), 'entry_account'), (_('debit'), 'debit'), (_('credit'), 'credit'), 'reference', 'third', 'entry.costaccounting']

    @property
    def entry_account(self):
        if self.third is None:
            return six.text_type(self.account)
        else:
            return "[%s %s]" % (self.account.code, six.text_type(self.third))

    def get_debit(self):
        try:
            return max((0, -1 * self.account.credit_debit_way() * self.amount))
        except ObjectDoesNotExist:
            return 0.0

    @property
    def debit(self):
        return format_devise(self.get_debit(), 0)

    def get_credit(self):
        try:
            return max((0, self.account.credit_debit_way() * self.amount))
        except ObjectDoesNotExist:
            return 0.0

    @property
    def credit(self):
        return format_devise(self.get_credit(), 0)

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = -1 * debit_val * self.account.credit_debit_way()
        elif credit_val > 0:
            self.amount = credit_val * self.account.credit_debit_way()
        else:
            self.amount = 0

    def equals(self, other):
        res = self.id == other.id
        res = res and (self.account.id == other.account.id)
        res = res and (self.amount == other.amount)
        res = res and (self.reference == other.reference)
        if self.third is None:
            res = res and (other.third is None)
        else:
            res = res and (
                self.third.id == other.third.id)
        return res

    def get_serial(self):
        if self.third is None:
            third_id = 0
        else:
            third_id = self.third.id
        if self.reference is None:
            reference = 'None'
        else:
            reference = self.reference
        return "%d|%d|%d|%f|%s|" % (self.id, self.account.id, third_id, self.amount, reference)

    @classmethod
    def add_serial(cls, num_cpt, debit_val, credit_val, thirdid=0, reference=None):
        import time
        new_entry_line = cls()
        new_entry_line.id = -1 * \
            int(time.time() *
                60)
        new_entry_line.account = ChartsAccount.objects.get(
            id=num_cpt)
        if thirdid == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(
                id=thirdid)
        new_entry_line.set_montant(debit_val, credit_val)
        if reference == "None":
            new_entry_line.reference = None
        else:
            new_entry_line.reference = reference
        return new_entry_line.get_serial()

    @classmethod
    def get_entrylineaccount(cls, serial_val):
        serial_vals = serial_val.split('|')
        new_entry_line = cls()
        new_entry_line.id = int(
            serial_vals[0])
        new_entry_line.account = ChartsAccount.objects.get(
            id=int(serial_vals[1]))
        if int(serial_vals[2]) == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(
                id=int(serial_vals[2]))
        new_entry_line.amount = float(serial_vals[3])
        new_entry_line.reference = "|".join(serial_vals[4:-1])
        if new_entry_line.reference == "None":
            new_entry_line.reference = None
        return new_entry_line

    def create_clone_inverse(self):
        import time
        new_entry_line = EntryLineAccount()
        new_entry_line.id = -1 * \
            int(time.time() *
                60)
        new_entry_line.account = self.account
        if self.third:
            new_entry_line.third = self.third
        else:
            new_entry_line.third = None
        new_entry_line.amount = -1 * self.amount
        new_entry_line.reference = self.reference
        return new_entry_line.get_serial()

    @property
    def has_account(self):
        try:
            return self.account is not None
        except ObjectDoesNotExist:
            return False

    class Meta(object):

        verbose_name = _('entry line of account')
        verbose_name_plural = _('entry lines of account')
        default_permissions = []


class ModelEntry(LucteriosModel):

    journal = models.ForeignKey('Journal', verbose_name=_(
        'journal'), null=False, default=0, on_delete=models.PROTECT)
    designation = models.CharField(_('name'), max_length=200)

    def __str__(self):
        return "[%s] %s (%s)" % (self.journal, self.designation, self.total)

    @classmethod
    def get_default_fields(cls):
        return ['journal', 'designation', (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ['journal', 'designation']

    @classmethod
    def get_show_fields(cls):
        return ['journal', 'designation', ((_('total'), 'total'),), 'modellineentry_set']

    def get_total(self):
        try:
            value = 0.0
            for line in self.modellineentry_set.all():
                value += line.get_credit()
            return value
        except LucteriosException:
            return 0.0

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def get_serial_entry(self, factor):
        serial_val = ''
        num = 0
        for line in self.modellineentry_set.all():
            if serial_val != '':
                serial_val += '\n'
            serial_val += line.get_serial(factor, num)
            num += 1
        return serial_val

    class Meta(object):

        verbose_name = _('Model of entry')
        verbose_name_plural = _('Models of entry')
        default_permissions = []


class ModelLineEntry(LucteriosModel):

    model = models.ForeignKey('ModelEntry', verbose_name=_(
        'model'), null=False, default=0, on_delete=models.CASCADE)
    code = models.CharField(_('code'), max_length=50)
    third = models.ForeignKey(
        'Third', verbose_name=_('third'), null=True, on_delete=models.PROTECT)
    amount = models.FloatField(_('amount'), default=0)

    @classmethod
    def get_default_fields(cls):
        return ['code', 'third', (_('debit'), 'debit'), (_('credit'), 'credit')]

    @classmethod
    def get_edit_fields(cls):
        return ['code', 'third']

    def credit_debit_way(self):
        chart_account = current_system_account().new_charts_account(self.code)
        if chart_account[0] == '':
            raise LucteriosException(IMPORTANT, _("Invalid code"))
        if chart_account[1] in [0, 4]:
            return -1
        else:
            return 1

    def get_debit(self):
        try:
            return max((0, -1 * self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    @property
    def debit(self):
        return format_devise(self.get_debit(), 0)

    def get_credit(self):
        try:
            return max((0, self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    @property
    def credit(self):
        return format_devise(self.get_credit(), 0)

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = -1 * debit_val * self.credit_debit_way()
        elif credit_val > 0:
            self.amount = credit_val * self.credit_debit_way()
        else:
            self.amount = 0

    def get_serial(self, factor, num):
        import time
        try:
            new_entry_line = EntryLineAccount()
            new_entry_line.id = -1 * \
                int(time.time() * 60) + \
                num
            new_entry_line.account = ChartsAccount.objects.get(
                code=self.code)
            new_entry_line.third = self.third
            new_entry_line.amount = currency_round(self.amount * factor)
            new_entry_line.reference = None
            return new_entry_line.get_serial()
        except ObjectDoesNotExist:
            raise LucteriosException(
                IMPORTANT, _('Account code "%s" unknown for this fiscal year!') % self.code)

    class Meta(object):

        verbose_name = _('Model line')
        verbose_name_plural = _('Model lines')
        default_permissions = []
