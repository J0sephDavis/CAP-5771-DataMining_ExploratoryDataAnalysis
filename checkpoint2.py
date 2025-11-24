from typing import Dict
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
	StatusEnum
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
from dataset.plotting import DEFAULT_FIGURE_DPI, DEFAULT_FIGURE_SIZE
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

def comparison_barchart(
		filtered_frame:pd.DataFrame,
		removed_frame:pd.DataFrame,
		figure_dpi=DEFAULT_FIGURE_DPI,
		**matplot_kwargs
	)->Tuple[Figure, Axes]:
	""" Stacked barchart showing removed vs remaining records """
	_logger.info('comparison_barchart_by_type')
	matplot_kwargs.setdefault('figsize',DEFAULT_FIGURE_SIZE)

	leftover = filtered_frame.shape[0]
	leftover_name='Leftover'
	removed = removed_frame.shape[0]
	removed_name = 'Removed'
	_logger.info(f'removed:\n{removed}')
	_logger.info(f'leftover:\n{leftover}')
	
	total_records = (leftover + removed)
	float_removed = removed / total_records
	_logger.info('total records: {}'.format(total_records))
	_logger.info('total_left: {}'.format(leftover))
	_logger.info('total_removed: {}'.format(removed))
	_logger.info('float_removed: {}'.format(float_removed))
	figure,axes = plt.subplots(dpi=figure_dpi)
	tdf = pd.DataFrame(
		[
			[leftover,removed]
		],columns=[leftover_name,removed_name]
	)
	tdf.plot(ax=axes, kind='bar',stacked=True, rot=0, **matplot_kwargs)
	axes.set_xlabel('')
	return figure,axes

def _generate_datasets(plot_comparisons:bool=False)->UserListFilter:
	''' Just fetches & saves dependent data if we need it. Returns the filtered list. '''
	generate_prefilter:bool = not UserListPreFilter.default_path.exists()
	generate_clean:bool = generate_prefilter or not UserListClean.default_path.exists()
	generate_filter:bool = generate_clean or not UserListFilter.default_path.exists()
	
	fig_dir = Path(get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS))

	sw = Stopwatch()
	pref:UserListPreFilter
	if plot_comparisons or generate_prefilter:
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

		fig,ax = comparison_barchart(filtered_frame=pref.get_frame(), removed_frame=prefo.get_frame())
		fig.savefig(fig_dir.joinpath('00 prefilter removed.tiff'))
		plt.close(fig=fig)
		del user_rankings
		gc.collect()
	elif generate_clean:
		pref = UserListPreFilter(frame=None)
	else:
		pref = None #  bs value to satisfy typesetter.
	
	clean:UserListClean
	if plot_comparisons or generate_clean:
		_logger.info('Perform cleaning on prefiltered data...')
		sw.start()
		clean, cleanedOut = UserListClean.clean_rankings(ranking=pref)
		sw.end()
		_logger.info(f'Cleaning(2) took: {str(sw)}')
		
		_logger.info('saving prefilter data')
		pref.save(index=False)
		fig,ax = comparison_barchart(filtered_frame=clean.get_frame(), removed_frame=cleanedOut.get_frame())
		fig.savefig(fig_dir.joinpath('01 clean removed.tiff'))
		plt.close(fig=fig)
		del pref
		gc.collect()
	elif generate_filter:
		clean = UserListClean(frame=None)
	else:
		clean = None # bs value to satisfy typesetter
	
	filter:UserListFilter
	if plot_comparisons or generate_filter:
		_logger.info('Perform filtering on cleaned data...')
		sw.start()
		filter, filteredOut = UserListFilter.filter_rankings(cleaned_rankings=clean)
		sw.end()
		_logger.info(f'Filtering(3) took: {str(sw)}')
		
		_logger.info('saving clean data')
		clean.save(index=False)
		fig,ax = comparison_barchart(filtered_frame=filter.get_frame(), removed_frame=filteredOut.get_frame())
		fig.savefig(fig_dir.joinpath('02 filter removed.tiff'))
		plt.close(fig=fig)
		del clean
		gc.collect()
	else:
		filter = UserListFilter(frame=None)
	
	_logger.info('saving filter data')
	filter.save(index=False)
	return filter

def get_filtered_data():
	''' returns the filter dataset if it needs to be fetched. Might be redundant but I no longer care.'''
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
# from sklearn.decomposition import TruncatedSVD
from scipy.sparse import linalg as sparse_linalg
from numpy import linalg
# from numpy import linalg
import numpy as np
from scipy.sparse import csr_matrix
import seaborn as sns

def init_folders():
	''' Call to create folders needed by this program. '''
	folders:List[str] = [
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_CLEAN),
		get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS_FILTER),
		get_env_val_safe(EnvFields.DIR_RANKING_DATASETS)
	]
	for folder in folders:
		_logger.info(f'try-create folder: {folder}')
		Path(folder).mkdir(mode=0o775, parents=False, exist_ok=True)
	return

def do_animelist_umap():
	''' Call to generate the UMAP of the anime list genres.
	Professor asked for this during checkpoint 1'''
	_logger.debug('do_animelist_umap')
	anime_list = AnimeListClean()
	result_data,x_col,y_col = anime_list.plot_umap(n_neighbors=48)
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x=x_col, y=y_col,
		hue=y_col, style=AnimeListColumns.TYPE,
		data=result_data, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig('AnimeList Genre UMAP neighbors:48.tiff')
	pass

def do_animelist_tsne():
	''' Call to generate the TSNE of the aniem list genres. For comparison to UMAP results.'''
	_logger.debug('do_animelist_tsne')
	anime_list = AnimeListClean()
	result_data,x_col,y_col = anime_list.plot_tsne()
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x=x_col, y=y_col,
		hue=y_col, style=AnimeListColumns.TYPE,
		data=result_data, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig('AnimeList Genre TSNE perplexity:48.tiff')
	pass

def do_svd():
	raise NotImplementedError('give up')
	sw = Stopwatch()
	filter = get_filtered_data()
	_logger.debug('do_svd')
	''' SVD:
	1. Decompose matrix X into U S V^T
		- U: Left Singular Vectors
		- S: Sigma, Singular Values - A diagonal matrix
		- V: Right Singular Vectors
	'''
	'''
	# SVD: https://towardsdatascience.com/predict-ratings-with-svd-in-collaborative-filtering-recommendation-system-733aaa768b14/
		1. transform data
		2. calc sim
		3. det k
		4. conv original svd to k dim
		5. validate by top-k recs
	# See also: https://github.com/Chhaviroy/movie-recommendation-system-svd/blob/main/22_movierecommendationsystemusingsvd.py
	# See: https://blog.csdn.net/weixin_41988628/article/details/83217255
	'''

	filter.frame = filter.get_frame().sample(n=100000)
	cbf = UserContentScore(filter=filter)
	def euclidean_simularity(a,b):
		return 1.0/(1.0+linalg.norm(a-b))
	
	def get_k(sigma,percentage):
		''' The percenteage of the sum of squares of the first k singular values
		to the sum of squares of the total singular values.
		'''
		_logger.debug(f'get_k(sigma:{sigma} percentage:{percentage})')
		sigma_sqr = sigma**2
		_logger.debug(f'sigma_sqr:{sigma_sqr}')
		sum_sigma_sqr=sum(sigma_sqr)
		_logger.debug(f'sum_sigma_sqr:{sum_sigma_sqr}')
		k_sum_sigma=0
		k=0
		for i in sigma:
			k_sum_sigma+=i**2
			k+=1
			_logger.debug(f'k_sum_sigma,k: ({k_sum_sigma},{k})')
			if k_sum_sigma>=sum_sigma_sqr*percentage:
				_logger.debug(f'k_sum_sigma > sum_sigma_sqr *percentage ({k_sum_sigma}>{sum_sigma_sqr*percentage})')
				return k
	
	def svdEst(testdata:csr_matrix,user,simMeas,item,percentage):
		_logger.debug(f'svdEst user:{user} item:{item} percentage:{percentage}')
		n=testdata.get_shape()[1]
		sim_total=0.0
		rat_sim_total=0.0
		m = testdata.get_shape()[0]
		max_k=min(n,m,15)-1 # Cannot allocate 532 GiB lol
		_logger.debug(f'max_k = {max_k}')
		u,sigma,vt=sparse_linalg.svds(testdata,k=max_k)
		
		k = get_k(sigma,percentage)
		_logger.info(f'k should be.. {k}')
		
		if u is None or vt is None:
			raise Exception('')
		
		sigma_k = np.diag(sigma[:k])
		formed_items=np.around(
			np.dot(
				np.dot(u[:,:k], sigma_k),
				vt[:k,:]
			),
			decimals=3
		)
		for j in range(n):
			user_rating = testdata[user,j]
			if (user_rating == 0) or (j== item):
				continue
			similarity=simMeas(formed_items[item,:].T,formed_items[j,:].T)
			sim_total+=similarity
			rat_sim_total+=similarity*user_rating
		if sim_total==0:
			return 0
		else:
			return np.around(rat_sim_total/sim_total,decimals=3)
	
	def recommend(testdata:csr_matrix, user, sim_meas, est_method, percentage=0.9):
		_logger.debug('recommend')
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
	result = recommend(cbf.get_matrix(),user=cbf.username_codes.codes[0],sim_meas=euclidean_simularity, est_method=svdEst, percentage=0.90)
	_logger.info(f'recommend result: {result}')
	return

import networkx as nx
import numpy as np
from community import community_louvain,partition_at_level

def _create_adjacency_matrix():
	_logger.info('create_adjacency matrix?')
	cleaned_data = UserListClean(frame=None)
	df = cleaned_data.get_frame()
	selected_columns = [
		UserRankingColumn.USERNAME,
		UserRankingColumn.ANIME_ID,
	]
	remove_cols = []
	for col in df.columns:
		if col not in selected_columns:
			remove_cols.append(col)
	df.drop(columns=remove_cols,inplace=True)
	df.dropna(inplace=True,how='any')
	
	del cleaned_data
	gc.collect()
	_logger.debug('create factorize values')
	user_id,user_uniques = pd.factorize(df[UserRankingColumn.USERNAME])
	content_id,content_uniques = pd.factorize(df[UserRankingColumn.ANIME_ID])
	_logger.debug('create sparse matrix')
	x=csr_matrix(
		(np.ones(len(user_id)),(user_id,content_id)), shape=(len(user_uniques),len(content_uniques))
	)
	_logger.info('generating content-content sparse matrix')
	content_content = x.T @ x
	_logger.info('creating graph')
	G_c2c:nx.Graph = nx.from_scipy_sparse_array(content_content)
	# graph_partitions = community_louvain.best_partition(G_c2c)
	_logger.info('generating dendrogram')
	dendrogram_dictionary = community_louvain.generate_dendrogram(graph=G_c2c)
	_logger.debug('dendrogram_dictionary:')
	_logger.debug(f'{dendrogram_dictionary}')
	partition = partition_at_level(dendrogram_dictionary,level=0)
	nx.draw_networkx(
		G=G_c2c,
		pos=nx.spring_layout(
			G_c2c,
			seed=42
		),
		node_color=[partition[n] for n in G_c2c.nodes],
		node_size=100,
		cmap = plt.cm.get_cmap('tab10'),
		with_labels=False
	)
	plt.show()
	
	return
def create_networks():
	_logger.info('creating network graphs.')
	matrix = _create_adjacency_matrix()
	G = nx.Graph() # Undirected graph
	pass

status_remapper:Dict[int,str] = {
	StatusEnum.COMPLETED.value:StatusEnum.COMPLETED.name,
	StatusEnum.DROPPED.value:StatusEnum.DROPPED.name,
	StatusEnum.ON_HOLD.value:StatusEnum.ON_HOLD.name,
	StatusEnum.PLAN_TO_WATCH.value:StatusEnum.PLAN_TO_WATCH.name,
	StatusEnum.WATCHING.value:StatusEnum.WATCHING.name,
}

def _save_fig(fig:Figure, filename:str):
	folder = Path(get_env_val_safe(EnvFields.DIR_FIGURES_RANKINGS))
	fig.set_size_inches(DEFAULT_FIGURE_SIZE)
	fig.set_dpi(DEFAULT_FIGURE_DPI)
	fig.savefig(folder.joinpath(filename))

def _plot_feature_distributions(ulc:UserListClean, exclude_zero:bool):
	''' boxplot of score grouped by status'''
	frame = ulc.get_frame().copy()
	fig,ax = plt.subplots()
	if exclude_zero:
		zer = frame.loc[frame[UserRankingColumn.SCORE]==0]
		frame.drop(inplace=True,index=zer.index)
	frame[UserRankingColumn.STATUS]=frame[UserRankingColumn.STATUS].map(status_remapper)
	frame.boxplot(by=UserRankingColumn.STATUS, column=UserRankingColumn.SCORE,ax=ax)
	title:str = f'Score distribution by status exclude zero:{exclude_zero}'
	ax.set_title(title)
	_save_fig(fig,f'ULC Boxplot {title}.tiff')
	plt.close(fig=fig)

def _plot_status_barchart(ulc:UserListClean):
	''' barchart of each status '''
	frame = ulc.get_frame().copy()
	count = frame[UserRankingColumn.STATUS].value_counts(ascending=False,sort=True)
	count.rename(index={
		StatusEnum.COMPLETED.value:StatusEnum.COMPLETED.name,
		StatusEnum.DROPPED.value:StatusEnum.DROPPED.name,
		StatusEnum.ON_HOLD.value:StatusEnum.ON_HOLD.name,
		StatusEnum.PLAN_TO_WATCH.value:StatusEnum.PLAN_TO_WATCH.name,
		StatusEnum.WATCHING.value:StatusEnum.WATCHING.name,
	}, inplace=True,errors='ignore')
	fig,ax = plt.subplots()
	count.plot(kind='bar', xlabel='status', rot=0)
	title:str = 'Status'
	ax.set_title(title)
	_save_fig(fig,f'ULC barchart {title}.tiff')
	plt.close(fig=fig)

def _plot_status_barchart_score_gte_5(ulc:UserListClean):
	''' barchart of status where score gte 5'''
	frame = ulc.get_frame().copy()
	score_lt5 = frame.loc[frame[UserRankingColumn.SCORE]<5]
	frame.drop(inplace=True, index=(score_lt5).index)

	count = frame[UserRankingColumn.STATUS].value_counts(ascending=False,sort=True)
	count.rename(index={
		StatusEnum.COMPLETED.value:StatusEnum.COMPLETED.name,
		StatusEnum.DROPPED.value:StatusEnum.DROPPED.name,
		StatusEnum.ON_HOLD.value:StatusEnum.ON_HOLD.name,
		StatusEnum.PLAN_TO_WATCH.value:StatusEnum.PLAN_TO_WATCH.name,
		StatusEnum.WATCHING.value:StatusEnum.WATCHING.name,
	}, inplace=True,errors='ignore')
	fig,ax = plt.subplots()
	count.plot(kind='bar', xlabel='status', rot=0)

	title:str = 'Status where score_gte_5'
	ax.set_title(title)
	_save_fig(fig,f'ULC Barchart {title}.tiff')
	plt.close(fig=fig)

def _plot_status_barchart_score_lste_5(ulc:UserListClean,exclude_zero:bool):
	''' barchar of status with scores lte5 optionally exlcude zero'''
	frame = ulc.get_frame().copy()
	score_gt5 = frame.loc[frame[UserRankingColumn.SCORE]>5]
	frame.drop(inplace=True, index=(score_gt5).index)
	if exclude_zero:
		zer=frame.loc[frame[UserRankingColumn.SCORE]==0]
		frame.drop(inplace=True,index=zer.index)

	count = frame[UserRankingColumn.STATUS].value_counts(ascending=False,sort=True)
	count.rename(index={
		StatusEnum.COMPLETED.value:StatusEnum.COMPLETED.name,
		StatusEnum.DROPPED.value:StatusEnum.DROPPED.name,
		StatusEnum.ON_HOLD.value:StatusEnum.ON_HOLD.name,
		StatusEnum.PLAN_TO_WATCH.value:StatusEnum.PLAN_TO_WATCH.name,
		StatusEnum.WATCHING.value:StatusEnum.WATCHING.name,
	}, inplace=True,errors='ignore')
	fig,ax = plt.subplots()
	count.plot(kind='bar', xlabel='status', rot=0)
	title:str = f'Status where score_lte_5 excluding zero:{exclude_zero}'
	ax.set_title(title)
	_save_fig(fig,f'ULC Barchart {title}.tiff')
	plt.close(fig=fig)

def _plot_status_barchart_score_eq_0(ulc):
	''' barchar of status with scores eq 0. '''
	frame = ulc.get_frame().copy()
	non_zero=frame.loc[frame[UserRankingColumn.SCORE]!=0]
	frame.drop(inplace=True,index=non_zero.index)

	count = frame[UserRankingColumn.STATUS].value_counts(ascending=False,sort=True)
	count.rename(index={
		StatusEnum.COMPLETED.value:StatusEnum.COMPLETED.name,
		StatusEnum.DROPPED.value:StatusEnum.DROPPED.name,
		StatusEnum.ON_HOLD.value:StatusEnum.ON_HOLD.name,
		StatusEnum.PLAN_TO_WATCH.value:StatusEnum.PLAN_TO_WATCH.name,
		StatusEnum.WATCHING.value:StatusEnum.WATCHING.name,
	}, inplace=True,errors='ignore')
	fig,ax = plt.subplots()
	count.plot(kind='bar', xlabel='status', rot=0)
	title:str = 'Status where score eq 0'
	ax.set_title(title)
	_save_fig(fig,f'ULC Barchart {title}.tiff')
	plt.close(fig=fig)

def _plot_score_barchart(ulc:UserListClean):
	''' barchar of scores. '''
	frame = ulc.get_frame().copy()
	count = frame[UserRankingColumn.SCORE].value_counts(ascending=False,sort=True)
	fig,ax = plt.subplots()
	count.plot(kind='bar', xlabel='Score', rot=0)
	title:str = 'Score'
	ax.set_title(title)
	_save_fig(fig,f'ULC Barchart {title}.tiff')
	plt.close(fig=fig)

def plot_figs():
	ulc = UserListClean(frame=None, usecols=[UserRankingColumn.STATUS,UserRankingColumn.SCORE])
	# _plot_status_barchart(ulc)
	# _plot_feature_distributions(ulc,True)
	# _plot_feature_distributions(ulc,False)
	# _plot_status_barchart_score_gte_5(ulc)
	# _plot_status_barchart_score_lste_5(ulc,True)
	# _plot_status_barchart_score_lste_5(ulc,False)
	# _plot_status_barchart_score_eq_0(ulc)
	_plot_score_barchart(ulc)