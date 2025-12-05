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
from typing import Optional,Tuple,List,Dict,Union
from pathlib import Path
from scipy.sparse import csr_matrix, save_npz, load_npz
import umap

import gc

def mass_analysis(score_gte:int, score_lte:int,
				  frac:float, root_folder:Path,
				  neighbors:List, metrics:List,
				  dist:List, do_plot:bool):
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	ucs=UserContentScore(
		filter=ulf,
		score_max=score_gte,
		score_min=score_lte,
		frac=frac,
		parent_folder=root_folder
	)
	del ulf
	gc.collect()
	arguments:List[Dict] = []
	for m in metrics:
		for n in neighbors:
			for d in dist:
				if d is None:
					d = 0.0
				arguments.append({
					'n_neighbors':n,
					'min_dist':d,
					'metric':m,
					'do_plot':do_plot
				})
	could_not_complete:List[Tuple[Dict,BaseException]] = []
	interrupted:bool = False
	s = stopwatch.Stopwatch()
	for arg in arguments:
		if interrupted:
			break
		_logger.debug(f'mass_analysis, arg={arg}')
		s.start()
		try:
			ucs.run_umap(**arg)
		except KeyboardInterrupt:
			_logger.info('keyboard interrupt. attempting to quit.')
			interrupted=True
		except BaseException as e:
			_logger.error(f'Could not complete umap... Wait for report after we run the rest.\n{e}')
			could_not_complete.append(((arg),e))
		finally:
			plt.close('all')
			gc.collect()
			s.end()
			_logger.info(f'mass analysis iteration took {str(s)}')
	# Dump errors
	for rec in could_not_complete:
		_logger.error(f'{rec[0]}.. Failed {str(rec[1])}',exc_info=rec[1])
	return interrupted
	
def mass_umap_exploration():
	folder =Path('18 UMAP Exploration')

	folder.mkdir(mode=0o775, exist_ok=True, parents=True)
	s= stopwatch.Stopwatch()
	thresholds:List[Tuple[int,int]] = [
		(1,4), (5,6), (7,8), (9,10)
	]
	fracs = [0.05,0.1,0.5]
	for frac in fracs:
		for score_min, score_max in thresholds:
			_logger.info(f'score threshold: [{score_min},{score_max}], frac:{frac}')
			s.start()
			if mass_analysis(
					score_gte=score_min, score_lte=score_max,
					frac=frac,
					root_folder=folder,
					neighbors=[32,1024,2048],
					metrics=['hamming','jaccard'],
					dist=[None],
					do_plot=True
				):
				s.end()
				_logger.info(f'mass_anlysis (INTERUPTED) took: {str(s)}')
				return
			else:
				s.end()
				_logger.info(f'mass_anlysis took: {str(s)}')
def main():
	# mass_umap_exploration() # Just explore a ton of variations
	folder = Path('19 UMAP User Case Study')
	file_dataset = folder.joinpath('dataset.npz')
	folder.mkdir(mode=0o775, parents=False,exist_ok=True)
	def file_data_subset(min,max)->Path:
		return folder.joinpath(f'dataset_{min}_{max}.npz')
	# - Case Study - 
	# 1. Sample a larger dataset & make a csr matrix removing only those with score=0
	dataset:csr_matrix
	if file_dataset.exists():
		dataset = load_npz(file_dataset)
	else:
		ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
		ucs=UserContentScore(
			filter=ulf,
			score_max=10,
			score_min=1,
			frac=0.05,
			parent_folder=folder
		)
		dataset = ucs.get_matrix()
		del ucs,ulf
	# 2. Create subsets with scores zeroed outside of the ranges: (1,4), (5,6), (7,8), (9,10)
	gc.collect()
	thresholds = [ (1,4), (5,6), (7,8), (9,10) ]
	for min,max in thresholds:
		file_subsets = file_data_subset(min,max)
		if file_subsets.exists():
			continue
		_logger.debug(f'create threshold subset: {min} {max}')
		matrix:csr_matrix = dataset.copy()
		mask = matrix.data < min
		matrix.data[mask] = 0
		mask = matrix.data > max
		matrix.data[mask] = 0
		matrix.eliminate_zeros()
		save_npz(file_data_subset(min,max), matrix)
		del matrix,mask,file_subsets
		gc.collect()
	del dataset
	gc.collect()
	
	sw = stopwatch.Stopwatch()

	def run_umap(neighbors:int,min:int,max:int):
		label:str = f'jaccard score_{min}_{max} n_{neighbors}'
		file_umapdata = folder.joinpath(f'umap {label}.csv')
		if file_umapdata.exists():
			_logger.info(f'Load prev UMAP {label}')
			return pd.read_csv(file_umapdata)
		_logger.info(f'Perf UMAP {label}')
		reducer = umap.UMAP(
			n_neighbors=neighbors,
			metric='jaccard'
		)
		sw.start()
		embedding = reducer.fit_transform(load_npz(file_data_subset(min,max)))
		sw.end()
		_logger.info(f'umap fit_transform took: {str(sw)}')
		umap_data = pd.DataFrame(embedding, columns=['UMAP-X','UMAP-Y'])
		_logger.debug('saving umap to file')
		sw.start()
		umap_data.to_csv(file_umapdata,index=False)
		sw.end()
		_logger.debug(f'saving to csv took: {str(sw)}')
	
	neighbors = [32,1024]
	for n in neighbors:
		for min,max in thresholds:
			_logger.info(f'min_{min}\tmax_{max}\tneighbors_{n}')
			run_umap(neighbors=n,min=min,max=max)
	gc.collect()
	# 3. Choose a random user in the dataset and record their nearest neighbors at each score level:
	# 	- [USER_ID, DIST_A, DIST_B, DIST_C, DIST_D] # Where DIST_A would be the distance of the USER_ID from our selected user in the (1,4) graph.
	# 4. Find the top-n neighbors in the distance matrix for each bin and record [USER_ID,AVG_DIST,MED_DIST]
	# 5. Replot UMAP with the neighbors colored by AVG/MED_DIST
	