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
from AnimeList.clean import AnimeListClean
from RankingList.contentcontent import UserContentScore
import umap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional
from pathlib import Path
def run_umap(folder:Optional[Path],data:UserContentScore, n_neighbors:int, min_dist:float,metric:str):
	umap_results = data.run_umap(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
		data=umap_results, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	if folder is not None:
		file = folder.joinpath(f'umap ucs {metric} {n_neighbors}_neighbors {min_dist}_dst.tiff')
	else:
		file=f'umap ucs {metric} {n_neighbors}_neighbors {min_dist}_dst.tiff'
	f.savefig(file)
	
def main():
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	# Create Users-Content with score as value
	ucs=UserContentScore(ulf)
	del ulf
	# Perform UMAP
	folder:Path = Path('final_umap')
	folder.mkdir(mode=0o775, parents=False, exist_ok=True)
	min_dists=[0,0.2,0.4,0.6,0.8,1.0]
	neighbors=[2,4,8,16,32,64,128,256,512]
	metrics=['cosine','minkowski','chebyshev','manhattan','euclidean']
	for dist in min_dists:
		for n in neighbors:
			for metric in metrics:
				run_umap(folder=folder,data=ucs, n_neighbors=n, min_dist=dist, metric=metric)
	# Attempt to make a user-user similarity measure by finding users with similar ratings.