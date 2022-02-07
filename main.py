import locale

# import i18n

from polidoro_argument import Command, PolidoroArgumentParser
from polidoro_sqlite_utils import SQLiteTable
import models



@Command
def create(model, *attrs, **kw_attrs):
    entity = SQLiteTable.get_model(model).create(*attrs, **kw_attrs).save()
    entity.print()


# @Command
# def list(model, *, show_id=False, **kwargs):
#     if show_id is None:
#         show_id = True
#     get_model(model).print_as_table(show_id=show_id, **kwargs)


# @Command
# def delete(model, pk):
#     model = get_model(model)
#     model.delete(pk)
#     model.print_as_table()


# @Command
# def edit(model, set=None, **kwargs):
#     model = get_model(model)
#     model_attributes = model.get_attributes()
#     for entity in model.find(**kwargs):
#         print(entity)
#         if input('Edit this[Y/n]: ').lower() in ['y', '']:
#             if set:
#                 for attr_value in set.split(';'):
#                     attr, value = attr_value.split('=')
#                     attr_value = model_attributes[attr]
#                     setattr(entity, attr, attr_value.parse(value))
#             else:
#                 for attr, attr_type in model_attributes.items():
#                     value = getattr(entity, attr, None)
#                     value = input(f'{attr} ({value}): ')
#                     if value:
#                         setattr(entity, attr, attr_type.parse(value))
#             entity.save()


# @Command
# def balance(*args):
#     if 'recalculate' in args:
#         Balance.delete_where()
#     date = datetime.datetime.now()
#
#     if 'last' in args:
#         som = datetime.date(date.year, date.month, 1)
#         date = som - datetime.timedelta(days=1)
#     Balance.show(date)


# @Command
# def parse(file_name, *args, force=False, remove_file=False):
#     if force is None:
#         force = True
#
#     if not args:
#         try:
#             date = dateutil.parser.parse(file_name)
#         except dateutil.parser.ParserError:
#             search = re.search(r'(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<account>\w+)', file_name)
#             if search and search.groupdict().get('account'):
#                 parse(file_name, search.groupdict()['account'].lower(), force=force, remove_file=remove_file)
#                 exit()
#             raise ValueError('parser missing')
#         year = date.year
#         month = date.month
#         for account in Account.all():
#             for extension in ['csv', 'txt']:
#                 file_name = f'{year}-{month:02}-{account.alias}.{extension}'
#                 if os.path.exists(file_name):
#                     parse(file_name, account.alias.lower(), force=force, remove_file=True)
#         balance('last')
#     if len(args) > 2:
#         files = [f for f in [file_name] + type_list(args) if os.path.isfile(file_name)]
#         file_count = 0
#         total_files = len(files)
#         for file_name in files:
#             file_count += 1
#             search = re.search(r'(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<account>\w+)', file_name)
#             if search:
#                 groupdict = search.groupdict()
#                 parser = groupdict['account'].lower()
#                 print(f'[{file_count}/{total_files}] Parsing {file_name}...')
#                 parse(file_name, parser, force=force, remove_file=True)
#                 print()
#             else:
#                 print(f'Ignoring {file_name}')
#         exit()
#
#     parser = Parser.parsers[args[0]]
#     info = parser.parse(file_name)
#     total = len(info)
#     count = 0
#     for t in info:
#         count += 1
#         reason_rule = ReasonRule.find(reason=t['reason'])
#         if reason_rule:
#             reason_rule = reason_rule[0]
#             for attr, value in reason_rule.__dict__.items():
#                 if attr == 'id':
#                     continue
#                 if value == 'parser.account':
#                     value = parser.account
#                 t.setdefault(attr, value)
#
#         transaction = Transaction.create(ask_for_missing_attributes=False, **t)
#         print(f'[{count}/{total}]', Transaction(**t))
#         if Transaction.find(transaction):
#             print('Already exists!')
#         else:
#             if True or input('Confirm [Y/n]: ').lower() in ['y', '']:
#                 if transaction.category == 'ending_balance':
#                     Transaction.delete(category=transaction.category, origin=transaction.origin.id)
#
#                 ask_for_missing_attributes = not force and not reason_rule or not t['date']
#                 transaction = Transaction.create(ask_for_missing_attributes=ask_for_missing_attributes, **t)
#                 existent_transaction = Transaction.find(transaction, ignores=['reason'])
#                 if existent_transaction and \
#                         (force or input(f'Already exists {existent_transaction}, continue anyway [y/N]: ').lower() in ['n', '']):
#                     continue
#
#                 transaction.save()
#                 if transaction.category and not reason_rule and \
#                         (force or input('Create ReasonRule [Y/n]: ').lower() in ['y', '']):
#                     reason_rule_dict = copy.deepcopy(transaction.__dict__)
#                     del reason_rule_dict['id']
#                     if not transaction.origin:
#                         del reason_rule_dict['destination']
#                     if not transaction.destination:
#                         del reason_rule_dict['origin']
#                     ReasonRule.create(ask_for_missing_attributes=False, **reason_rule_dict).save()
#
#             elif input('Ignore or Edit [I/e]: ').lower() not in ['i', '']:
#                 print('EDIT')
#
#     if remove_file or input(f'Remove {file_name} [Y/n]: ') in ['y', '']:
#         os.remove(file_name)




if __name__ == '__main__':
    try:
        PolidoroArgumentParser().parse_args()
    except KeyboardInterrupt:
        pass
