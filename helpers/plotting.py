import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple,Optional
from pandas.plotting import scatter_matrix;
from sklearn.manifold import TSNE
import seaborn as sns
import time

DEFAULT_FIGURE_SIZE=(10,10)
DEFAULT_FIGURE_DPI=5000
ROWS_TO_READ:Optional[int] = None

def plot_joint_grid(dataset:pd.DataFrame, x_col:str,y_col:str, hue_column:str):
	''' Plots a KDE joint grid plot between x & y.
	- On the x and y axes, the KDE is done for each value.
	- The center of the graph is a the 2d KDE plot.
	'''
	jg = sns.JointGrid(data=dataset,x=x_col,y=y_col)
	jg.plot_joint(sns.kdeplot,bw_adjust=1,cut=1)
	jg.plot_marginals(sns.kdeplot, data=dataset, hue=hue_column, legend=True, bw_adjust=0.7,cut=2)
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
	jg.figure.set_size_inches(DEFAULT_FIGURE_SIZE)
	jg.figure.set_dpi(DEFAULT_FIGURE_DPI)
	return jg

def perform_tsne(
		tsne_data:pd.DataFrame,
		perplexity:int=48,max_iter:int=5000, no_progress_iter:int=500,
	)->Tuple[pd.DataFrame, str,str]:
	''' Performs TSNE & returns the results.
	tsne_data: should be a copy of the data, containing all columns you want to process
	Returns the tsne_results, the name of the x column, the name of the y column.
	'''
	time_started = time.time()
	tsne_x_column:str = f'TSNE-X perp:{perplexity} max:{max_iter}'
	tsne_y_column:str = f'TSNE-Y perp:{perplexity} max:{max_iter}'

	tsne = TSNE(perplexity=perplexity, max_iter=max_iter, n_iter_without_progress=no_progress_iter)
	tsne_res = tsne.fit_transform(tsne_data)
	print('tsne P:{} completed in {} sec'.format(perplexity, time.time()-time_started))
	
	return (pd.DataFrame(tsne_res, columns=[tsne_x_column, tsne_y_column]),
		tsne_x_column, tsne_y_column
	)

def scatter(
		data:pd.DataFrame, x:str, y:str, file_name:str,
		hue:Optional[str]=None, style:Optional[str] = None,
		figure_size:Tuple[int,int]=DEFAULT_FIGURE_SIZE, figure_dpi:int=DEFAULT_FIGURE_DPI
	):
	''' Plots scatterplot and returns None or figures,axes'''
	should_cont, already_exists = should_continue_with_file(
		filename=file_name, clobber=True, raise_exception=True
	)
	if not should_cont:
		print(f'TSNE not plotted {file_name} already exists.')
		return None
	f,ax = plt.subplots()
	scatter = sns.scatterplot(ax=ax,
		x=x, y=y,
		hue=hue, style=style,
		data=data, legend='auto',alpha=0.7,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(figure_size)
	f.set_dpi(figure_dpi)
	f.savefig(file_name)
	print(f'PLOT_TSNE, Saved figure: {file_name}')
	return (f,ax)