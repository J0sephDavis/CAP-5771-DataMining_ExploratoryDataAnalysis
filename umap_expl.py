from typing import List
from collections import Counter
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz
from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as plt
folder:Path = Path(
	'/home/joseph/Desktop/BARC1447_SHARED/18 UMAP Exploration/__UCS score_9 frac_0.1 bin_True drop_True'
)
name:str = 'umap m_jaccard n_1024 d_0.0'

def plot_umap(file_plot:Path, data:pd.DataFrame,alpha:float, major_freq:int=20, minor_freq:int=40):
	# file_plot = folder.joinpath(f'{name}.tiff')
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x='UMAP-X', y='UMAP-Y', hue='UMAP-Y',
		data=data, legend='auto',alpha=alpha,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	from matplotlib import ticker
	ax.xaxis.set_major_locator(locator=ticker.MaxNLocator(major_freq))
	ax.yaxis.set_major_locator(locator=ticker.MaxNLocator(major_freq))
	# ax.xaxis.set_minor_locator(locator=ticker.MaxNLocator(minor_freq))
	# ax.yaxis.set_minor_locator(locator=ticker.MaxNLocator(minor_freq))
	ax.grid(visible=True, which='major',axis='both')
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig(file_plot)
	plt.close(fig=f)

file_umap_result = folder.joinpath(f'{name}.csv')
file_frame_subset = folder.joinpath('frame.csv')
file_csr_matrix=folder.joinpath('dataset.npz')
file_anime_list = Path('/home/joseph/Desktop/BARC1447_SHARED/AnimeList.csv')
files = [
	file_umap_result, file_frame_subset, file_csr_matrix, file_anime_list
]
for file in files:
	if not file.exists():
		raise FileNotFoundError(f'missing file {file}')

frame_subset = pd.read_csv(file_frame_subset, index_col='INDEX')
cat_user = pd.Categorical(frame_subset['username'])
cat_anime = pd.Categorical(frame_subset['anime_id'])

# Get row indicies from csr_matrix.tocoo().row
# Get column indices from coo.col
matrix = load_npz(folder.joinpath('dataset.npz'))
_mshape = matrix.shape
if (_mshape[0] != cat_user.categories.shape[0]) or (_mshape[1] != cat_anime.categories.shape[0]):
	print('matrix shape',matrix.shape)
	print('cat users',cat_user.categories.shape[0])
	print('cat anime',cat_anime.categories.shape[0])
	print('Categories and matrix shape are not the same. This is old data with an overly sparse matrix..')

print('loading umap data')
umap_data = pd.read_csv(file_umap_result)
file_umap_no_na:Path = folder.joinpath(f'{name}_FILLED_NA.csv')
if not file_umap_no_na.exists():
	umap_data.fillna(value=99999).to_csv(folder.joinpath(f'FILLED NA {name}.csv'), index=False)

print('loading anime dataset')
anime_lit = pd.read_csv(file_anime_list, usecols=['anime_id','title','score','rank'])


def process_cluster(umap_data:pd.DataFrame, matrix:csr_matrix, label:str, alpha:float=0.5):
	print('process_cluster: ', label)
	''' matrix: entire csr
		umap: subset of data.
	'''
	file_cluster_umap = folder.joinpath(f'{name}_{label}_cluster.csv') # First cluster
	if not file_cluster_umap.exists():
		c_matrix = matrix[umap_data.index]
		print(f'selected {c_matrix.shape[0]} rows from the csr')
		c_rows, c_cols = c_matrix.nonzero()
		print('calculating col freq')
		c_col_freq = Counter(c_cols)
		pass
		print('preparing cluster dataset')
		c_frame = pd.DataFrame(data= {
				'code':list(c_col_freq.keys()),
				'freq':list(c_col_freq.values())
			}
		)
		c_frame['anime_id'] = c_frame['code'].map(lambda x: cat_anime[x])
		c_frame['percent'] = c_frame['freq']/c_matrix.shape[0] # Frequency / users
		c_frame= c_frame.merge(right=anime_lit, left_on='anime_id', right_on='anime_id', how='left')
		pass
		print('saving cluster dataset')
		c_frame.to_csv(file_cluster_umap,index=False)
		pass

	file_plot = folder.joinpath(f'{name}_{label}_cluster.tiff')
	if not file_plot.exists():
		print('plotting cluster')
		plot_umap(file_plot=file_plot, data=umap_data, alpha=alpha)

# UCS st 9 f 0.1 bin true drop true folder:'/home/joseph/Desktop/BARC1447_SHARED/18 UMAP Exploration/__UCS score_9 frac_0.1 bin_True drop_True'  name:'umap m_jaccard n_1024 d_0.0'
all_alp=0.05
file_umap_grid_plot = folder.joinpath(f'{name}_WITH_GRID_a{all_alp}.tiff')
if not file_umap_grid_plot.exists():
	print('replotting umap data with grid')
	plot_umap(file_plot=file_umap_grid_plot, data=umap_data,alpha=all_alp)

process_cluster(
	umap_data=umap_data.loc[
			(umap_data['UMAP-X'] > 0)	& (umap_data['UMAP-X'] < 13)
		&   (umap_data['UMAP-Y'] < 8)	& (umap_data['UMAP-Y'] > 4)
	],
	matrix=matrix,
	label='alpha',
	alpha=0.8
)
bravo_data = umap_data.loc[
		(umap_data['UMAP-X'] > 150)	& (umap_data['UMAP-X'] < 160)
	&   (umap_data['UMAP-Y'] > 18)	& (umap_data['UMAP-Y'] < 21)
]
process_cluster(
	umap_data=bravo_data,
	matrix=matrix,
	label='bravo',
	alpha=0.2
)
process_cluster(
	umap_data=umap_data.loc[
			(umap_data['UMAP-X'] >= 152.8)	& (umap_data['UMAP-X'] <= 153.2)
		&   (umap_data['UMAP-Y'] >= 20.10)	& (umap_data['UMAP-Y'] <= 20.25)
	],
	matrix=matrix,
	label='charlie',
	alpha=0.8
)
delta_data = umap_data.loc[
			(umap_data['UMAP-X'] >= 154.4)	& (umap_data['UMAP-X'] <= 154.8)
		&   (umap_data['UMAP-Y'] >= 19.80)	& (umap_data['UMAP-Y'] <= 19.95)
	]
process_cluster(
	umap_data=delta_data,
	matrix=matrix,
	label='delta',
	alpha=0.8
)
label='bravo'
file_label_low_alp = folder.joinpath(f'{name}_{label}_a{all_alp}.tiff')
if not file_label_low_alp.exists():
	print(f'replotting {label} with low alp')
	plot_umap(
		file_plot=file_label_low_alp,
		data=bravo_data,
		alpha=all_alp
	)



echo_data = umap_data.loc[
			(umap_data['UMAP-X'] >= 155.6)	& (umap_data['UMAP-X'] <= 156.4)
		&   (umap_data['UMAP-Y'] >= 19.50)	& (umap_data['UMAP-Y'] <= 19.80)
	]
process_cluster(
	umap_data=echo_data,
	matrix=matrix,
	label='echo',
	alpha=0.5
)

process_cluster(
	umap_data=umap_data.loc[
			(umap_data['UMAP-X'] >= 152.8)	& (umap_data['UMAP-X'] <= 153.3)
		&   (umap_data['UMAP-Y'] >= 20.10)	& (umap_data['UMAP-Y'] <= 20.3)
	],
	matrix=matrix,
	label='fox',
	alpha=0.5
)