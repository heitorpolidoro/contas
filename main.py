import calendar
import datetime

import time
from functools import lru_cache

from polidoro_table import Table

try:
    import i18n
    import locale


    @lru_cache
    def _(text):
        return i18n.t(text)


    lc, encoding = locale.getdefaultlocale()

    i18n.set('locale', lc)
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append('locale')
except ImportError:
    _ = str
    i18n = None
    locale = None
import os

import dateutil.parser
import re
from polidoro_argument.command import Command
from polidoro_model.base import BaseType

from parsers import Parser
from polidoro_question.question import Question

os.environ['DB_URL'] = 'sqlite:///contas.db'

from polidoro_argument import PolidoroArgumentParser
import polidoro_model.commands
from models import *

BaseType.__print_as_table__ = True
# BaseType.__translate_values__ = True


def get_previous_month(date):
    som = datetime.date(date.year, date.month, 1)
    return som - datetime.timedelta(days=1)


@Command
def balance(*args):
    if 'recalculate' in args:
        Balance.delete()

    last_12_months = get_last_months(12)

    t = Table('Últimos 12 saldos')
    accounts = [a for a in Account.all() if a.id != 1]
    accounts_name = [a.alias for a in accounts]
    t.add_columns(['Mês/Ano'] + accounts_name + ['Entrada', 'Saída', 'Saldo', 'Total'])
    locale.setlocale(locale.LC_ALL, '')
    for date in reversed(last_12_months):
        total = Balance.get_total_balance(date)
        accounts_total = [Balance.find_or_create(account=a, month=date.month, year=date.year).total for a in accounts]
        t.add_row([
            f'{date.month}/{date.year}',
            *accounts_total,
            f'{total.total_in:n}',
            f'{total.total_out:n}',
            f'{total.balance:n}',
            f'{total.total:n}',
        ])
    t.print()


def get_last_months(months):
    date = datetime.datetime.now()

    last_months = []
    for _ in range(months):
        last_months.append(date)
        date = get_previous_month(date)
    return last_months


@Command
def categories():
    last_12_months = get_last_months(12)
    for date in last_12_months:
        year = date.year
        month = date.month
        som = datetime.date(year, month, 1)
        eom = datetime.date(year, month, calendar.monthrange(year, month)[1])
        transactions = Transaction.filter(date=(som, eom)).group_by('category_id')
        for t in transactions:
            print(t)



def find_category(reason):
    cats = []
    for cat in Category.all():
        if cat.regex:
            if re.match(cat.regex, reason) or \
                    '_balance' not in cat.category and re.match(cat.regex, reason, re.IGNORECASE):
                cats.append(cat)

    return cats


@Command
def parse(file_name, *, force=False, remove_file=False):
    if force is None:
        force = True

    files_parsers = []
    try:
        # parse all files starting with 'date'
        date = dateutil.parser.parse(file_name)
        year = date.year
        month = date.month
        for account in Account.all():
            for extension in ['csv', 'txt']:
                file_name = f'{year}-{month:02}-{account.alias}.{extension}'
                if os.path.exists(file_name):
                    files_parsers.append((file_name, account.alias.lower()))
    except dateutil.parser.ParserError:
        # get account from file name
        search = re.search(r'(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<account>\w+)', file_name)
        if search and search.groupdict().get('account'):
            files_parsers.append((file_name, search.groupdict()['account'].lower()))
        else:
            raise ValueError('parser missing')

    balances_to_delete = set()
    for parse_info in files_parsers:
        file_name, parser_name = parse_info
        print(f'----------------- Parsing {file_name} -----------------')
        parser = Parser.parsers[parser_name]
        account = list(Account.filter(alias=parser.account))
        if account:
            account = account[0]
        else:
            if Question(_('Account with alias "') + parser.account + _('" not found. Create'),
                        type=bool, default=True).ask():
                account = Account.create(alias=parser.account)
                account.save()
        info = parser.parse(file_name, account)
        total = len(info)
        count = 0

        for t in info:
            count += 1
            regexed_reason = t.pop('regexed_reason')
            temp_t = Transaction.create(ask_for_none_values=False, **t)
            print(f'[{count}/{total}] {temp_t}')
            t_filter = {k: v for k, v in t.items() if v is not None}
            t_filter.pop('reason')
            if Transaction.filter(**t_filter).all() \
                    and (force or not Question('Already exist a transaction like this, continue', type=bool).ask()):
                continue
            cats = find_category(regexed_reason)
            for cat in cats:
                if cat and (not cat.ask_for_confirmation or cat.ask_for_confirmation
                            and (force or Question(_('Use "') + str(cat) + _('" as category'), type=bool).ask())):
                    t['category'] = cat
                    t['origin'] = t.get('origin', cat.fixed_origin)
                    t['destination'] = t.get('destination', cat.fixed_destination)
                    break

            saved_t = Transaction.create(**t).save()
            balances_to_delete.add((saved_t.date.year, saved_t.date.month))

        if remove_file or Question(_('Remove') + f' {file_name}', type=bool).ask():
            os.remove(file_name)

    if balances_to_delete:
        delete_year, delete_month = min(balances_to_delete)
        date = datetime.date(delete_year, delete_month, 1)
        today = datetime.datetime.now().date()
        while date < today:
            print(date)
            input('ENTER')
            Balance.delete(month=delete_month, year=delete_year)
            delete_month += 1
            if delete_month == 13:
                delete_month = 1
                delete_year += 1
            date = datetime.date(delete_year, delete_month, 1)


if __name__ == '__main__':
    try:
        default_categories = ['opening_balance', 'ending_balance', 'transfer']
        for category in default_categories:
            if not Category.filter(category=category).count():
                Category.create(category=category, ask_for_none_values=False).save()
        PolidoroArgumentParser().parse_args()
    except KeyboardInterrupt:
        pass
