import tarfile
import os
from pathlib import Path
from typing import List
from .context import todays_date_iso8601
def save_files_to_tar(name_infix:str, name_prefix:str, working_directory:str, globs:List[str], delete_source_files:bool=False, clobber:bool=False):
	''' Adds all files from glob to a tar file, with the {name} value appended to the ISO8601 date, and saved in the save_to_path folder.
	name_infix:str - comes after the ISO datetime, but before the file extension. {date} - {name_infix}.tar.lzma
	name_prefix:str - comes before ISO datetime, use this to build relative paths. {name_prefix}{date}...
	globs:List[str] - A list of glob patterns. refer to pathlib.Path documentation
	working_directory:str - the path from which glob patterns are explored.
	delete_source_file:bool - After adding a file to the tarball, delete it.
	clobber:bool - if a tarfile already exists, delete it and write over it.
	'''
	file_path:Path = Path(f'{name_prefix}{todays_date_iso8601()} - {name_infix}.tar.lzma')
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
	name='Anime Exploration'
	globs=['*.csv', '*.jpg']
	directory = f'{os.getcwd()}{os.sep}08 Anime Exploration/'
	save_files_to_tar(
		name_infix = name, name_prefix = directory,
		working_directory = directory,
		globs = globs,
		delete_source_files=True, clobber=False
	)