from helpers.context import (
	get_env_val_safe,
	EnvFields,
	APP_LOGGER_NAME,
)
from helpers.stopwatch import Stopwatch
from pathlib import Path
import pandas as pd
from typing import (
	Optional,
	List,
	Tuple,
	Final,
)
from RankingList.dataset import (
	UserRankingList,
	UserRankingColumn,
	columns_for_retrieval as ranking_list_columns_for_retrieval,
	UserListPreFilter,
	UserListClean,
	UserListFilter,
)
from RankingList.contentcontent import (
	UserContentScore
)
from AnimeList.clean import AnimeListClean
from AnimeList.dataset import AnimeListColumns
import logging as _logging
_logger = _logging.getLogger(f'{APP_LOGGER_NAME}.CP2')
''' TODO
- [ ] Fetch dataset

- [ ] Clean
	- [ ] Remove invalid records
	- [ ] Fix invalid values, if we need to.

- [ ] Filter
	- [ ] ANIME_ID must be in our filtered & cleaned ANIME dataset.
	- [ ] 

- [ ] Boxplots for each feature
- [ ] Measure covariance of features
- [ ] Visualize covariant features
- [ ] UMAP, TSNE of data
'''

''' NOTE
 	My computer likely cannot handle loading this entire dataset at once.
	 	There are 80,076,112 records.
	We are going to ignore the following columns due to sparsity:
		- TAGS
		- REWATCHING
		- REWATCHING_EP
	We might ignore the following due to sparsity and lack of usability/reliability:
		- START_DATE
		- FINISH_DATE
		- LAST_UPDATED
	We primarily care about:
		- USERNAME
		- ANIME_ID
		- WATCHED_EPISODES
		- SCORE
		- STATUS
'''
import gc
def _generate_datasets():
	generate_prefilter:bool = not UserListPreFilter.default_path.exists()
	generate_clean:bool = generate_prefilter or not UserListClean.default_path.exists()
	generate_filter:bool = generate_clean or not UserListFilter.default_path.exists()

	sw = Stopwatch()
	pref:UserListPreFilter
	if generate_prefilter:
		_logger.info('Fetch raw user_rankings and the clean anime_list')
		sw.start()
		user_rankings = UserRankingList(nrows=None,usecols=ranking_list_columns_for_retrieval)
		sw.end()
		_logger.info(f'Loading user rankings took {str(sw)}')
		sw.start()
		anime_list = AnimeListClean(usecols=[AnimeListColumns.ANIME_ID])
		sw.end()
		_logger.info(f'Loading the anime list took {str(sw)}')

		# PRE FILTER - Remove records where the ANIME_ID is not found in our cleaned anime list
		_logger.info('Perform Prefiltering on raw data... (The removal of anime_id not found in our clean dataset).')	
		sw.start()
		pref,prefo = UserListPreFilter.prefilter_rankings(
			raw_rankings=user_rankings, anime_list=anime_list
		)
		sw.end()
		_logger.info(f'Prefiltering(1) took: {str(sw)}')
		del user_rankings
		gc.collect()
	elif generate_clean:
		pref = UserListPreFilter(frame=None)
	else:
		pref = None #  bs value to satisfy typesetter.
	
	clean:UserListClean
	if generate_clean:
		_logger.info('Perform cleaning on prefiltered data...')
		sw.start()
		clean, cleanedOut = UserListClean.clean_rankings(ranking=pref)
		sw.end()
		_logger.info(f'Cleaning(2) took: {str(sw)}')
		
		_logger.info('saving prefilter data')
		pref.save(index=False)
		del pref
		gc.collect()
	elif generate_filter:
		clean = UserListClean(frame=None)
	else:
		clean = None # bs value to satisfy typesetter
	
	filter:UserListFilter
	if generate_filter:
		_logger.info('Perform filtering on cleaned data...')
		sw.start()
		filter, filteredOut = UserListFilter.filter_rankings(cleaned_rankings=clean)
		sw.end()
		_logger.info(f'Filtering(3) took: {str(sw)}')
		
		_logger.info('saving clean data')
		clean.save(index=False)
		del clean
		gc.collect()
	else:
		filter = UserListFilter(frame=None)
	
	_logger.info('saving filter data')
	filter.save(index=False)
	return filter


def make_folders():
	folders:List[str] = [
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_CLEAN),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_FILTER),
		get_env_val_safe(EnvFields.DIR_RANKING_DATASETS)
	]
	for folder in folders:
		_logger.info(f'try-create folder: {folder}')
		Path(folder).mkdir(mode=0o775, parents=False, exist_ok=True)

def get_filtered_data():
	files:List[str] = [
		get_env_val_safe(EnvFields.CSV_RANKING_CLEAN),
		get_env_val_safe(EnvFields.CSV_RANKING_FILTER),
		get_env_val_safe(EnvFields.CSV_RANKINGS_PREFILTER),		
	]
	prefilter_clean_filter_data:bool = False
	for file in files:
		if not Path(file).exists():
			prefilter_clean_filter_data = True
			break
	filter:UserListFilter
	if prefilter_clean_filter_data:
		filter = _generate_datasets()
	else:
		filter = UserListFilter(frame=None)
	return filter
# cannot use scikit-surprise on the the barc pc....
from sklearn.decomposition import TruncatedSVD
# from scipy.sparse import linalg
from numpy import linalg
import numpy as np
def run():
	_logger.info('Begin.')
	make_folders()
	filter = get_filtered_data()

	'''
	# SVD: https://towardsdatascience.com/predict-ratings-with-svd-in-collaborative-filtering-recommendation-system-733aaa768b14/
		1. transform data
		2. calc sim
		3. det k
		4. conv original svd to k dim
		5. validate by top-k recs
	# See also: https://github.com/Chhaviroy/movie-recommendation-system-svd/blob/main/22_movierecommendationsystemusingsvd.py
	'''
	# Dataset: Rows=User, Columns=Content, Cells=Ratings
	sw = Stopwatch()
	cbf:UserContentScore
	if not UserContentScore.default_path.exists():
		_logger.info('generating content collab frame')
		cbf = UserContentScore.from_filter(filter=None)
		# Saving takes far longer than just generating it....
		# sw.start()
		# cbf.save(index=False)
		# sw.end()
		_logger.info(f'saving the cbf took {str(sw)}')
	else:
		_logger.info('loading content collab frame from file')
		sw.start()
		cbf = UserContentScore(frame=None)
		sw.end()
		_logger.info(f'loading the cbf took {str(sw)}')

	def euclidean_simularity(a,b):
		return 1.0/(1.0+linalg.norm(a-b))
	def get_k(sigma,percentage):
		''' The percenteage of the sum of squares of the first k singular values
		to the sum of squares of the total singular values.
		'''
		sigma_sqr = sigma**2
		sum_sigma_sqr=sum(sigma_sqr)
		k_sum_sigma=0
		k=0
		for i in sigma:
			k_sum_sigma+=i**2
			k+=1
			if k_sum_sigma>=sum_sigma_sqr*percentage:
				return k
	def svdEst(testdata:pd.DataFrame,user,simMeas,item,percentage):
		n=testdata.shape[1]
		sim_total=0.0
		rat_sim_total=0.0
		u,sigma,vt=linalg.svd(testdata, compute_uv=True)
		k = get_k(sigma,percentage)
		sigma_k = np.diag(sigma[:k])
		formed_items=np.around(
			np.dot(
				np.dot(u[:,:k], sigma_k),
				vt[:k,:]
			),
			decimals=3
		)
		for j in range(n):
			user_rating = testdata.loc[[user,j],UserRankingColumn.SCORE].iloc[0]
			if (user_rating == 0) or (j== item):
				continue
			similarity=simMeas(formed_items[item,:].T,formed_items[j,:].T)
			sim_total+=similarity
			rat_sim_total+=similarity*user_rating
		if sim_total==0:
			return 0
		else:
			return np.around(rat_sim_total/sim_total,decimals=3)
	def recommend(testdata:pd.DataFrame, user, sim_meas, est_method, percentage=0.9):
		unrated_items=np.nonzero(testdata[user,:]==0)[0].tolist()
		item_scores=[]
		if len(unrated_items)==0:
			_logger.info('SVD: all items rated')
			return item_scores
		else:
			_logger.info(f'svd: len(unrated_items): {len(unrated_items)}')
		for item in unrated_items:
			estimated_score = est_method(testdata,user,sim_meas,item,percentage)
			item_scores.append((item,estimated_score))
		item_scores=sorted(item_scores,key=lambda x:x[1], reverse=True)
		return item_scores
	result = recommend(cbf.get_frame(),0,sim_meas=euclidean_simularity, est_method=svdEst, percentage=0.90)
	_logger.info(f'recommend result: {result}')
	_logger.info('End.')
	return