import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple,List,Dict
import matplotlib.ticker as ticker
import numpy as np
from pandas.plotting import scatter_matrix;
from sklearn.manifold import TSNE

import os
from dotenv import load_dotenv, find_dotenv;
de_path = find_dotenv(filename='data.env', raise_error_if_not_found=True)
load_dotenv(de_path, override=True)

mal_data_folder = os.getenv('MAL_DATA_FOLDER','')
print(mal_data_folder)

data_ranking_info = os.getenv('MAL_RANKING_LIST','')
print(data_ranking_info)

data_user_info = os.getenv('MAL_USER_LIST','')
print(data_user_info)

data_anime_info:str = os.getenv('MAL_ANIME_LIST','')
print(data_anime_info)

figures_filter_results = '10 CP1 Data Cleaning/filter_results'
figures_clean_results = '10 CP1 Data Cleaning/clean_results'

DEFAULT_FIGURE_SIZE=(5,5)
DEFAULT_FIGURE_DPI=300
ROWS_TO_READ:int|None = None

dataset = pd.read_csv(filepath_or_buffer='10 CP1 Data Cleaning/AnimeList_filtered_cleaned.csv')
print(dataset.info())
print(dataset.describe())

from sklearn.decomposition import PCA
import seaborn as sns

# correlation = dataset.corr(numeric_only=True)
# fig,ax = plt.subplots(dpi=DEFAULT_FIGURE_DPI)
# scatter_matrix(dataset[['score','members','favorites']],ax=ax,figsize=DEFAULT_FIGURE_SIZE)

dataset['fav_per_members'] = dataset['favorites'] / (dataset['members']/100)

def plot_joint_grid(x_col:str,y_col:str):
	jg = sns.JointGrid(data=dataset,x=x_col,y=y_col)
	jg.plot_joint(sns.kdeplot,bw_adjust=1,cut=1)
	jg.plot_marginals(sns.kdeplot, data=dataset, hue='type', legend=True, bw_adjust=0.7,cut=2)
	legend = jg.ax_marg_x.get_legend()
	leg_y = jg.ax_marg_y.get_legend()
	if leg_y is not None:
		leg_y.remove()
	if legend is not None:
		handles, labels = legend.legend_handles, [t.get_text() for t in legend.get_texts()]
		if handles is not None:
			legend.remove()
			jg.ax_joint.legend(handles,labels, loc='upper right', frameon=True)
	jg.set_axis_labels(xlabel=x_col,ylabel=y_col)
	jg.figure.suptitle(t='{} by {} KDE'.format(x_col,y_col), y=0.995)
	jg.figure.subplots_adjust(top=0.98, left=0.16)
	return jg

def create_figure_four():
	jg = plot_joint_grid('score','members')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.1,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	return jg

def create_figure_five():
	jg = plot_joint_grid('score','fav_per_members')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.15,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	jg.figure.suptitle('Score, Favorites per Hundred Members')
	return jg

def create_figure_six():
	jg = plot_joint_grid('members','favorites')
	low,high=jg.ax_joint.get_ylim()
	jg.ax_joint.set_ylim(low*0.15,high*0.24)
	jg.ax_joint.set_xlim(0,10)
	return jg
# sns_fig4 = create_figure_four()
# sns_fig4.figure.set_size_inches(DEFAULT_FIGURE_SIZE[0],DEFAULT_FIGURE_SIZE[1])
# sns_fig4.figure.set_dpi(DEFAULT_FIGURE_DPI)
# sns_fig4.savefig('Figure 4 - Score by Members KDE plots.tiff')


# f5 = create_figure_five()
# f5.savefig('Figure 5 - Score by Favorites per Hundred Members.tiff')

# f6 = create_figure_six()
# print(dataset.corr(numeric_only=True))
# from sklearn.decomposition import PCA
# pca = PCA(n_components=1)
# pca.fit(dataset[['favorites','members']])
# print(pca.get_covariance())
# print(pca.get_params())


def graph_set_two():
	graph_args:List[Tuple[str,str|None,bool,str|None]] = [
		# ('fav_per_members', None, False, 'fav_per_members'), 
		# ('members_per_fav', None, False, 'members_per_fav'), 
		# ('fav_per_members', 'score', False, 'fav_per_members x score'), 
		# ('members_per_fav', 'score', False, 'members_per_fav x score'), 
		
		# Compare
		('score', None, False, 'Score'), 
		('score', None, True, 'Score by Type'),
		# # ------------
		
		# # Mention
		('members', None, True, 'Members by Type'),
		('favorites', None, False, 'Favorites'),
		# # ------------

		# # Compare
		# ('score', 'favorites', True, 'Score, Favorites by Type'),
		# ('score', 'favorites', False, 'Score by Favorites'),
		# ------------
		
		# Compare
		# ('score', 'members', False, 'Score by Members'), # Figure 4 done with joint grid
		# ('score', 'members', True, 'Score, Members by Type'), # Bad.
		# ------------
		# ('members', 'favorites', False), # Bad.
		# ('members', None, False), # Bad.
		# ('favorites', None, True), # Bad.
		# ('members', 'favorites', True), # Bad.
	]
	for args in graph_args:
		f,ax = plt.subplots()
		kde = sns.kdeplot(data=dataset,
			x=args[0], y=args[1],
			hue='type' if args[2] else None,
			ax=ax
		)
		if (args[0] == 'score'): kde.set_xlim(0,10)
		if (args[1] == 'score'): kde.set_ylim(0,10)
		if args[3] is not None: kde.set(title=args[3])
	# - SCORE by FAVORITES
	# - MEMBERS BY FAVORITES

	for label, data in subsets.items():
		snsp = sns.pairplot(data, corner=True)
		snsp.figure.suptitle('{}'.format(label))
# sns.pairplot(dataset[['score','members','favorites','type']], hue="type")

import time

tsne_df = dataset.copy()[['anime_id','genre','type']]
genre_cols = tsne_df['genre'].str.get_dummies(sep=',')
tsne_df.drop(columns=['genre'],inplace=True)
tsne_df = tsne_df.join(genre_cols)
nrows = tsne_df.shape[1]
data = tsne_df.drop(columns=['anime_id','type']).apply(pd.Series.value_counts)
data = data.transpose()
tsne_df.drop(columns=data.loc[(data[1]<nrows*0.05)].index, inplace=True)

def perform_tsne(perp=48, max_iter=5000, no_prog_iter=500):
	time_started = time.time()
	tsne_one:str = 'tsne-2d-{}-{}-x'.format(perp, max_iter)
	tsne_two:str = 'tsne-2d-{}-{}-y'.format(perp, max_iter)
	tsne = TSNE(perplexity=perp, max_iter=max_iter, n_iter_without_progress=no_prog_iter)
	tsne_res = tsne.fit_transform(tsne_df.drop(columns=['anime_id','type']))
	tsne_df[tsne_one] = tsne_res[:,0]
	tsne_df[tsne_two] = tsne_res[:,1]
	print('tsne P:{} completed in {} sec'.format(perp, time.time()-time_started))
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x=tsne_one, y=tsne_two,
		hue=tsne_two, style='type',
		data=tsne_df, legend='auto',alpha=0.7,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig('TSNE OF GENRES-5 p:{} i:{}.tiff'.format(perp, max_iter))
	print('saved as: TSNE OF GENRES p:{} i:{}.tiff'.format(perp,max_iter))

for i in [32,48,62]:
	perform_tsne(i, 2000)
tsne_df.to_csv('TSNE_DATA_trim_05.csv', index=False)

# genre_occurences = tsne_df.drop(columns=['anime_id','type'])
# genre_occurences = genre_occurences.transpose().dot(genre_occurences)
# genre_occurences.to_csv('occurences.csv')

correlation = tsne_df.drop(columns=['anime_id','type']).corr()
correlation.to_csv('genre_correlation.csv')

exit()