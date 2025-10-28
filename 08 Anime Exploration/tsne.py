import os
from dotenv import load_dotenv, find_dotenv;
from typing import Tuple,List
import matplotlib.pyplot as plt;
import pandas as pd
import networkx as nx
from sklearn.manifold import TSNE
import time
import seaborn as sns

find_dotenv(filename='data.env')
load_dotenv('data.env')
data_anime_info:str = os.getenv('MAL_ANIME_LIST','')
print(data_anime_info)

def get_genres_tables(nrows:int|None):
	select_columns:List[str] = [
		'anime_id',
		'title',
		'genre',
		'type',
	];
	frame:pd.DataFrame = pd.read_csv(data_anime_info, usecols=select_columns, nrows=nrows)
	genre_cols = frame['genre'].str.get_dummies(sep=',')
	frame.drop(columns=['genre'],inplace=True)
	frame = frame.join(genre_cols)

	data = frame.drop(columns=['title', 'anime_id','type']).apply(pd.Series.value_counts)
	data = data.transpose()
	if nrows is None: # get num rows
		nrows = frame.shape[0]
	print('SHAPE BEFORE PRUNING: {}'.format(frame.drop(columns=['title','anime_id','type']).shape))
	frame.drop(columns=data.loc[(data[1]<nrows*0.03) | (data[0]<nrows*0.03)].index, inplace=True)
	return frame

def save_tsne_labels(frame):
	frame['title'].to_csv('tsne_data_labels_title.csv',index=False)
	frame['anime_id'].to_csv('tsne_data_labels_id.csv',index=False)
	frame.drop(columns=['title','anime_id']).to_csv('tsne_data.csv',index=False)

def get_genre_occurences(frame)->pd.DataFrame:
	genres = frame.drop(columns=['anime_id','title'])
	genres = genres.reindex(sorted(genres.columns),axis=1)
	return genres.transpose().dot(genres)

# frame = for_online_tsne(512)
n = None
# occurences = get_genre_occurences(n)
# occurences.to_csv('occurences.csv')
df = get_genres_tables(n)
df.info()

save_tsne_labels(df)

def perform_tsne(perp=48, max_iter=5000, no_prog_iter=500):
	time_started = time.time()
	tsne_one:str = 'tsne-2d-{}-one'.format(perp)
	tsne_two:str = 'tsne-2d-{}-two'.format(perp)
	tsne = TSNE(perplexity=perp, max_iter=max_iter, n_iter_without_progress=no_prog_iter)
	tsne_res = tsne.fit_transform(df.drop(columns=['anime_id','title','type']))
	df[tsne_one] = tsne_res[:,0]
	df[tsne_two] = tsne_res[:,1]
	print('tsne P:{} completed in {} sec'.format(perp, time.time()-time_started))
	f,ax = plt.subplots()
	sns.scatterplot(ax=ax,
		x=tsne_one, y=tsne_two,
		hue=tsne_two, style='type',
		data=df, legend='auto',alpha=0.5,
		palette=sns.color_palette("mako", as_cmap=True)
	)
	f.set_size_inches(10,10)
	f.set_dpi(500)
	f.savefig('TSNE OF GENRES p:{}.tiff'.format(perp))

perform_tsne()

# # Graph genre to genre connections
# G = nx.Graph()
# G.add_nodes_from(list(occurences.columns))
# for idx in occurences.index:
# 	for col in occurences.columns:
# 		weight = occurences.loc[idx,col]
# 		if weight == 0:
# 			continue
# 		if idx == col:
# 			#just label the node differently?
# 			continue
# 		print('I: {} | C: {} | W: {}'.format(idx,col, weight))
# 		G.add_edge(idx,col,weight=weight)

# fig = plt.figure(figsize=(20,20))

# communities = nx.community.greedy_modularity_communities(G,weight='weight')
# supergraph = nx.cycle_graph(len(communities))
# superpos = nx.spring_layout(supergraph, scale=2, seed=429)

# centers = list(superpos.values())
# pos = {}
# for center, comm in zip(centers, communities):
#     pos.update(nx.spring_layout(nx.subgraph(G, comm), center=center, seed=1430))

# for nodes, clr in zip(communities, ("tab:blue", "tab:orange", "tab:green")):
#     nx.draw_networkx_nodes(G, pos=pos, nodelist=nodes, node_color=clr, node_size=100)
# nx.draw_networkx_edges(G, pos=pos)

# # pos = nx.spring_layout(G,k=0.25, seed=20)
# # nx.draw(
# # 	G, pos=pos,
# # 	with_labels=True,
# # 	font_weight='bold',
# # )
# # nx.draw_networkx_nodes(G,pos,node_size=1600)
# plt.title('network graph')
# # labels = nx.get_edge_attributes(G,'weight')
# # nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
# plt.show()
# fig.savefig('network_graph.jpg')

exit()