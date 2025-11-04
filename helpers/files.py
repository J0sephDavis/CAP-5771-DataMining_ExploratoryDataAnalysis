from pathlib import (
	Path as _Path
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Tuple as _Tuple,
	Union as _Union,
)
from enum import StrEnum as _StrEnum
from .exceptions import (
	DatasetFileExists as _DatasetFileExists,
	DatasetMissingFrame as _DatasetMissingFrame,
)
def should_continue_with_file(filename:str, clobber:bool=False, raise_exception:bool=True)->_Tuple[bool,bool]:
	''' Returns (continue_with_operation, file_already_exists)'''
	path = _Path(filename)
	if not path.exists():
		return True,False # Continue, file does not exist.
	if clobber:
		print(f'WARNING, {filename} already exists. Overwriting.')
		return True,True # Continue, clobber file.
	if (raise_exception):
		raise FileExistsError(f'{filename}')
	else:
		print(f'WARNING, {filename} already exists. Do not continue.')
		return False,True # Do not continue, file already exists
	
class DatasetBase:
	''' Represents a dataframe and its relationship to a file.'''
	nrows:_Optional[int]
	path:_Path
	frame:_Optional[_pd.DataFrame]
	use_columns:_Optional[_List[_Union[str,_StrEnum]]]

	def __init__(self,
			path:_Path,
			nrows:_Optional[int] = None,
			frame:_Optional[_pd.DataFrame] = None,
			use_columns:_Optional[_List[_Union[str,_StrEnum]]] = None,
			)->None:
		'''
		path -- the path to the dataset
		nrows -- the number of rows you want, ONLY if you are loading from file.
		frame -- If you already have the dataframe, give it here.
		use_columns -- the columns you want to read during read_csv.
		'''
		self.nrows = nrows
		self.path = path
		self.frame = frame
		self.use_columns = use_columns
		if self.frame is not None:
			self.save()
		elif self.path.exists():
			self.load()
	
	def get_frame(self)->_pd.DataFrame:
		if self.frame is None:
			raise _DatasetMissingFrame()
		return self.frame

	def load(self, force_reload:bool=False, **read_csv_kwargs)->None:
		''' Loads from frame, fallsback to file, raiases exception if it could not get the data.
		force_reload -- if true, skips trying the existing frame and attempts to load from file.
		'''
		if (not force_reload) and (self.frame is not None):
			return
		if not self.path.exists():
			raise FileNotFoundError('Dataset file not found.')
		self.frame = _pd.read_csv(
			filepath_or_buffer = self.path,
			nrows = self.nrows,
			usecols = self.use_columns,
			**read_csv_kwargs
		)
	
	def save(self, clobber:bool=True, include_index:bool=False, **to_csv_kwargs):
		if self.frame is None:
			raise _DatasetMissingFrame('Cannot save frame, frame is not loaded.')
		if (not clobber) and self.path.exists():
			raise _DatasetFileExists('Cannot save frame, file already exists.')
		self.frame.to_csv(
			path_or_buf=self.path,
			index=include_index,
			**to_csv_kwargs
		)