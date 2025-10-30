from dotenv import load_dotenv, find_dotenv, dotenv_values
from typing import Tuple, Dict, List, Optional, Any, Callable
from enum import StrEnum
import datetime
import os

class EnvException(Exception):
	pass
class EnvExceptionKeyError(EnvException):
	pass
class EnvExceptionMissingValue(EnvException):
	pass

def todays_date_iso8601()->str:
	return datetime.datetime.now().strftime(r'%Y-%m-%d')

_default_dotenv_path:str = 'data.env'
_unknown_field_prefix = '?!: '

class EnvRequiredFields(StrEnum):
	USER_LIST='MAL_USER_LIST'
	RANKING_LIST='MAL_RANKING_LIST'
	ANIME_LIST='MAL_ANIME_LIST'
	
	CF_FOLDER='CF_FOLDER' # Cleaned and Filtered root folder
	CF_FOLDER_COMPARE='CF_FOLDER_COMPARE' # Cleaned and Filtered root folder
	CF_FOLDER_CLEANED='CF_FOLDER_CLEANED' # Where The cleaned data & figures can be found
	CF_FOLDER_FILITED='CF_FOLDER_FILTERED'
	
	ANIME_FILTERED='ANIME_FILTERED' # Where the filtered anime dataset can be found
	ANIME_CLEANED='ANIME_CLEANED' # Where the cleaned dataset can be found

_env_known_fields:List[str] = [x.value for x in EnvRequiredFields]

def _get_len_safe(val)->int:
	""" Get val repr then measure len"""
	val=str(val)
	return len(val)

def _get_max_lengths(env_vals:Dict, preprocess_value:Callable[[Any],Any])->Tuple[int,int]:
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

def pretty_print_key_val(env_vals:Dict, remove_prefix:Optional[str]=os.getcwd()):
	""" Pretty print a dictionary by key,val. Removes cwd from all values. """
	if remove_prefix is not None:
		def preprocess_value(value)->Any:
			''' Removes prefix from string '''
			if isinstance(value,str):
				return value.removeprefix(remove_prefix)
			return value
	else:
		def preprocess_value(value)->Any:
			return value
	max_key_len, max_value_len = _get_max_lengths(env_vals, preprocess_value)
	
	header:str = f" {'KEY':{max_key_len}s} | {'VALUE':{max_value_len}s}"
	separator:str = '-'*len(header)
	print(separator,header,separator,sep='\n')
	for k,v in env_vals.items():
		v = preprocess_value(v)
		if (k not in _env_known_fields):
			k = f'{_unknown_field_prefix}{k}'
		print(' {0:{key_col_width}s} | {1:{value_col_width}s}'.format(
			k,v,
			key_col_width=max_key_len,
			value_col_width=max_value_len)
		)
	print(separator)

def load_find_env(
			dotenv_path:str=_default_dotenv_path, override_env:bool=True,
			use_cwd:bool=True, raise_error_if_not_found:bool=True,
			pretty_print_remove_suffix:Optional[str] = os.getcwd()
		)->Tuple[bool,str]:
	""" Loads the dotenv & returns load_dotenv(), find_dotenv()"""
	try:
		path:str = find_dotenv(
			filename=dotenv_path, usecwd=use_cwd,
			raise_error_if_not_found=raise_error_if_not_found
		)
	except OSError as e:
		print( # Begin formatted block, do not indent.
f"""
{str(e.__class__)}{'-'*(80-len(str(e.__class__)))}
{e}
	find_dotenv could not find the requested dotenv.
	dotenv_path:{dotenv_path}
	use_cwd:{use_cwd}.
Please check the filename.
{'-'*80}"""
		) # End formatted block.
		raise e # Raise again to stop execution & print traceback
	success = load_dotenv(dotenv_path=path, override=override_env)
	pretty_print_key_val(dotenv_values(path), f'{os.getcwd()}')
	return success, path

def get_env_val_safe(key:str)->str:
	''' Get an env value safely, if the value is None, raise KeyError '''
	val = os.getenv(key,None)
	if val is None:
		raise KeyError(f'Could not get env value with  key: {key}')
	return val

if __name__ == '__main__':
	loaded,path = load_find_env(pretty_print_remove_suffix=os.getcwd())