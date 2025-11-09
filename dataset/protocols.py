from typing import (
	Protocol as _Protocol,
	Optional as _Optional
)
from pathlib import (
	Path as _Path
)
import pandas as _pd
from helpers.exceptions import (
	DatasetMissingFrame as _DatasetMissingFrame,
	DatasetNotFound as _DatasetNotFound,
)
from abc import (
	ABC as _ABC,
	abstractmethod as _abstractmethod,
)

class DatasetProtoclFrame(_Protocol):
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

class DatasetSavable(DatasetProtocolFile, DatasetProtoclFrame, _ABC):
	''' Base class for saving implementations '''
	@_abstractmethod
	def save(self, **kwargs)->None:
		''' Save frame to a file. '''
		pass
	
class DatasetLoadable(DatasetProtocolFile, DatasetProtoclFrame, _ABC):
	''' Base class for loading implementations'''
	@_abstractmethod
	def load(self)->None:
		''' Load frame from a file. '''
		pass