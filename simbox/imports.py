from __future__ import annotations

from typing import Union,Optional,TypeVar,Callable,Any

from pydrake.common.all import *
from pydrake.systems.all import *
from pydrake.solvers import *

import numpy as np
import pydot,matplotlib
from matplotlib import animation
import matplotlib.pyplot as plt
from IPython.display import SVG, display, HTML