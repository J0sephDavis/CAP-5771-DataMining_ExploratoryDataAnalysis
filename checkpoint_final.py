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
def run_umap(data:UserContentScore, n_neighbors:int=2):
	umap_results = data.run_umap()
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
		data=umap_results, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig(f'umap ucs {n_neighbors}_neighbors.tiff')
	
def main():
	ulf=UserListFilter(frame=None, cols=[UserRankingColumn.USERNAME,UserRankingColumn.ANIME_ID,UserRankingColumn.SCORE])
	# Create Users-Content with score as value
	ucs=UserContentScore(ulf)
	del ulf
	# Perform UMAP
	neighbors=[2,4,8,16,32,64,128,256,512]
	for n in neighbors:
		run_umap(ucs, n_neighbors=n)
	# Attempt to make a user-user similarity measure by finding users with similar ratings.