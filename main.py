import os
from dotenv import load_dotenv, find_dotenv;
from typing import Tuple,List

def get_environment_variables()->Tuple[str,str,str,str]:
	find_dotenv(filename='data.env')
	load_dotenv('data.env')
	mal_data_folder = os.getenv('MAL_DATA_FOLDER','')
	print(mal_data_folder)
	data_ranking_info = os.getenv('MAL_RANKING_LIST','')
	print(data_ranking_info)
	data_user_info = os.getenv('MAL_USER_LIST','')
	print(data_user_info)
	data_anime_info:str = os.getenv('MAL_ANIME_LIST','')
	print(data_anime_info)
	return (mal_data_folder,data_ranking_info,data_user_info,data_anime_info)