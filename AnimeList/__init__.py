''' Methods to get the AnimeList datasets '''
__all__ = [
	'dataset',
	'filter',
	'clean',
	'plotting',
]
from enum import StrEnum as _StrEnum
class DatasetDescriptors(_StrEnum):
	ColumnName='DATASET_DESCRIPTOR'
	Filtered = 'Filtered'
	Raw = 'Raw'
	Cleaned = 'Cleaned'