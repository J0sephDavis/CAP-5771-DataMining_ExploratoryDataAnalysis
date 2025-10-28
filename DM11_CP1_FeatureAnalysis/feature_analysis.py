from helpers.context import todays_date_iso8601
from helpers import plotting, context, files
import pandas as pd
import os
from sklearn.decomposition import PCA
from pathlib import Path
from typing import List

dotenv_found, dotenv_path = context.load_find_env()
clean_folder:Path = Path(f'13 CP1 - Feature Analysis')

# TSNE
def create_genres_frame(dataset:pd.DataFrame)->pd.DataFrame:
	''' Takes genres & types from the dataset. Splits genres into binary vectors. '''
	tsne_df = dataset[['genre']]
	tsne_df = tsne_df['genre'].str.get_dummies(sep=',')
	# Remove genres which are seen <5% of the time across the dataset.
	nrows = tsne_df.shape[1]
	genre_counts = tsne_df.apply(pd.Series.value_counts)
	genre_counts = genre_counts.transpose()
	tsne_df.drop(columns=genre_counts.loc[(genre_counts[1]<nrows*0.05)].index, inplace=True)
	return tsne_df

def multiple_tsne_plots(dataset:pd.DataFrame, perplexities:List[int] = [32,48,64])->pd.DataFrame:
	''' Performs TSNE on perplexities and returns dataset.'''
	tsne_dataframe = create_genres_frame(dataset.copy())
	for p in perplexities:
		max_iter:int = 5000
		tsne_data, x_name, y_name = plotting.perform_tsne(
			tsne_data=tsne_dataframe,
			perplexity=p, max_iter=max_iter
		)
		filename:str = f'TSNE perplexity:{p} max_iterations:{max_iter}.tiff'
		dataset = dataset.merge(tsne_data, left_index=True, right_index=True)
		plotting.scatter(
			data=dataset, file_name=filename,
			x=x_name,y=y_name,
			hue=y_name, style='type'
	)
	return dataset

# KDE Figures
def fig_score_mem(dataset:pd.DataFrame, filename:str, clobber:bool=False):
	''' KDE of score by member'''
	should_save, already_exists = files.should_continue_with_file(filename, clobber, False)
	if not should_save:
		return
	jg = plotting.joint_grid(dataset=dataset, x='score',y='members', hue='type')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.1,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	jg.savefig(filename)
	return jg

def figure_kde_score_fpm(dataset:pd.DataFrame, filename:str, clobber:bool=False):
	''' KDE of score by favorites per hundred members '''
	should_save, already_exists = files.should_continue_with_file(filename, clobber, False)
	if not should_save:
		return
	jg = plotting.joint_grid(dataset=dataset, x='score',y='fav_per_members', hue='type')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.15,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	jg.figure.suptitle('Score, Favorites per Hundred Members')
	jg.savefig(filename)
	return jg

def figure_mem_fav(dataset:pd.DataFrame, filename:str, clobber:bool=False):
	''' KDE of members by favorites '''
	should_save, already_exists = files.should_continue_with_file(filename, clobber, False)
	if not should_save:
		return
	jg = plotting.joint_grid(dataset=dataset, x='members',y='favorites', hue='type')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.15,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	jg.savefig(filename)
	return jg

def plot_results(generate_kde_graphs:bool=True, generate_TSNE:bool=True):
	clean_data = pd.read_csv(
		'10 CP1 Data Cleaning/AnimeList_filtered_cleaned.csv'
	)
	clean_data['fav_per_members'] = clean_data['favorites'] / (clean_data['members']/100)
	print(clean_data.info())
	print(clean_data.describe())
	if generate_kde_graphs:
		figures_CLEAN = Path(f'{clean_folder}/figures')
		figures_CLEAN.mkdir(mode=0o755,parents=True,exist_ok=True)
		f4 = fig_score_mem(
			dataset=clean_data,
			filename=f'{figures_CLEAN}{os.sep}Figure 4 - KDE Score by Members.tiff'
		)
		f5 = figure_kde_score_fpm(
			dataset=clean_data,
			filename=f'{figures_CLEAN}{os.sep}Figure 5 - KDE Favorites per Hundred Mem by Score.tiff'
		)
		f6 = figure_mem_fav(
			dataset=clean_data,
			filename=f'{figures_CLEAN}{os.sep}Figure 6 - KDE Members by Favorites.tiff'
		)
	if generate_TSNE:
		data_CLEAN = Path(f'{clean_folder}/data')
		data_CLEAN.mkdir(mode=0o755,parents=True,exist_ok=True)
		dataset_with_tsne = multiple_tsne_plots(clean_data)
		dataset_with_tsne.to_csv(f'{data_CLEAN}{os.sep}{todays_date_iso8601()} Genre TSNE.csv', index=False)
	return
plot_results(True,True)
# def plot_filtered_results(generate_kde_graphs:bool=True, generate_TSNE:bool=False):
# 	filter_data = pd.read_csv(
# 		'10 CP1 Data Cleaning/AnimeList_filtered_cleaned.csv'
# 	)
# 	filter_data['fav_per_members'] = filter_data['favorites'] / (filter_data['members']/100)
# 	print(filter_data.info())
# 	print(filter_data.describe())
# 	if generate_kde_graphs:
# 		figures_FILTER = Path(f'{filter_folder}/figures_FILTER')
# 		figures_FILTER.mkdir(mode=771,parents=True,exist_ok=True)
# 		f4 = fig_score_mem(
# 			dataset=filter_data,
# 			filename=f'{figures_FILTER}{os.sep}Figure 4 - KDE Score by Members.tiff'
# 		)
# 		f5 = figure_kde_score_fpm(
# 			dataset=filter_data,
# 			filename=f'{figures_FILTER}{os.sep}Figure 5 - KDE Favorites per Hundred Mem by Score.tiff'
# 		)
# 		f6 = figure_mem_fav(
# 			dataset=filter_data,
# 			filename=f'{figures_FILTER}{os.sep}Figure 6 - KDE Members by Favorites.tiff'
# 		)
# 	if generate_TSNE:
# 		data_FILTER = Path(f'{clean_folder}/data_FILTER')
# 		data_FILTER.mkdir(mode=771,parents=True,exist_ok=True)
# 		dataset_with_tsne = multiple_tsne_plots(filter_data)
# 		dataset_with_tsne.to_csv(f'{data_FILTER}{os.sep}{todays_date_iso8601()} Genre TSNE.csv', index=False)
# 	return

# def pca_of_fav_mem(dataset:pd.DataFrame):
# 	# print(dataset.corr(numeric_only=True))
# 	pca = PCA(n_components=1)
# 	pca.fit(dataset[['favorites','members']])
# 	print(pca.get_covariance())
# 	print(pca.get_params())
# 	return pca

# def graph_set_two():
# 	graph_args:List[Tuple[str,str|None,bool,str|None]] = [
# 		# ('fav_per_members', None, False, 'fav_per_members'), 
# 		# ('members_per_fav', None, False, 'members_per_fav'), 
# 		# ('fav_per_members', 'score', False, 'fav_per_members x score'), 
# 		# ('members_per_fav', 'score', False, 'members_per_fav x score'), 
		
# 		# Compare
# 		('score', None, False, 'Score'), 
# 		('score', None, True, 'Score by Type'),
# 		# # ------------
		
# 		# # Mention
# 		('members', None, True, 'Members by Type'),
# 		('favorites', None, False, 'Favorites'),
# 		# # ------------

# 		# # Compare
# 		# ('score', 'favorites', True, 'Score, Favorites by Type'),
# 		# ('score', 'favorites', False, 'Score by Favorites'),
# 		# ------------
		
# 		# Compare
# 		# ('score', 'members', False, 'Score by Members'), # Figure 4 done with joint grid
# 		# ('score', 'members', True, 'Score, Members by Type'), # Bad.
# 		# ------------
# 		# ('members', 'favorites', False), # Bad.
# 		# ('members', None, False), # Bad.
# 		# ('favorites', None, True), # Bad.
# 		# ('members', 'favorites', True), # Bad.
# 	]
# 	for args in graph_args:
# 		f,ax = plt.subplots()
# 		kde = sns.kdeplot(data=dataset,
# 			x=args[0], y=args[1],
# 			hue='type' if args[2] else None,
# 			ax=ax
# 		)
# 		if (args[0] == 'score'): kde.set_xlim(0,10)
# 		if (args[1] == 'score'): kde.set_ylim(0,10)
# 		if args[3] is not None: kde.set(title=args[3])
# 	# - SCORE by FAVORITES
# 	# - MEMBERS BY FAVORITES

# 	for label, data in subsets.items():
# 		snsp = sns.pairplot(data, corner=True)
# 		snsp.figure.suptitle('{}'.format(label))
# # sns.pairplot(dataset[['score','members','favorites','type']], hue="type")


# genre_occurences = tsne_df.drop(columns=['anime_id','type'])
# genre_occurences = genre_occurences.transpose().dot(genre_occurences)
# genre_occurences.to_csv('occurences.csv')

# correlation = tsne_df.drop(columns=['anime_id','type']).corr()
# correlation.to_csv('genre_correlation.csv')

# correlation = dataset.corr(numeric_only=True)
# fig,ax = plt.subplots(dpi=DEFAULT_FIGURE_DPI)
# scatter_matrix(dataset[['score','members','favorites']],ax=ax,figsize=DEFAULT_FIGURE_SIZE)