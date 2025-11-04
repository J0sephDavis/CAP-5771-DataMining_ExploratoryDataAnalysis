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
	
def get_dataset(file:_Path, nrows:_Optional[int], use_cols:_Optional[_List[str]]):
	''' Returns the dataset, raises FileNotFoundError if not file.exists(). '''
	if not file.exists():
		raise FileNotFoundError(f'Dataset not found @ {file}')
	return _pd.read_csv(file, nrows=nrows, usecols=use_cols)


class DatasetBase:
	''' Represents a dataframe and its relationship to a file.'''
	nrows:_Optional[int]
	path:_Optional[_Path]
	frame:_Optional[_pd.DataFrame]
	use_columns:_Optional[_List[_Union[str,_StrEnum]]]

	def __init__(self,
			nrows:_Optional[int] = None,
			path:_Optional[_Path] = None,
			frame:_Optional[_pd.DataFrame] = None,
			use_columns:_Optional[_List[_Union[str,_StrEnum]]] = None,
			try_get_frame_now:bool = False
			)->None:
		'''
		nrows -- the number of rows you want, ONLY if you are loading from file.
		path -- the path to the dataset
		frame -- If you already have the dataframe, give it here.
		use_columns -- the columns you want to read during read_csv.
		try_get_frame -- calls get_frame, which will load from csv / do nothng if frame is already set.
		'''
		self.nrows = nrows
		self.path = path
		self.frame = frame
		self.use_columns = use_columns
		if try_get_frame_now:
			self.get_frame()

	def get_frame(self, force_reload:bool=False)->_Optional[_pd.DataFrame]:
		''' Loads from frame, fallsback to file, returns None if it could not get the data.
		force_reload -- if true, skips trying the existing frame and attempts to load from file.
		'''
		if (not force_reload) and (self.frame is not None):
			return self.frame
		if self.path is not None:
			self.frame = get_dataset(file=self.path, nrows=None, use_cols=self.use_columns)
			return self.frame
		print('Warning, no frame or path for dataset. Dataset will be None. TODO: Exception here?')
		return None
	