from dotenv import (
	load_dotenv as _load_dotenv,
	find_dotenv as _find_dotenv,
	dotenv_values as _dotenv_values,
)
from typing import (
	Tuple as _Tuple,
	Dict as _Dict,
	List as _List,
	Optional as _Optional,
	Any as _Any,
	Callable as _Callable,
	Union as _Union
)
from enum import StrEnum as _StrEnum
import datetime as _datetime
import os as _os

class EnvException(Exception):
	''' Generic Environment Exception '''
	pass
class EnvExceptionKeyError(EnvException):
	''' Key is not an EnvField '''
	pass
class EnvExceptionMissingValue(EnvException):
	''' Value is None & was not expected to be None. '''
	pass

def todays_date_iso8601()->str:
	return _datetime.datetime.now().strftime(r'%Y-%m-%d')

_default_dotenv_path:str = 'data.env'
_unknown_field_prefix = '?!: '
APP_LOGGER_NAME='DM04'
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.helpers.context')

class EnvFields(_StrEnum):
	USER_LIST='USER_LIST'
	RANKING_LIST='RANKING_LIST'
	ANIME_LIST='ANIME_LIST'
	
	DIR_ANIME_DATASETS='DIR_ANIME_DATASETS'
	CSV_ANIME_FILTER='CSV_ANIME_FILTER'
	CSV_ANIME_FILTER_OUT='CSV_ANIME_FILTER_OUT'
	CSV_ANIME_CLEAN='CSV_ANIME_CLEAN'
	CSV_ANIME_CLEAN_OUT='CSV_ANIME_CLEAN_OUT'

	DIR_FIGURES_ANIME='DIR_FIGURES_ANIME'
	DIR_FIGURES_ANIME_FILTER='DIR_FIGURES_ANIME_FILTER'
	DIR_FIGURES_ANIME_CLEAN='DIR_FIGURES_ANIME_CLEAN'
	DIR_FIGURES_ANIME_COMPARISON='DIR_FIGURES_ANIME_COMPARISON'

	DIR_FIGURES_RANKINGS='DIR_FIGURES_RANKINGS'
	DIR_FIGURES_RANKINGS_FILTER='DIR_FIGURES_RANKINGS_FILTER'
	DIR_FIGURES_RANKINGS_CLEAN='DIR_FIGURES_RANKINGS_CLEAN'
	
	DIR_RANKING_DATASETS='DIR_RANKING_DATASETS'
	CSV_RANKINGS_PREFILTER='CSV_RANKINGS_PREFILTER'
	CSV_RANKINGS_PREFILTER_OUT='CSV_RANKINGS_PREFILTER_OUT'
	
	CSV_RANKING_FILTER='CSV_RANKING_FILTER'
	CSV_RANKING_FILTER_OUT='CSV_RANKING_FILTER_OUT'

	CSV_RANKING_CLEAN='CSV_RANKING_CLEAN'
	CSV_RANKING_CLEAN_OUT='CSV_RANKING_CLEAN_OUT'

_env_known_fields:_List[str] = [x.value for x in EnvFields]

def _get_len_safe(val)->int:
	""" Get val repr then measure len"""
	val=str(val)
	return len(val)

def _get_max_lengths(env_vals:_Dict, preprocess_value:_Callable[[_Any],_Any])->_Tuple[int,int]:
	''' Returns the maximum length of the keys & values from the passed dict. '''
	max_key_len:int = 4
	max_value_len:int = 6
	for k,v in env_vals.items():
		v = preprocess_value(v)
		max_key_len = max(max_key_len,
			_get_len_safe(k) + (0 if k in _env_known_fields else len(_unknown_field_prefix))
		)
		max_value_len = max(max_value_len, _get_len_safe(v)+1)
	return max_key_len, max_value_len

def pretty_print_key_val(env_vals:_Dict, remove_prefix:_Optional[str]=_os.getcwd()):
	""" Pretty print a dictionary by key,val. Removes cwd from all values. """
	if remove_prefix is not None:
		def preprocess_value(value)->_Any:
			''' Removes prefix from string '''
			if isinstance(value,str):
				return value.removeprefix(remove_prefix)
			return value
	else:
		def preprocess_value(value)->_Any:
			return value
	max_key_len, max_value_len = _get_max_lengths(env_vals, preprocess_value)
	
	header:str = f" {'KEY':{max_key_len}s} | {'VALUE':{max_value_len}s}"
	separator:str = '-'*len(header)
	output:_List[str] = [separator,header,separator]
	for k,v in env_vals.items():
		v = preprocess_value(v)
		if (k not in _env_known_fields):
			k = f'{_unknown_field_prefix}{k}'
		output.append(' {0:{key_col_width}s} | {1:{value_col_width}s}'.format(
			k,v,
			key_col_width=max_key_len,
			value_col_width=max_value_len)
		)
	output.append(separator)
	_logger.info('\n'.join(output))

def load_find_env(
			dotenv_path:str=_default_dotenv_path, override_env:bool=True,
			use_cwd:bool=True, raise_error_if_not_found:bool=True,
			pretty_print_remove_suffix:_Optional[str] = _os.getcwd()
		)->_Tuple[bool,str]:
	""" Loads the dotenv & returns load_dotenv(), find_dotenv()"""
	try:
		path:str = _find_dotenv(
			filename=dotenv_path, usecwd=use_cwd,
			raise_error_if_not_found=raise_error_if_not_found
		)
	except OSError as e:
		_logger.error(f"find_dotenv could not find the requested dotenv.\
			dotenv_path:{dotenv_path} use_cwd:{use_cwd}.\
			Please check the filename.",
			exc_info=e
		)
		raise e # Raise again to stop execution & print traceback
	success = _load_dotenv(dotenv_path=path, override=override_env)
	pretty_print_key_val(_dotenv_values(path), f'{pretty_print_remove_suffix}')
	return success, path

def get_env_val_safe(key:_Union[_StrEnum,str], default:_Optional[str]=None)->str:
	''' Get an env value safely
	- If key is a StrEnum, we expect it to be in our known field list; raises EnvExceptionKeyError
	- If value is None & default is None, raises EnvExceptionMissingValue
	- Otherwise, returns value, or default if value is None
	'''
	if isinstance(key,_StrEnum):
		if key not in _env_known_fields:
			err =  EnvExceptionKeyError(f'Unknown field passed to get_env_val_safe')
			_logger.error('get_env_val_safe:',exc_info=err)
			raise err

	val = _os.getenv(key,default)
		
	if val is None:
		err = EnvExceptionMissingValue(f'Could not get env value with key: {key}')
		_logger.error('get_env_val_safe:',exc_info=err)
		raise err
	_logger.info(f'get_env_val_safe->{val}')
	return val