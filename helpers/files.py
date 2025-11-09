from pathlib import (
	Path as _Path
)
import pandas as _pd
from typing import (
	Optional as _Optional,
	List as _List,
	Union as _Union,
)
from enum import StrEnum as _StrEnum
from .exceptions import (
	DatasetFileExists as _DatasetFileExists,
	DatasetMissingFrame as _DatasetMissingFrame,
)
import logging as _logging
from .context import APP_LOGGER_NAME as _APP_LOGGER_NAME
_logger = _logging.getLogger(f'{_APP_LOGGER_NAME}.Helpers.Files')

def should_continue_with_file(
		filename:_Path,
		clobber:bool=False,
		raise_exception:bool=True
	)->bool:
	''' Returns (continue_with_operation, file_already_exists)'''
	exists:bool = filename.exists()
	if exists:
		if clobber:
			_logger.warning(f'File already exists, allowing overwrite. {filename}')
			return True
		elif raise_exception:
			err =  FileExistsError(f'File already exists. {filename}')
			_logger.error('should_continue_with_file',exc_info=err)
			raise err
		return False
	return True