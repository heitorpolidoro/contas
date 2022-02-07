from datetime import datetime, time, date
import dateutil

NO_DEFAULT = 'NO_DEFAULT'


class BaseField:
    def __init__(self, *, default=NO_DEFAULT, null=False, **_):
        self.default = default
        self.null = null

    def parse(self, value):
        if value is None:
            return None

        if isinstance(value, self.type):
            return value

        parser = getattr(self, '_field_parse', self.type)
        return parser(value)

    def ask(self, attr):  # pragma: no cover
        try:
            from polidoro_question.question import Question
            value = Question(question=attr, type=self.parse).ask()
        except ImportError:
            value = self.parse(input(f'{attr}: '))
        setattr(self, attr, value)


class IntegerField(BaseField):
    type = int


class FloatField(BaseField):
    type = float

    def __init__(self, *, precision=2, **kwargs):
        super(FloatField, self).__init__(**kwargs)
        self.precision = precision

    def _field_parse(self, value):
        return round(float(value), self.precision)


class TextField(BaseField):
    type = str


class DatetimeField(BaseField):
    type = datetime

    def __init__(self, *, format=None, **kwargs):
        super(DatetimeField, self).__init__(**kwargs)
        for key in self.__dict__:
            kwargs.pop(key, None)
        self.format = format
        self.kwargs = kwargs

    def _field_parse(self, value):
        if self.format:
            return datetime.strptime(value, self.format)
        return dateutil.parser.parse(value, **self.kwargs)


class TimeField(DatetimeField):
    type = time

    def __init__(self, *, format='%H:%M', **kwargs):
        super(TimeField, self).__init__(format=format, **kwargs)

    def _field_parse(self, value):
        return super(TimeField, self)._field_parse(value).time()


class DateField(DatetimeField):
    type = date

    def _field_parse(self, value):
        return super(DateField, self)._field_parse(value).date()


class ForeignKey(BaseField):
    def __init__(self, model, **kwargs):
        super(ForeignKey, self).__init__(**kwargs)
        self.type = model

    def _field_parse(self, value):
        return self.type.get(value)
