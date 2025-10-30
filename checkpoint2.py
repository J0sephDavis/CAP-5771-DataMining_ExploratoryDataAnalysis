from helpers.context import load_find_env, get_env_val_safe,EnvFields
from pathlib import Path
import pandas as pd
from typing import Optional, List, Final
from enum import StrEnum
loaded, _ = load_find_env()
if not loaded:
	print('DOTENV could not be loaded. STOP.')
	exit()

''' TODO
1. [ ] Fetch dataset
2. [ ] Filter and Clean
3. [ ] Boxplots for each feature
4. [ ] Measure covariance of features
5. [ ] Visualize covariant features
6. [ ] UMAP, TSNE of data
'''