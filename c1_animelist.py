from helpers.files import DatasetBase
from AnimeList.filter import (
    AnimeListFiltered, AnimeListFilterOut, filter_dataset
)
from AnimeList.clean import (
    AnimeListClean, AnimeListCleanOut, clean_dataset
)
from AnimeList.dataset import AnimeListRaw
from typing import List
import pandas as pd
from AnimeList.plotting import (
    compare_by_label, comparison_barchart_by_type
)
from AnimeList import DatasetDescriptors
from pathlib import Path
from helpers.context import (
    EnvFields,
    get_env_val_safe,
)
def __label_copy(db:DatasetBase, label:str, descriptor_col:str)->pd.DataFrame:
    frame = db.get_frame().copy()
    frame[descriptor_col] = label
    return frame

def plot_removed(
        result:DatasetBase,
        removed:DatasetBase,
        result_label:str,
        removed_label:str,
        folder:Path,
        descriptor_col:str
        )->None:
    ''' Compares the two datasets by creating graphs '''
    res = __label_copy(result,result_label, descriptor_col)
    rem = __label_copy(removed,removed_label, descriptor_col)
    compFrame = pd.concat([res,rem],axis=0)
    if not folder.exists():
        folder.mkdir(mode=0o777, parents=True, exist_ok=True)
    compare_by_label(compFrame, descriptor_col, str(folder))
    F01, F01_ax = comparison_barchart_by_type(res, rem)
    F01.suptitle('Clean Results')
    F01.savefig(f'{folder}/F01.tiff')
    return

def plot_comparsion(
            raw:AnimeListRaw,
            filtered:AnimeListFiltered,
            clean:AnimeListClean,
            descriptor_col:str
        )->None:
    ''' Compare all of the datasets. '''
    R = __label_copy(raw,DatasetDescriptors.Raw, descriptor_col)
    F = __label_copy(filtered,DatasetDescriptors.Filtered, descriptor_col)
    C = __label_copy(clean, DatasetDescriptors.Cleaned, descriptor_col)
    comp_frame = pd.concat([R,F,C],axis=0)
    compare_by_label(
        comp_frame,
        descriptor_col,
        get_env_val_safe(EnvFields.DIR_FIGURES_ANIME_COMPARISON)
    )
    return

def run():
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
    descriptor_col:str = DatasetDescriptors.ColumnName
    plot_removed(
        result=filtered,removed=filter_removed,
        result_label=DatasetDescriptors.Filtered, removed_label='Removed',
        folder=Path(get_env_val_safe(EnvFields.DIR_FIGURES_ANIME_FILTER)),
        descriptor_col=descriptor_col
    )
    plot_removed(
        result=filtered,removed=filter_removed,
        result_label=DatasetDescriptors.Cleaned, removed_label='Removed',
        folder=Path(get_env_val_safe(EnvFields.DIR_FIGURES_ANIME_CLEAN)),
        descriptor_col=descriptor_col
    )
    plot_comparsion(
        raw=dataset,
        filtered=filtered,
        clean=clean,
        descriptor_col=descriptor_col
    )