'''
GOAL: get two pages worth of content?
- homophily measure?
	- Directional/Asymmetric
		- Intersection A&B / count(A)?
		- For sum of x in A & B x_a.rating-x_b.rating
			- average difference in ratings?
'''
from helpers import stopwatch
from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.Final')
from RankingList.dataset import UserListFilter, UserRankingColumn
from AnimeList.clean import AnimeListClean
from RankingList.contentcontent import UserContentScore
import umap
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional,Tuple,List
from pathlib import Path

import gc

def mass_analysis(score_gte:int, score_lte:int,
				  frac:float, root_folder:Path,
				  neighbors:List, metrics:List, dist:List):
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	ucs=UserContentScore(
		filter=ulf,
		score_max=score_gte,
		score_min=score_lte,
		frac=frac,
		drop_below_threshold=drop_below_threshold,
		parent_folder=root_folder
	)
	del ulf
	gc.collect()
	
	could_not_complete:List[Tuple[Tuple,BaseException]] = []
	interrupted:bool = False
	s = stopwatch.Stopwatch()
	for m in metrics:
		if interrupted:
			break
		for n in neighbors:
			if interrupted:
				break
			for d in dist:
				if interrupted:
					break
				if d is None:
					d = 0.0 # default to 0

				_logger.info(f'starting umap with dist:{dist} n:{n} metric:{m}')
				s.start()
				try:
					ucs.run_umap(
						n_neighbors=n,
						min_dist=d,
						metric=m
					)
				except KeyboardInterrupt:
					_logger.info('keyboard interrupt. attempting to quit.')
					interrupted=True
				except BaseException as e:
					_logger.error(f'Could not complete umap... Wait for report after we run the rest.\n{e}')
					could_not_complete.append(((dist,n,m),e))
				finally:
					plt.close('all')
					gc.collect()
					s.end()
					_logger.info(f'mass analysis iteration took {str(s)}')
	# Dump errors
	for rec in could_not_complete:
		_logger.error(f'dist:{rec[0][0]} neigh:{rec[0][1]} metrc:{rec[0][2]}.. Failed {str(rec[1])}',exc_info=rec[1])
	return interrupted
	
def main():
	folder =Path('18 UMAP Exploration')

	folder.mkdir(mode=0o775, exist_ok=True, parents=True)
	s= stopwatch.Stopwatch()
	thresholds:List[Tuple[int,int]] = [
		(1,4), (5,6), (7,8), (9,10)
	]
	for score_min, score_max in thresholds:
		_logger.info(f'score threshold: [{score_min},{score_max}]')
		s.start()
		if mass_analysis(
				score_gte=score_min, score_lte=score_max,
				frac=0.05,
				root_folder=folder,
				neighbors=[32],
				metrics=['hamming','jaccard'],
				dist=[None]
			):
			s.end()
			_logger.info(f'mass_anlysis (INTERUPTED) took: {str(s)}')
			return
		else:
			s.end()
			_logger.info(f'mass_anlysis took: {str(s)}')