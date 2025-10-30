from pathlib import (
	Path as _Path
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Tuple as _Tuple,
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
	
def get_dataset(file:_Path, nrows:_Optional[int], use_cols:_Optional[_List[str]]):
	''' Returns the dataset, raises FileNotFoundError if not file.exists(). '''
	if not file.exists():
		raise FileNotFoundError(f'Dataset not found @ {file}')
	return _pd.read_csv(file, nrows=nrows, usecols=use_cols)