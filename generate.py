import json
import os
import shutil
import re
from pathlib import Path

ABSOLUTE_URL = 'https://www.mariovarona.dev'
ONE_DIR_UP = '../'
TWO_DIRS_UP = '../../'
COMPONENTS_FOLDER_NAME = 'components'
COMPONENTS_HTML_FOLDER_NAME = 'html'
PATH_SEPARATOR = os.path.sep
STATIC_FOLDERS = ['css', 'images', 'js', 'static']
STATIC_FOLDER_WHOSE_FILES_ARE_GLOBAL = 'static'
LEGAL_FILES = ['tos.html', 'privacy.html']
INDEX_FILE_NAME = 'index.html'
SECTION_FILE_NAME = 'section.html'
SUBSECTION_FILE_NAME = 'subsection.html'
SKILLS_JSON_FILE_NAME = 'skills.json'
WEB_FOLDER_NAME = 'web'
WEB_JSON_FILE_NAME = 'web.json'

# TODO: Change to load absolute paths:
IS_PRODUCTION = True

def create_folders_for_lans(lans):
	for lan in lans:
		dir = WEB_FOLDER_NAME + PATH_SEPARATOR + lan
		
		if os.path.exists(dir):
			shutil.rmtree(dir)
		os.makedirs(dir)

		for folder in STATIC_FOLDERS:
			if 'static' not in folder:
				try:
					shutil.copytree(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + folder, WEB_FOLDER_NAME + PATH_SEPARATOR + folder) 
				except OSError as err:
					if err.errno != 17:
						print("Error:", err)

	for file in os.listdir(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + STATIC_FOLDER_WHOSE_FILES_ARE_GLOBAL):
		shutil.copy(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + STATIC_FOLDER_WHOSE_FILES_ARE_GLOBAL + PATH_SEPARATOR + file, WEB_FOLDER_NAME + PATH_SEPARATOR + file)				

def create_index_for_lans(lans, json_file):
	for lan in lans:

		index_path = WEB_FOLDER_NAME + PATH_SEPARATOR + lan + PATH_SEPARATOR + INDEX_FILE_NAME
		
		shutil.copy(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + INDEX_FILE_NAME, index_path)
		populate_independent_vars(index_path, json_file, lan)
		populate_header(index_path, json_file, lan)

def create_legal_files():
	for legal_file in LEGAL_FILES:

		legal_path = WEB_FOLDER_NAME + PATH_SEPARATOR + legal_file

		populate_independent_vars(legal_path, json_file, 'es')
		populate_header(legal_path, json_file, 'es')

def create_sections_for_lans(lans, json_file):
	for lan in lans:
		for section in json_file['sections']:

			section_filename = set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog')
			section_path = WEB_FOLDER_NAME + PATH_SEPARATOR + lan + PATH_SEPARATOR + section_filename + '.html'
			
			shutil.copy(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + SECTION_FILE_NAME, section_path)
			
			populate_independent_vars(section_path, json_file, lan)
			populate_header(section_path, json_file, lan, section)
			populate_section(section_path, json_file, lan, section)
			create_sub_sections_for_lans_and_section(lans, json_file, section, lan)

def create_sub_sections_for_lans_and_section(lans, json_file, section, lan):
	if 'subsections' in section:
		for subsection in section['subsections']:

			section_filename = set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog')
			subsection_filename = set_file_name(subsection['title_' + lan], section['title_en'].lower() == 'blog')
			section_dir_path = WEB_FOLDER_NAME + PATH_SEPARATOR + lan + PATH_SEPARATOR + section_filename
			subsection_path = WEB_FOLDER_NAME + PATH_SEPARATOR + lan + PATH_SEPARATOR + section_filename + PATH_SEPARATOR + subsection_filename + '.html'
			
			if not os.path.exists(section_dir_path):
				os.mkdir(section_dir_path)
			
			shutil.copy(COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + SUBSECTION_FILE_NAME, subsection_path)
			
			populate_independent_vars(subsection_path, json_file, lan)
			populate_header(subsection_path, json_file, lan, section, subsection)
			populate_subsection(subsection_path, json_file, lan, subsection)

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
				file_content = file_content.replace(str(regex_base_var), json_file[var])
				file_content = file_content.replace('$lan', lan)

			if '$projects_count' in file_content:
				file_content = file_content.replace('$projects_count', str(count_subsections('experience', json_file)))

			if '$skills_count' in file_content:
				file_content = file_content.replace('$skills_count', str(count_subsections('skills', json_file)))

			if '$universities_count' in file_content:
				file_content = file_content.replace('$universities_count', str(json_file['universities_count']))
		
			if '$courses_count' in file_content:
				file_content = file_content.replace('$courses_count', str(count_subsections('courses', json_file)))
	
			f.seek(0)
			f.write(file_content)
			f.close()

def populate_header(file, json_file, active_lan, section=None, subsection=None):
	(filename, ext) = os.path.splitext(file.split(PATH_SEPARATOR)[-1])
	with open(file, 'r+') as f:
		file_content = f.read()

		regex_lans = '{$list_lans}'
		regex_dropdown_sections = '{$dropdown_sections}'
		regex_menu_sections = '{$menu_sections}'

		if regex_lans in file_content:
			component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'nav_lan.html'
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

					component_content = component_content.replace('$path_to_lan', get_path_for_lan(lan_json, section, subsection))

					component_new_content = component_new_content + component_content

			file_content = replace_text_in_file(f, file_content, regex_lans, component_new_content)
			
			c.close()

		if regex_dropdown_sections in file_content:
			component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'dropdown_section.html'
			component_new_content = ''

			for section_json in json_file['sections']:
				name_section = section_json["title_" + active_lan]
				
				with open(component_path, 'r+') as c:
					component_content = c.read()
					component_content = component_content.replace('$section', name_section)
					section_path = set_file_name(name_section, section_json['title_en'].lower() == 'blog')
					
					component_content = component_content.replace('$path_section', ABSOLUTE_URL + "/" + active_lan + "/" + section_path)

					if section is None and subsection is None:
						component_content = component_content.replace('$dropdown_section_active', '')

					if not section is None and subsection is None:
						if filename.lower().split("-")[0] in name_section.lower():
							component_content = component_content.replace('$dropdown_section_active', 'active')
						else:
							component_content = component_content.replace('$dropdown_section_active', '')
					
					if not section is None and not subsection is None:
						if name_section == section['title_' + active_lan]:
							component_content = component_content.replace('$dropdown_section_active', 'active')
						else:
							component_content = component_content.replace('$dropdown_section_active', '')
					

					c.close()

					component_new_content = component_new_content + component_content

			file_content = replace_text_in_file(f, file_content, regex_dropdown_sections, component_new_content)
			c.close()

		if regex_menu_sections in file_content:
			component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'menu_section.html'
			component_new_content = ''

			for section_json in json_file['sections']:
				name_section = section_json["title_" + active_lan]
				img_section = return_url_for_environment(ONE_DIR_UP, section_json["img"])
				alt_img_section = section_json["alt_" + active_lan]

				with open(component_path, 'r+') as c:
					component_content = c.read()
					component_content = component_content.replace('$section', name_section)
					section_path = set_file_name(name_section, section_json['title_en'].lower() == 'blog')
					component_content = component_content.replace('$path_section', section_path)
					component_content = component_content.replace('$img_section', img_section)
					component_content = component_content.replace('$alt_img_section', alt_img_section)

					if filename.lower().split("-")[0] in name_section:
						component_content = component_content.replace('$active', 'active')
					else:
						component_content = component_content.replace('$active', '')

					component_new_content = component_new_content + component_content

			file_content = replace_text_in_file(f, file_content, regex_menu_sections, component_new_content)
			c.close()

	f.close()

def populate_section(file, json_file, active_lan, active_section):
	(filename, ext) = os.path.splitext(file.split(PATH_SEPARATOR)[-1])

	with open(file, 'r+') as f:
		file_content = f.read()

		file_content = replace_text_in_file(f, file_content, '$section', active_section['title_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$meta_section_title', active_section['meta_title_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$meta_section_description', active_section['meta_description_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$alt_img_section', active_section['alt_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$img_section', return_url_for_environment(ONE_DIR_UP, active_section['img']))
		file_content = replace_text_in_file(f, file_content, '$quote_section', active_section['quote_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$author_section', active_section['quote_author_' + active_lan])
		
		regex_menu_subsections = '{$menu_subsections}'
		regex_cards_mosaic = '{$cards_mosaic}'
		regex_highlights_and_cards = '{$highlights_and_cards}'

		if regex_menu_subsections in file_content or regex_cards_mosaic in file_content:
			component_menu_section_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'menu_section.html'
			component_section_cards_mosaic_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'section_cards_mosaic.html'
			component_section_card_img_mosaic_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'section_card_img_mosaic.html'
			component_section_card_txt_mosaic_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'section_card_txt_mosaic.html'
			component_new_content = ''


			if 'subsections' in active_section:
				for subsection_json in active_section['subsections']:
					name_subsection = subsection_json["title_" + active_lan]
					img_subsection = return_url_for_environment(ONE_DIR_UP, subsection_json["img"])
					alt_img_subsection = subsection_json["alt_" + active_lan]
					
					with open(component_menu_section_path, 'r+') as c:
						component_content = c.read()

						component_content = component_content.replace('$section', name_subsection)
						subsection_path = active_section["title_" + active_lan].lower() + "/" + set_file_name(name_subsection, active_section['title_en'].lower() == 'blog')
						component_content = component_content.replace('$path_section', subsection_path)
						component_content = component_content.replace('$img_section', img_subsection)
						component_content = component_content.replace('$alt_img_section', alt_img_subsection)

						component_new_content = component_new_content + component_content

				file_content = file_content.replace(regex_menu_subsections, component_new_content)
				file_content = replace_text_in_file(f, file_content, regex_highlights_and_cards, '')
				
				c.close()

			elif 'body_en' in active_section:
				file_content = replace_text_in_file(f, file_content, regex_menu_subsections, active_section['body_' + active_lan])

				if active_section['title_en'].lower() == 'transparency':

					with open(component_section_cards_mosaic_path, 'r+') as c:
						component_content = c.read()
						component_content = component_content.replace('$stat1', str(active_section['data']['stat1']))
						component_content = component_content.replace('$text_stat1', active_section['data']['text_stat1_' + active_lan])
						component_content = component_content.replace('$stat2', str(active_section['data']['stat2']))
						component_content = component_content.replace('$text_stat2', active_section['data']['text_stat2_' + active_lan])
						component_content = component_content.replace('$stat3', str(active_section['data']['stat3']))
						component_content = component_content.replace('$text_stat3', active_section['data']['text_stat3_' + active_lan])
						component_content = component_content.replace('$last_update', active_section['data']['last_update_' + active_lan])

						card_img_template = ''
						card_txt_template = ''
						with open(component_section_card_img_mosaic_path, 'r+') as card:
							card_img_template = card.read()
							card.close()

						with open(component_section_card_txt_mosaic_path, 'r+') as card:
							card_txt_template = card.read()
							card.close()
						
						cards_component = ''
						for card in active_section['data']['cards']:
							if 'img' in card:
								new_card_component = card_img_template
								new_card_component = new_card_component.replace('$img_card', return_url_for_environment(ONE_DIR_UP, card['img']))
								new_card_component = new_card_component.replace('$alt_img_card', card['alt_img_' + active_lan])
							else:
								new_card_component = card_txt_template
							
							new_card_component = new_card_component.replace('$title_card', card['title_' + active_lan])
							new_card_component = new_card_component.replace('$subtitle_card', card['subtitle_' + active_lan])
							new_card_component = new_card_component.replace('$href_card', card['href'])
							new_card_component = new_card_component.replace('$last_update_card', card['last_update_' + active_lan])
							new_card_component = new_card_component.replace('$bg_card', card['bg_card'])
							cards_component = cards_component + new_card_component

						component_content = component_content.replace(regex_cards_mosaic, cards_component)
						component_new_content = component_content

					file_content = replace_text_in_file(f, file_content, regex_highlights_and_cards, component_new_content)

					c.close()

				if active_section['title_en'].lower() == 'skills':
					file_content = replace_text_in_file(f, file_content, regex_highlights_and_cards, '')

	f.close()

def populate_subsection(file, json_file, active_lan, active_subsection):
	(filename, ext) = os.path.splitext(file.split(PATH_SEPARATOR)[-1])

	with open(file, 'r+') as f:
		file_content = f.read()
		link_component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'subsection_links.html'
		gallery_component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'subsection_gallery.html'
		gallery_card_component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'gallery_card.html'
		gallery_carousel_component_path = COMPONENTS_FOLDER_NAME + PATH_SEPARATOR + COMPONENTS_HTML_FOLDER_NAME + PATH_SEPARATOR + 'gallery_carousel_item.html'

		file_content = replace_text_in_file(f, file_content, '$subsection_title', active_subsection['title_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$meta_subsection_title', active_subsection['meta_title_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$meta_subsection_description', active_subsection['meta_description_' + active_lan])	
		file_content = replace_text_in_file(f, file_content, '$alt_img_subsection', active_subsection['alt_' + active_lan])
		file_content = replace_text_in_file(f, file_content, '$img_subsection', return_url_for_environment(TWO_DIRS_UP, active_subsection['img']))
		file_content = replace_text_in_file(f, file_content, '$subsection_body', active_subsection['body_' + active_lan])
		
		links_component = ''

		if 'link1' in active_subsection:

			with open(link_component_path, 'r+') as link:
				links_component = link.read()
				link.close()

			links_component = links_component.replace('$subsection_link_1', active_subsection['link1'])
			links_component = links_component.replace('$subsection_link_text_1', active_subsection['text_link1_' + active_lan])
			links_component = links_component.replace('hidden1', '')

		if 'link2' in active_subsection:
			links_component = links_component.replace('$subsection_link_2', active_subsection['link2'])
			links_component = links_component.replace('$subsection_link_text_2', active_subsection['text_link2_' + active_lan])
			links_component = links_component.replace('hidden2', '')

		if 'link3' in active_subsection:
			links_component = links_component.replace('$subsection_link_3', active_subsection['link3'])
			links_component = links_component.replace('$subsection_link_text_3', active_subsection['text_link3_' + active_lan])
			links_component = links_component.replace('hidden3', '')

		file_content = replace_text_in_file(f, file_content, '{$subsection_links}', links_component)

		gallery_component = ''
		gallery_card_component = ''
		gallery_carousel_component = ''

		if 'gallery' in active_subsection:

			with open(gallery_component_path, 'r+') as gallery:
				gallery_component = gallery.read()
				gallery.close()

			gallery_component = gallery_component.replace('$gallery_string', json_file['gallery_string_' + active_lan])
			gallery_component = gallery_component.replace('$previous_string', json_file['previous_string_' + active_lan])
			gallery_component = gallery_component.replace('$next_string', json_file['next_string_' + active_lan])

			img_index = 0
			for image in active_subsection['gallery']:
				with open(gallery_card_component_path, 'r+') as card:
					gallery_new_card_component = card.read()
					card.close()

				gallery_card_component = gallery_card_component + gallery_new_card_component.replace('$gallery_img_index', str(img_index))
				gallery_card_component = gallery_card_component.replace('$img_gallery', return_url_for_environment(TWO_DIRS_UP, image['img']))
				gallery_card_component = gallery_card_component.replace('$alt_img_gallery', image['alt_' + active_lan])
				
				with open(gallery_carousel_component_path, 'r+') as carousel:
					gallery_new_carousel_component = carousel.read()
					carousel.close()

				gallery_carousel_component = gallery_carousel_component + gallery_new_carousel_component.replace('$img_gallery', return_url_for_environment(TWO_DIRS_UP, image['img']))
				gallery_carousel_component = gallery_carousel_component.replace('$alt_img_gallery', image['alt_' + active_lan])
				gallery_carousel_component = gallery_carousel_component.replace('$gallery_img_title', image['img_title_' + active_lan])
				gallery_carousel_component = gallery_carousel_component.replace('$gallery_img_description', image['img_description_' + active_lan])

				if img_index == 0:
					gallery_carousel_component = gallery_carousel_component.replace('$active', 'active')

				img_index = img_index + 1

		file_content = file_content.replace('{$subsection_gallery}', gallery_component)
		file_content = file_content.replace('{$gallery_cards}', gallery_card_component)
		file_content = replace_text_in_file(f, file_content, '{$gallery_carousel_items}', gallery_carousel_component)

	f.close()

def replace_text_in_file(file_descriptor, file_content, to_replace, replacement):
	file_content = file_content.replace(to_replace, replacement)
	file_descriptor.seek(0)
	file_descriptor.write(file_content)
	return file_content

def count_subsections(name, json_file):
	i = 0

	if name == 'courses':
		for section in json_file['sections']:
			if 'subsections' in section:
				for subsection in section['subsections']:
					if subsection['title_en'].lower() == 'courses':
						i = subsection['body_en'].count('<br/>') + 1
						return i

	if name == 'skills':
		SKILLS_JSON_FILE_PATH = 'components' + PATH_SEPARATOR + 'js' + PATH_SEPARATOR + SKILLS_JSON_FILE_NAME
		file_content = json.load(open(SKILLS_JSON_FILE_PATH, 'r'))
		return len(file_content['skillsData'])


	for section in json_file['sections']:
		if section['title_en'].lower() == name:
			if 'subsections' in section:
				i = len(section['subsections'])
				return i
	return i

def make_url_friendly(name):
	url = name.replace("Á", "a").replace("á", "a").replace("ä", "ae").replace("Ä", "ae")
	url = url.replace("É", "e").replace("é", "e").replace("ë", "ee").replace("Ë", "ee")
	url = url.replace("Í", "i").replace("í", "i").replace("ï", "ie").replace("Ï", "ie")
	url = url.replace("Ó", "o").replace("ó", "o").replace("ö", "oe").replace("Ö", "oe")
	url = url.replace("Ú", "u").replace("ú", "u").replace("ü", "ue").replace("Ü", "ue")
	url = url.replace(".", "_").replace(",", "_").replace("-", "_").replace(" ", "-")
	url = url.lower()
	return url

def set_file_name(filename, is_blog):
	filename = make_url_friendly(filename.lower())
	filename = filename.split()[0]
	if not is_blog:
		filename = filename.split("-")[0]
		filename = filename.split("_")[0]
	return filename

def get_path_for_lan(lan, section=None, subsection=None):
	if not section is None and subsection is None:
		return ABSOLUTE_URL + "/" + lan + "/" + set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog')
	elif not section is None and not subsection is None:
		return ABSOLUTE_URL + "/" + lan + "/" + set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog') + "/" + set_file_name(subsection['title_' + lan], subsection['title_en'].lower() == 'blog')
	else:
		return ABSOLUTE_URL + "/" + lan + "/" + INDEX_FILE_NAME

def return_url_for_environment(levels_up, path):
	if IS_PRODUCTION:
		return ABSOLUTE_URL + "/" + path
	else:
		return levels_up + path

def clean_html_files():
	for file in Path(WEB_FOLDER_NAME).rglob('*.html'):
		with open(str(file.parents[0]) + PATH_SEPARATOR + str(file.name), 'r+') as f:
			file_content = f.read()
			end_pos = file_content.find("</html>")
			if end_pos != -1:
				file_content = file_content[:(end_pos+len("</html>"))]
				f.seek(0)
				f.write(file_content)
				f.truncate()
				
			f.close()

if __name__=="__main__":
	json_file = json.load(open(WEB_JSON_FILE_NAME, 'r'))
	lans = json_file["lans"]
	create_folders_for_lans(lans)
	create_index_for_lans(lans, json_file)
	create_sections_for_lans(lans, json_file)
	create_legal_files()
	clean_html_files()