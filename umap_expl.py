from typing import List
from collections import Counter
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz
from pathlib import Path

folder:Path = Path('/home/joseph/Desktop/BARC1447_SHARED/18 UMAP Exploration/UCS score_7 frac_0.03 bin_False drop_True')
file_umap_result = folder.joinpath('umap m_cosine n_1024 d_0.0.csv')
file_frame_subset = folder.joinpath('frame.csv')
file_csr_matrix=folder.joinpath('dataset.npz')
file_anime_list = Path('/home/joseph/Desktop/BARC1447_SHARED/AnimeList.csv')
files = [
	file_umap_result, file_frame_subset, file_csr_matrix, file_anime_list
]
for file in files:
	if not file.exists():
		raise FileNotFoundError(f'missing file {file}')

# Load the subset frame and get all usernames
# use pd.Categorical to get user categorical codes
# use pd.Categorical to get anime categorical codes
frame_subset = pd.read_csv(file_frame_subset, index_col='INDEX')
cat_user = pd.Categorical(frame_subset['username'])
cat_anime = pd.Categorical(frame_subset['anime_id'])

# Get row indicies from csr_matrix.tocoo().row
# Get column indices from coo.col
matrix = load_npz(folder.joinpath('dataset.npz'))
_mshape = matrix.shape
if (_mshape[0] != cat_user.categories.shape[0]) or (_mshape[1] != cat_anime.categories.shape[0]):
	print('matri shape',matrix.shape)
	print('cat users',cat_user.categories.shape[0])
	print('cat anime',cat_anime.categories.shape[0])
	raise Exception('Categories and matrix shape are not the same. This is old data with an overly sparse matrix..')
pass
print('loading umap data')
umap_data = pd.read_csv(file_umap_result)
alpha_umap = umap_data.loc[
		(umap_data['UMAP-X'] > 30)	& (umap_data['UMAP-X'] < 40)
	&   (umap_data['UMAP-Y'] < -15)	& (umap_data['UMAP-Y'] > -20)
]
# alpha_dense = pd.DataFrame(matrix[umap_data.index].todense()).join(other=umap_data)
csr_alpha = matrix[umap_data.index]
print(f'selected {csr_alpha.shape[0]} rows from the csr')
alpha_rows, alpha_cols = csr_alpha.nonzero()
print('column frequency calculated')
alpha_col_freq = Counter(alpha_cols)
pass
print('preparing cluster dataset')
alpha_cluster = pd.DataFrame(data= {
		'code':list(alpha_col_freq.keys()),
		'freq':list(alpha_col_freq.values())
	}
)
alpha_cluster['anime_id'] = alpha_cluster['code'].map(lambda x: cat_anime[x])
alpha_cluster['percent'] = alpha_cluster['freq']/alpha_cluster.shape[0]
# Merge anime information for analysis
print('loading anime dataset')
anime_lit = pd.read_csv(file_anime_list, usecols=['anime_id','title','score','rank'])
alpha_cluster= alpha_cluster.merge(right=anime_lit, left_on='anime_id', right_on='anime_id', how='left')
# # Merge UMAP data (IMPOSSIBLE! Becuse UMAP is by user not anime.)
# if alpha_cluster.shape[0] != alpha_umap.shape[0]:
# 	print('alpha:',alpha_cluster.shape)
# 	print('umap:',alpha_umap.shape)
# 	raise Exception('alpha subset not the same len as umap data?')
# alpha_cluster = alpha_cluster.merge(right=alpha_umap, left_index=True, right_index=True)
# save
print('saving cluster dataset')
file_alpha = folder.joinpath('alpha_cluster.csv') # First cluster
alpha_cluster.to_csv(file_alpha,index=False)
# Translate the column id to anime_id

# Translate the row id to uernames