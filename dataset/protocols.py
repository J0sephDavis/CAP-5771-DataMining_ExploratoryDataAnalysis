from typing import (
	Protocol as _Protocol,
	Optional as _Optional,
	Type as _Type,
)
from enum import (
	StrEnum as _StrEnum
)
from pathlib import (
	Path as _Path
)
import pandas as _pd
from helpers.exceptions import (
	DatasetMissingFrame as _DatasetMissingFrame,
)
from abc import (
	ABC as _ABC,
	abstractmethod as _abstractmethod,
)

class DatasetProtocolFrame(_Protocol):
	''' Describes the dataframe.
	frame -- Optional because it may not have been loaded yet.
	'''
	frame:_Optional[_pd.DataFrame]
	def get_frame(self):
		''' Returns the frame or raises DatasetMissingFrame. '''
		if self.frame is None:
			raise _DatasetMissingFrame('')
		return self.frame

class DatasetProtocolFile(_Protocol):
	''' Describes the file. '''
	file:_Path # The path to the object

class DatasetSavable(DatasetProtocolFile, DatasetProtocolFrame, _ABC):
	''' Base class for saving implementations '''
	@_abstractmethod
	def save(self, **kwargs)->None:
		''' Save frame to a file. '''
		pass

class DatasetLoadable(DatasetProtocolFile, DatasetProtocolFrame, _ABC):
	''' Base class for loading implementations'''
	@_abstractmethod
	def load(self)->None:
		''' Load frame from a file. '''
		pass