from .constants import *

from .Field import Field
from .Bean import Bean

Field(name='uid', type='int', increment=(0, 1))(Bean)
