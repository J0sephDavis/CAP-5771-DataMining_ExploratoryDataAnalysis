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

def mass_analysis(score_threshold:int, drop_below_threshold:bool,
				  frac:float, root_folder:Path, binary:bool,
				  neighbors:List, metrics:List, dist:List):
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	ucs=UserContentScore(
		filter=ulf,
		binary=binary,
		score_threshold_gt=score_threshold,
		frac=frac,
		drop_below_threshold=drop_below_threshold,
		parent_folder=root_folder
	)
	del ulf
	gc.collect()
	
	could_not_complete:List[Tuple[Tuple,BaseException]] = []
	interrupted:bool = False
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
	# Dump errors
	for rec in could_not_complete:
		_logger.error(f'dist:{rec[0][0]} neigh:{rec[0][1]} metrc:{rec[0][2]}.. Failed {str(rec[1])}',exc_info=rec[1])
	return interrupted
	

def main():
	folder =Path('18 UMAP Exploration')

	folder.mkdir(mode=0o775, exist_ok=True, parents=True)

	neighbors = [1024]
	frac_data = 0.1
	for t in [7,8,9,5]:
		_logger.info('perform binary analysis')
		if mass_analysis( # BINARY no-drop @5
				score_threshold=t, frac=frac_data,
				drop_below_threshold=True,
				root_folder=folder,
				binary=False,
				neighbors=neighbors,
				metrics=['cosine'],
				dist=[None]):
			return