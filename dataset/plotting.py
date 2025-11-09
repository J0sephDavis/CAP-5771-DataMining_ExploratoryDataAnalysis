from .protocols import (
	DatasetProtocolFrame as _DatasetProtocolFrame,
)
from abc import (
	ABC as _ABC,
	abstractmethod as _abstractmethod,
)
from typing import (
	override as _override,
	Tuple as _Tuple,
	Any as _Any,
	Optional as _Optional,
)
import pandas as _pd
import time as _time
from sklearn.manifold import TSNE as _TSNE
import seaborn as _sns
from matplotlib.figure import Figure as _Figure
from matplotlib.axes import Axes as _Axes
import matplotlib.pyplot as _plt
from helpers.files import (
	should_continue_with_file as _should_continue_with_file,
)
from pathlib import Path as _Path
DEFAULT_FIGURE_SIZE=(10,10)
DEFAULT_FIGURE_DPI=500
ROWS_TO_READ:_Optional[int] = None
import logging as _logging
from helpers.context import APP_LOGGER_NAME as _APP_NAME
_logger = _logging.getLogger(f'{_APP_NAME}.dataset.plotting')

class PlotTSNE(_DatasetProtocolFrame):
	''' TSNE Plot. '''
	@_abstractmethod
	def plot_tsne_transform_data(self)->_pd.DataFrame:
		''' This should return the dataframe prepared for the plotting task. '''
		pass

	def plot_tsne(self,
		  		perplexity:int=48,
				max_iter:int=5000,
				no_progress_iter:int=500
			)->_Tuple[_pd.DataFrame,str,str]:
		''' Performs TSNE & returns the results.
		tsne_data: should be a copy of the data, containing all columns you want to process
		Returns the tsne_results, the name of the x column, the name of the y column.
		'''
		_logger.info('Plotting TSNE...')
		tsne_x_column:str = f'TSNE-X perp:{perplexity} max:{max_iter}'
		tsne_y_column:str = f'TSNE-Y perp:{perplexity} max:{max_iter}'

		time_started = _time.time()
		tsne = _TSNE(
			perplexity=perplexity,
			max_iter=max_iter,
			n_iter_without_progress=no_progress_iter
		)
		tsne_res = tsne.fit_transform(self.plot_tsne_transform_data())

		_logger.info('plot_tsne P:{} completed in {} sec'.format(perplexity, _time.time()-time_started))
		return (_pd.DataFrame(tsne_res, columns=[tsne_x_column, tsne_y_column]),
			tsne_x_column, tsne_y_column
		)
	

class PlotJointGridKDE(_DatasetProtocolFrame):
	''' KDE Joint Grid plot. '''
	@_abstractmethod
	def plot_jg_transform_data(self)->_pd.DataFrame:
		''' Transform the data, if needed, before JointGrid KDE plotting. '''
		pass

	def plot_jg(self,
				x_column:str,
				y_columns:str,
				hue_column:_Optional[str],
			)->_sns.JointGrid:
		''' Plots a KDE joint grid plot between x & y.
		- On the x and y axes, the KDE is done for each value.
		- The center of the graph is a the 2d KDE plot.
		'''
		DATA_FRAME = self.plot_jg_transform_data()
		jg = _sns.JointGrid(data=DATA_FRAME, x=x_column, y=y_columns)
		jg.plot_joint(_sns.kdeplot, bw_adjust=1, cut=1)
		jg.plot_marginals(
			_sns.kdeplot,
			data=DATA_FRAME,
			hue=hue_column,
			legend=True,
			bw_adjust=0.7,
			cut=2
		)
		legend = jg.ax_marg_x.get_legend()
		leg_y = jg.ax_marg_y.get_legend()
		if leg_y is not None:
			leg_y.remove()
		if legend is not None:
			handles, labels = legend.legend_handles, [t.get_text() for t in legend.get_texts()]
			if handles is not None:
				legend.remove()
				jg.ax_joint.legend(handles,labels, loc='upper right', frameon=True)
		jg.set_axis_labels(xlabel=x_column, ylabel=y_columns)
		jg.figure.suptitle(t='{} by {} KDE'.format(x_column,y_columns), y=0.995)
		jg.figure.subplots_adjust(top=0.98, left=0.16)
		jg.figure.set_size_inches(DEFAULT_FIGURE_SIZE)
		jg.figure.set_dpi(DEFAULT_FIGURE_DPI)
		_logger.info('plotted joint grid.')
		return jg
	
class PlotScatter(_DatasetProtocolFrame):
	@_abstractmethod
	def plot_scatter_transform_data(self)->_pd.DataFrame:
		pass

	def plot_scatter(self,
			data:_pd.DataFrame,
			x_column:str,
			y_column:str,
			file_name:_Path,
			hue_column:_Optional[str]=None,
			style_column:_Optional[str] = None,
			clobber:bool=False,
			raise_err_no_clob:bool=False,
			)->_Optional[_Tuple[_Figure,_Axes]]:
		''' Plots scatterplot and returns None or figures,axes'''
		_logger.info('Plotting scatter')
		should_cont = _should_continue_with_file(
			filename=file_name, clobber=True, raise_exception=True
		)
		if not should_cont:
			_logger.warning(f'TSNE not plotted {file_name} already exists.')
			return None
		f,ax = _plt.subplots()
		scatter = _sns.scatterplot(ax=ax,
			x=x_column, y=y_column,
			hue=hue_column, style=style_column,
			data=data, legend='auto',alpha=0.7,
			palette=_sns.color_palette("mako", as_cmap=True)
		)
		f.set_size_inches(DEFAULT_FIGURE_SIZE)
		f.set_dpi(DEFAULT_FIGURE_DPI)
		f.savefig(file_name)
		_logger.info(f'plot_scatter, TODO: saving figure should be callers responsibility. Saved figure: {file_name}')
		return (f,ax)