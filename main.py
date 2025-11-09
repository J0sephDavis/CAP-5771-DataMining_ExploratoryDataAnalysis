import logging
logger = logging.getLogger('DM04')
logger.info('Beginning Project')
# TODO: setup logger handles. 
from helpers.context import load_find_env
load_find_env()

from dataclasses import dataclass
from typing import ClassVar

@dataclass
class control_flow:
	run_checkpoint_one:ClassVar[bool] = True
	run_checkpoint_two:ClassVar[bool] = True

logger.info(f'run_checkpoint_one: {control_flow.run_checkpoint_one}')
if control_flow.run_checkpoint_one:
	import c1_animelist
	c1_animelist.run()

logger.info(f'run_checkpoint_two: {control_flow.run_checkpoint_two}')
if control_flow.run_checkpoint_two:
	import checkpoint2
	checkpoint2.run()