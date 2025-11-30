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
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional,Tuple,List
from pathlib import Path

def run_umap(folder:Optional[Path],data:UserContentScore, n_neighbors:int, min_dist:float,metric:str, label:str):
	if folder is not None:
		file = folder.joinpath(f'umap ucs {metric} {n_neighbors}_neighbors {min_dist}_dst.tiff')
	else:
		file=Path(f'umap ucs {metric} {n_neighbors}_neighbors {min_dist}_dst.tiff')
	_logger.info(f'does file: {file} exist?')
	if file.exists():
		_logger.info('file already exists... skip.')
		return
	_logger.info('run umap')
	umap_results = data.run_umap(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric, label=label)
	_logger.info('plot data')
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
		data=umap_results, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig(file)
	plt.close(fig=f)

import gc

def generate_data(dataset:UserContentScore, neighbors:List, metrics:List, dist:List, folder:Path)->bool:
	''' Returns True if interrupted. '''
	
	could_not_complete:List[Tuple[Tuple,BaseException]] = []
	interrupted:bool = False
	for m in metrics:
		if interrupted: break

		for n in neighbors:
			if interrupted: break

			for d in dist:
				if interrupted: break
				if d is None: d = 0.0

				_logger.info(f'starting umap with dist:{dist} n:{n} metric:{m}')
				try:
					run_umap(folder=folder,data=dataset, n_neighbors=n, min_dist=d, metric=m, label=f'{m} n{n} d{d}')
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

def non_binary_analysis(folder:Path,score_threshold:int):
	_logger.info(f'non-binary analysis. folder:{folder}, score_thresh:{score_threshold}')
	folder.mkdir(mode=0o775, parents=False, exist_ok=True)
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	ucs=UserContentScore(filter=ulf, binary=False, score_threshold_gt=score_threshold) # Positive values marked as such.
	del ulf
	gc.collect()
	metrics=['cosine','chebyshev','manhattan','euclidean']
	neighbors = [16,32,256,1024]
	generate_data(dataset=ucs, metrics=metrics, neighbors=neighbors, folder=folder, dist=[None])
	pass

def binary_analysis(folder:Path, score_threshold:int):
	_logger.info(f'binary analysis. folder:{folder}, score_thresh:{score_threshold}')
	folder.mkdir(mode=0o775, parents=False, exist_ok=True)
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	ucs=UserContentScore(filter=ulf, binary=True, score_threshold_gt=score_threshold) # Positive values marked as such.
	del ulf
	gc.collect()
	metrics = ['hamming','jaccard','yule','kulsinski']
	neighbors = [16,32,256,1024]
	generate_data(dataset=ucs, metrics=metrics, neighbors=neighbors, folder=folder, dist=[None])
	pass

def main():
	if binary_analysis(Path('umap_binary_data_thresh5'), 5):
		return
	if non_binary_analysis(Path('umap_nonbinary_data_thresh5'), 5):
		return