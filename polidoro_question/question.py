
try:
    import i18n
    import locale
    _ = i18n.t
    lc, encoding = locale.getdefaultlocale()

    i18n.set('locale', lc)
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append('locale')
except ImportError:
    _ = str


class Question:
    def __init__(self, **kwargs):
        self.question = _(kwargs.get('question')).capitalize()
        self.type = kwargs.get('type', str)

    def ask(self):
        resp = input(f'{self.question}: ')
        return self.type(resp)
