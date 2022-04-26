import calendar
import csv
import locale
import re
from collections import defaultdict
from datetime import datetime, timedelta, date


class Parser:
    parsers = {}

    def __init__(self, *, date_col=None, reason_col=None, value_col=None, account=None, locale=None,
                 encoding='utf-8', reason_regexes=None, date_format=None, discard_lines=0, line_regex=None,
                 pre_interceptors=None, post_interceptors=None):
        if pre_interceptors is None:
            pre_interceptors = []
        if post_interceptors is None:
            post_interceptors = []
        if reason_regexes is None:
            reason_regexes = []
        self.date_col = date_col
        self.reason_col = reason_col
        self.value_col = value_col
        self.account = account
        self.encoding = encoding
        self.reason_regexes = reason_regexes
        self.reason = None
        self.date_format = date_format
        self.discard_lines = discard_lines
        self.line_regex = line_regex
        self.locale = locale
        self.pre_interceptors = pre_interceptors
        self.post_interceptors = post_interceptors

    def parse(self, file_name, account):
        self.account = account
        if self.locale:
            locale.setlocale(locale.LC_ALL, self.locale)
        with open(file_name, newline='', encoding=self.encoding) as file:
            return self._parse(file)

    def _parse(self, file):
        raise NotImplementedError

    def extract_line_info(self, line):
        try:
            if isinstance(line, list):
                line_info = dict(
                    date=line[self.date_col],
                    regexed_reason=line[self.reason_col],
                    value=line[self.value_col]
                )
            elif isinstance(line, dict):
                line_info = line
                line_info.setdefault('regexed_reason', line['reason'])

            for interceptor in self.pre_interceptors:
                line_info = interceptor(self, line_info)

            line_info['regexed_reason'] = line_info['regexed_reason'].strip()
            line_info['reason'] = line_info['regexed_reason']
            if self.locale:
                line_info['value'] = locale.atof(line_info['value'])
            else:
                line_info['value'] = float(line_info['value'])

            line_info['regexed_reason'] = self.regex_reason(line_info['regexed_reason'])
            line_info['date'] = self.format_date(line_info['date'])

            if line_info['value'] < 0:
                line_info['origin'] = self.account
            elif line_info['value'] > 0:
                line_info['destination'] = self.account

            for interceptor in self.post_interceptors:
                line_info = interceptor(self, line_info)

            line_info['value'] = abs(line_info['value'])
            return line_info
        except ValueError:
            print(self.__dict__)
            raise

    def regex_reason(self, reason):
        for regex in self.reason_regexes:
            reason = re.sub(regex, '', reason)
        return reason

    def format_date(self, date):
        if date and self.date_format:
            date = datetime.strptime(date, self.date_format).date()
        return date

    def extract_info(self, lines, discard_lines=None):
        info = []
        if discard_lines is None:
            discard_lines = self.discard_lines
        for line in lines:
            if discard_lines:
                discard_lines -= 1
                continue

            info.append(self.extract_line_info(line))
        return info


class CSVParser(Parser):
    def _parse(self, csvfile):
        return self.extract_info(csv.reader(csvfile))


class TXTParser(Parser):
    def _parse(self, txtfile):
        lines = []
        for line in txtfile.readlines():
            info = re.search(self.line_regex, line)
            if info:
                lines.append(info.groupdict())
        return self.extract_info(lines)


class FundoBBParser(Parser):
    def _parse(self, file):
        info = []
        rendimentos = {}

        for line in file.readlines():
            balance_info = re.search(
                r'(?P<date>\d\d/\d\d/\d\d\d\d) (?P<reason>SALDO ANTERIOR|SALDO ATUAL) *(?P<value>[\d\.,]+)', line)
            if balance_info:
                info.append(self.extract_line_info(balance_info.groupdict()))
                if 'SALDO ATUAL' in line:
                    rendimentos['date'] = balance_info.groupdict()['date']
            else:
                rendimento_info = re.search(r'(?P<reason>RENDIMENTO LÍQUIDO) *(?P<value>[\d\.,-]+)', line)
                if rendimento_info:
                    rendimentos.update(rendimento_info.groupdict())
                    info.append(self.extract_line_info(rendimentos))

        return info


class BradescoParser(Parser):
    def _parse(self, csvfile):
        lines = []
        fundo = []
        transactions_aux = defaultdict(float)
        for line in csv.reader(csvfile, delimiter=';'):
            if len(line) in [6, 7] and line[0] not in ['Data', '']:
                value = line[3] or line[4] or line[5]
                lines.append(line[:2] + [value])
                if line[1] in [' Apl.invest Fac', ' Resgate Inv Fac']:
                    transactions_aux[line[0]] += locale.atof(value)
            elif len(line) == 4 and line[1] == ' Saldo Invest Fácil':
                fundo.append(line)

        transactions = self.extract_info(lines)

        transactions_to_create = []
        for idx, f in enumerate(fundo):
            if idx != 0:
                diff = round(locale.atof(f[2]) - locale.atof(fundo[idx-1][2]) + transactions_aux.get(f[0], 0), 2)
                if diff:
                    transactions_to_create.append([f[0], 'Rendimento', str(diff)])

        old_locale = self.locale
        self.locale = None
        from models import Account

        self.account = Account.filter(alias='FundoBRA').first()
        transactions.extend(self.extract_info(transactions_to_create, discard_lines=0))
        self.locale = old_locale
        self.account = 'BRA'
        return transactions


def bb_saldo_anterior_interceptor(_self, info):
    if info['reason'].lower() == 'saldo anterior':
        while info['date'].day != 1:
            info['date'] += timedelta(days=1)

    return info


def change_value_sign(_self, info):
    value = info['value']
    if value[0] == '-':
        value = value[1:]
    else:
        value = f'-{value}'
    info['value'] = value
    return info


def fix_parc_date(_self, info):
    if 'PARC' in info['reason']:
        parc = int(re.search(r'.*[ -]PARC (?P<parc>\d\d)/\d\d', info['reason']).groupdict()['parc'])
        info_date = info['date']
        month = info_date.month
        year = info_date.year
        while parc != 1:
            month += 1
            if month == 13:
                month = 1
                year += 1
            parc -= 1
        try:
            info['date'] = date(year, month, info_date.day)
        except ValueError as err:
            if str(err) == 'day is out of range for month':
                info['date'] = date(year, month, calendar.monthrange(year, month)[1])
    return info


Parser.parsers['bb'] = CSVParser(
    date_col=0, reason_col=2, value_col=5, account='BB', encoding='latin1',
    date_format='%d/%m/%Y', discard_lines=1,
    reason_regexes=[
        r' \d\d/\d\d \d\d:\d\d',
        r' - Cobrança referente \d\d/\d\d/\d\d\d\d',
        r' - \d\d/\d\d .*-X'
    ],
    post_interceptors=[bb_saldo_anterior_interceptor]
)

Parser.parsers['bra'] = BradescoParser(
    date_col=0, reason_col=1, value_col=2, account='BRA', encoding='latin1',
    date_format='%d/%m/%y', discard_lines=1, locale='pt_BR.UTF-8',
    post_interceptors=[bb_saldo_anterior_interceptor]
)

Parser.parsers['fundobb'] = FundoBBParser(
    encoding='latin1', account='FundoBB', locale='pt_BR.UTF-8', date_format='%d/%m/%Y',
    post_interceptors=[bb_saldo_anterior_interceptor]
)

Parser.parsers['visabb'] = TXTParser(
    encoding='latin1', account='VisaBB', locale='pt_BR.UTF-8', date_format='%d.%m.%Y',
    line_regex=r'(?P<date>\d\d.\d\d.\d\d\d\d)(?P<reason>.*?) (?P<value>[-\d\.]+,\d+).*0,00',
    pre_interceptors=[change_value_sign], post_interceptors=[fix_parc_date], reason_regexes=[r'PARC \d\d/\d\d']

)
