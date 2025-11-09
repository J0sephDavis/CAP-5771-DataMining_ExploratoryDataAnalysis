import logging
import platform
import os
from pathlib import Path
from datetime import datetime
logger = logging.getLogger('DM04')
logger.info('Beginning Project')
logger.setLevel(logging.DEBUG)
LOG_FORMATTER = logging.Formatter(fmt=r'%(levelname)s;%(name)s;%(asctime)s %(message)s')
def _setup_handler(handler:logging.Handler):
	handler.setFormatter(LOG_FORMATTER)
	logger.addHandler(handler)
date_format:str = r'%Y-%m-%d %H:%M:%S' if platform.system().casefold() != 'windows' else r'%Y-%m-%d %H_%M_%S'
log_folder=Path('logs')
log_folder.mkdir(mode=0o777, parents=True,exist_ok=True)
FILE_HANDLER = logging.FileHandler(
	filename= log_folder.joinpath(f'{datetime.now().strftime(date_format)} DM04.log'), mode='w'
)
FILE_HANDLER.setLevel(logging.DEBUG)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.INFO)

_setup_handler(FILE_HANDLER)
_setup_handler(STREAM_HANDLER)
logger.info(f'There are {len(os.listdir(log_folder))} log files.')

from dataclasses import dataclass
from typing import ClassVar
from helpers.context import load_find_env
load_find_env()


@dataclass
class control_flow:
	run_checkpoint_one:ClassVar[bool] = True
	run_checkpoint_two:ClassVar[bool] = True
try:
	logger.info(f'run_checkpoint_one: {control_flow.run_checkpoint_one}')
	if control_flow.run_checkpoint_one:
		import c1_animelist
		c1_animelist.run()

	logger.info(f'run_checkpoint_two: {control_flow.run_checkpoint_two}')
	if control_flow.run_checkpoint_two:
		import checkpoint2
		checkpoint2.run()
except Exception as e:
	logger.error('Exception in main:',exc_info=e)
	logging.shutdown()
	raise e
logger.error('Exit.')
logging.shutdown()