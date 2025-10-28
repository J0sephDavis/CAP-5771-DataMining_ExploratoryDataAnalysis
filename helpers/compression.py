import tarfile
import os
import datetime
from pathlib import Path
from typing import List
def save_files_to_tar(name_infix:str, working_directory:str, globs:List[str], delete_source_files:bool=False, clobber:bool=False):
	''' Adds all files from glob to a tar file, with the {name} value appended to the ISO8601 date, and saved in the save_to_path folder.'''
	file_path:Path = Path(f'{datetime.datetime.now().strftime(r'%Y-%m-%d')} - {name_infix}.tar.lzma')
	print(f'TAR FILE: {file_path}')
	if file_path.exists():
		if clobber:
			print('File already eixsts, deleting.')
			file_path.unlink()
			if file_path.exists():
				raise Exception('failed to delete file')
		else:
			raise Exception('File already exists. Specify clobber=True if you do not care.')
	
	files:List[Path] = []
	with tarfile.open(name=file_path, mode='w:xz') as tar:
		load_path = Path(working_directory)
		for glob in globs:
			for p in load_path.glob(glob):
				file = Path(p)
				if not file.is_file():
					continue
				if file in files:
					continue
				print(f'Adding file: {file}')
				tar.add(file,arcname=file.name)
				files.append(file)
	
	if not delete_source_files:
		return
	for file in files:
		print(f'Deleting file: {file}')
		file.unlink()

if __name__ == '__main__':
	name='TSNE OF GENRES - Checkpoint 1'
	sp=os.getcwd()
	lp=os.getcwd()
	globs=['*TSNE*.csv', '*TSNE*.tiff']
	save_files_to_tar(name,lp,globs,delete_source_files=True, clobber=False)