from helpers.files import (
    DatasetBase
)
from AnimeList.filter import (
    AnimeListFiltered, AnimeListFilterOut, filter_dataset
)
from AnimeList.clean import (
    AnimeListClean, AnimeListCleanOut, clean_dataset
)
from AnimeList.dataset import (
    AnimeListRaw
)
from typing import (
    Tuple, Final, List
)
import pandas as pd
from AnimeList.plotting import (
    compare_by_label, comparison_barchart_by_type
)
from pathlib import Path
from helpers.context import (
    EnvFields,
    get_env_val_safe,
    load_find_env
)
load_find_env()
folders:List[EnvFields] = [
    EnvFields.DIR_FIGURES_ANIME,
    EnvFields.DIR_FIGURES_ANIME_CLEAN,
    EnvFields.DIR_FIGURES_ANIME_COMPARISON,
    EnvFields.DIR_FIGURES_ANIME_FILTER,
    EnvFields.DIR_GENERATED_DATASETS,
]
for key in folders:
    Path(get_env_val_safe(key)).mkdir(exist_ok=True, parents=True, mode=0o777)

dataset = AnimeListRaw()
filtered, filter_removed = filter_dataset(dataset)
clean, clean_removed = clean_dataset(filtered)
column_label:Final[str] = 'COMARE_LABEL'
def __label_copy(db:DatasetBase, label:str)->pd.DataFrame:
    frame = db.get_frame().copy()
    frame[column_label] = label
    return frame

def plot_removed(
        result:DatasetBase, removed:DatasetBase,
        result_label:str, removed_label:str,
        folder:Path
        )->None:
    ''' Compares the two datasets by creating graphs '''
    res = __label_copy(result,result_label)
    rem = __label_copy(removed,removed_label)
    compFrame = pd.concat([res,rem],axis=0)
    if not folder.exists():
        folder.mkdir(mode=0o777, parents=True, exist_ok=True)
    compare_by_label(compFrame, column_label, str(folder))
    F01, F01_ax = comparison_barchart_by_type(res, rem)
    F01.suptitle('Clean Results')
    F01.savefig(f'{folder}/F01.tiff')
    return

plot_removed(
    result=filtered,removed=filter_removed,
    result_label='Filtered', removed_label='Removed',
    folder=Path(get_env_val_safe(EnvFields.DIR_FIGURES_ANIME_FILTER))
)
plot_removed(
    result=filtered,removed=filter_removed,
    result_label='Cleaned', removed_label='Removed',
    folder=Path(get_env_val_safe(EnvFields.DIR_FIGURES_ANIME_CLEAN))
)