import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple,List,Dict
import matplotlib.ticker as ticker
import numpy as np
from pandas.plotting import scatter_matrix;
from sklearn.manifold import TSNE
import seaborn as sns

dataset = pd.read_csv('TSNE_DATA.csv')
def plot_joint_grid(x_col:str,y_col:str):
	jg = sns.JointGrid(data=dataset,x=x_col,y=y_col)
	# jg.plot_joint(sns.kdeplot,bw_adjust=0.7,cut=1)
	jg.plot_joint(sns.scatterplot, data=dataset, alpha=0.5, palette=sns.color_palette("mako"))
	jg.plot_marginals(sns.kdeplot, data=dataset, hue='type', legend=True, bw_adjust=0.7,cut=2, palette=sns.color_palette("mako"))
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

print(dataset.info())
plot_joint_grid('tsne-2d-16-one','tsne-2d-16-two')
plot_joint_grid('tsne-2d-32-one','tsne-2d-32-two')
plot_joint_grid('tsne-2d-48-one','tsne-2d-48-two')
plot_joint_grid('tsne-2d-64-one','tsne-2d-64-two')
exit()