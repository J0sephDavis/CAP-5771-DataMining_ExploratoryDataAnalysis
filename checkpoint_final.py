'''
GOAL: get two pages worth of content?
- homophily measure?
    - Directional/Asymmetric
        - Intersection A&B / count(A)?
        - For sum of x in A & B x_a.rating-x_b.rating
            - average difference in ratings?
'''
from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.CP2')
from RankingList.dataset import UserListFilter, UserRankingColumn
def main():
    ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME])
    _logger.info(ulf.get_frame()[UserRankingColumn.USERNAME].unique().shape)