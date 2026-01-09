import string

class BaseField:
  dataType = object

  def __init__(self, value=None):
    self.value = object
    self.set(value)

  def default(self):
    if self.dataType == int:
      return 0
    elif self.dataType == float:
      return 0.0
    elif self.dataType == str:
      return ''
    else:
      return None

  def validate(self, value):
    _value = value
    if value is None:
      _value = self.default()

    if not isinstance(_value, self.dataType) or _value is None:
      _ownDataTypeStr = str(self.dataType)
      _theirDataTypeValueStr = str(type(_value))
      print(f'Expected {_ownDataTypeStr}, got {_theirDataTypeValueStr}')
      raise TypeError()

    return _value

  def set(self, value):
    self.value = self.validate(value)

  def get(self):
    return self.value

class IntegerField(BaseField):
  dataType = int

class FloatField(BaseField):
  dataType = float

class TextField(BaseField):
  dataType = str

class IntegerRangeField(IntegerField):
  def __init__(self, value=None, minValue=None, maxValue=None):
    super().__init__(value)
    self.min = IntegerField()
    self.max = IntegerField()

    self.min.set(minValue if minValue else self.min.default())
    self.max.set(maxValue if maxValue else self.max.default())

class QuantityField(IntegerField):
  def __init__(self, value=None, maxValue=None):
    super().__init__(value)

    self.max = IntegerField(maxValue)
    self.setMax(maxValue if maxValue else self.max.default())

  def changeValue(self, amount=1):
    self.value = self.value + amount

  def setMax(self, maxValue):
    self.max.validate(maxValue)
    self.max.set(maxValue)

  def get(self):
    return{
      'value': self.value,
      'max': self.max.get()
    }