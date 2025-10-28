from pathlib import Path
from typing import Tuple
def should_continue_with_file(filename:str, clobber:bool=False, raise_exception:bool=True)->Tuple[bool,bool]:
	''' Returns (continue_with_operation, file_already_exists)'''
	path = Path(filename)
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