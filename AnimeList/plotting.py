from helpers.plotting import DEFAULT_FIGURE_DPI, DEFAULT_FIGURE_SIZE
import pandas as pd
from typing import Tuple, List
import matplotlib.pyplot as plt
# # Plotting Functions
def barchart_by_type(frame:pd.DataFrame,
		figsize=DEFAULT_FIGURE_SIZE, figure_dpi=DEFAULT_FIGURE_DPI
	)->Tuple[plt.Figure, plt.Axes]:
	""" Plots the amount of entries by the categorical feature 'type'. Returns figure, axes """
	type_counts = frame['type'].value_counts()
	figure,axes = plt.subplots(dpi=figure_dpi)
	type_counts.plot.bar(ax=axes, figsize=figsize)
	axes.set_xlabel('Content Types')
	axes.set_ylabel('Count')
	axes.set_title('Entries by Content Type')
	return figure,axes

def boxplot_by_type(frame:pd.DataFrame,
		column:str, exclude_types:List[str]=[], sub_by:str|None = None,
		plot_overall:bool=False, plot_aggregate:bool=False, plot_all_except_include:bool=False,
		show_fliers:bool=True, show_mean:bool=True,
		figure_dpi:int = 300,
		**matplot_kwargs
	)->Tuple[plt.Figure,plt.Axes]:
	""" Plots the column by type. plot_overall shows the entire dataframes boxplot. plot_aggregate respects exclude_types """
	if not (column in frame.columns):
		raise KeyError('boxplot_by_type {} not found in frame.columns'.format(column))
	
	figure,axes = plt.subplots(dpi=figure_dpi)
	# Set the default figure size to 20in by 20in...
	# Set default width to 0.5 * width of graph (must be set to get them to auto adjust when plotting overall/aggregate)
	matplot_kwargs.setdefault('figsize',DEFAULT_FIGURE_SIZE)
	matplot_kwargs.setdefault('widths',0.5)

	FILTERED_FRAME = (frame[~frame['type'].isin(exclude_types)] if (len(exclude_types) != 0) else frame)
	FILTERED_FRAME.boxplot(
			column=[column],ax=axes,
			by='type' if sub_by is None  else ['type', sub_by],
			showfliers=show_fliers,
			showmeans=show_mean, meanline=show_mean,
			**matplot_kwargs
		)

	labels = [label.get_text() for label in axes.get_xticklabels()]
	def additional_plot(df:pd.DataFrame, label:str):
		df.boxplot(
			column=[column], ax=axes, by = (sub_by if sub_by is not None else None),
			showfliers=show_fliers,
			showmeans=show_mean, meanline=show_mean,
			positions=[len(labels)+1],
			**matplot_kwargs
		)
		labels.append(label)
		axes.set_xticklabels(labels)

	if plot_overall: # Insert the overall boxplot & correct xticklabels
		additional_plot(frame,'All')
	
	if plot_aggregate: # Insert the aggregate (of displayed data), correct xticklabels
		additional_plot(FILTERED_FRAME, 'Aggregate')
	
	if plot_all_except_include and len(exclude_types) != 0:
		additional_plot(frame[frame['type'].isin(exclude_types)],'Excluded')

	title:str = '{} by Content Type'.format(column)
	figure.suptitle('')
	axes.set_title(title)

	# sub_title:str = '({} {})'.format(
	# 	'Show Fliers' if show_fliers else 'Hide Fliers',
	# 	', Show Mean' if show_mean else ''
	# )
	# axes.set_title('')

	axes.set_xlabel('')
	axes.set_ylabel('')
	return figure,axes

def comparison_barchart_by_type(
		filtered_frame:pd.DataFrame,
		removed_frame:pd.DataFrame,
		figure_dpi=DEFAULT_FIGURE_DPI,
		**matplot_kwargs
	)->Tuple[plt.Figure, plt.Axes]:
	""" Stacked barchart showing removed vs remaining records """
	matplot_kwargs.setdefault('figsize',DEFAULT_FIGURE_SIZE)
	leftover = filtered_frame['type'].value_counts()
	print('leftover:')
	print(leftover)
	leftover.name='Leftover'

	removed = removed_frame['type'].value_counts()
	removed.name='Removed'
	print('removed:')
	print(removed)
	total_records = (leftover.sum() + removed.sum())
	total_left = leftover.sum()
	total_removed = removed.sum()
	float_removed = total_removed / total_records
	print('total records: {}'.format(total_records))
	print('total_left: {}'.format(total_left))
	print('total_removed: {}'.format(total_removed))
	print('float_removed: {}'.format(float_removed))
	figure,axes = plt.subplots(dpi=figure_dpi)
	tdf = pd.concat([leftover,removed],axis=1)
	tdf.plot(ax=axes, kind='bar',stacked=True, rot=0, **matplot_kwargs)
	axes.set_xlabel('')
	# axes.set_ylabel('Count')
	return figure,axes

# ------------------------------------------------------------------------------
def compare_by_label(
		comparison_frame:pd.DataFrame,
		column_label:str,
		figure_folder:str
	)->None:
	''' Given a dataframe where column label exists.
	- generate multiple boxplots describing the distribution shift
		with respect to several features.
	'''
	rotation=12
	# Compare each type before & after filtering. Score Distributions
	F02A, F02A_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['TV'],
		column='score',
		sub_by=column_label,
		rot=rotation
	)
	F02A.savefig('{}/F02A.tiff'.format(figure_folder))
	F02B, F02B_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='score',
		sub_by=column_label,
	)
	F02B.savefig('{}/F02B.tiff'.format(figure_folder))

	# Compare each type before & after filtering. Score Distributions
	F03A, F03A_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['TV'],
		column='members',
		sub_by=column_label,
		rot=rotation
	)
	F03A.savefig('{}/F03A.tiff'.format(figure_folder))
	F03B, F03B_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='members',
		sub_by=column_label,
	)
	F03B.savefig('{}/F03B.tiff'.format(figure_folder))

	# Compare each type before & after filtering. Score Distributions
	F04A, F04A_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['TV'],
		column='members',
		sub_by=column_label,
		show_fliers=False,
		rot=rotation
	)
	F04A.savefig('{}/F04A.tiff'.format(figure_folder))
	F04B, F04B_ax = boxplot_by_type(
		comparison_frame,
		exclude_types=['Movie','ONA','OVA','Special'],
		column='members',
		sub_by=column_label,
		show_fliers=False,
	)
	F04B.savefig('{}/F04B.tiff'.format(figure_folder))