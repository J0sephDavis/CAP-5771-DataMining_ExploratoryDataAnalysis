import pandas as _pd
from helpers.exceptions import (
	DatasetNotFound as _DatasetNotFound,
)

from .protocols import (
	DatasetSavable as _DatasetSavable,
	DatasetLoadable as _DatasetLoadable,
)

class DatasetSaveCSV(_DatasetSavable):
	def save(self, **kwargs)->None:
		''' Uses frame.to_csv(file,**kwargs) to save the csv. '''
		self.get_frame().to_csv(self.file, **kwargs)

class DatasetLoadCSV(_DatasetLoadable):
	def load(self, **kwargs)->None:
		''' Calls read_csv or raises DatasetNotFound if the file does not exist. '''
		if not self.file.exists():
			raise _DatasetNotFound('Could not find the dataset.')
		self.frame = _pd.read_csv(self.file, **kwargs)

class DatasetCSV(DatasetSaveCSV, _DatasetLoadable):
	def __init__(self) -> None:
		super().__init__()