import json
import os
import shutil
import re

STATIC_FOLDERS = ['css', 'images', 'js']
COMPONENTS_FOLDER_NAME = 'components'
COMPONENTS_HTML_FOLDER_NAME = 'html'
WEB_FOLDER_NAME = 'web'
WEB_JSON_FILE_NAME = 'web.json'

def create_folders_for_lans(lans):
	for lan in lans:
		dir = WEB_FOLDER_NAME + os.path.sep + lan
		if os.path.exists(dir):
			shutil.rmtree(dir)
		os.makedirs(dir)
		for folder in STATIC_FOLDERS:
			try:
				shutil.copytree(COMPONENTS_FOLDER_NAME + os.path.sep + folder, WEB_FOLDER_NAME + os.path.sep + folder) 
			except OSError as err:
				if err.errno != 17:
					print("Error:", e)

def populate_independent_vars(file, json_file, lan):
	for var in json_file:
		regex_base_var = ''
		if var.endswith('_' + lan):
			base_var = var[:-(len(lan)+1)]
			regex_base_var = '$' + base_var
		else:
			regex_base_var = '$' + var

		with open(file, 'r+') as f:
			file_content = f.read()

			if not isinstance(regex_base_var, list) and regex_base_var in file_content:
				new_file = file_content.replace(str(regex_base_var), json_file[var])
				new_file = new_file.replace('$lan', lan)
				f.seek(0)
				f.write(new_file)
				f.close()

def populate_header(file, json_file, active_lan):
	(filename, ext) = os.path.splitext(file.split(os.path.sep)[-1])
	with open(file, 'r+') as f:
		file_content = f.read()

		regex_lans = '{$list_lans}'

		if regex_lans in file_content:
			component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'nav_lan.html'
			component_new_content = ''
			for lan_json in json_file['lans']:
				with open(component_path, 'r+') as c:
					component_content = c.read()
					component_content = component_content.replace('$lan', lan_json)
					component_content = component_content.replace('$filename', filename)

					if lan_json == active_lan:
						component_content = component_content.replace('$active', 'active')
					else:
						component_content = component_content.replace('$active', '')

					component_new_content = component_new_content + component_content

			new_file = file_content.replace(regex_lans, component_new_content)
			f.seek(0)
			f.write(new_file)
			c.close()
	f.close()
				

def create_index_for_lans(lans, json_file):
	for lan in lans:
		index_path = WEB_FOLDER_NAME + os.path.sep + lan + os.path.sep + 'index.html'
		shutil.copy(COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'index.html', index_path)
		populate_independent_vars(index_path, json_file, lan)
		populate_header(index_path, json_file, lan)
		

if __name__=="__main__":
	json_file = json.load(open(WEB_JSON_FILE_NAME, 'r'))
	lans = json_file["lans"]
	create_folders_for_lans(lans)
	create_index_for_lans(lans, json_file)