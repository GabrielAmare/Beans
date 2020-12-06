from .constants import *

from .Field import Field
from .FieldList import FieldList
from .Bean import Bean

Field(name='uid', type='int', increment=(0, 1))(Bean)
