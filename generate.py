import json
import os
import shutil
import re
from pathlib import Path

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
				file_content = file_content.replace(str(regex_base_var), json_file[var])
				file_content = file_content.replace('$lan', lan)
				f.seek(0)
				f.write(file_content)

			if '$projects_count' in file_content:
				file_content = file_content.replace('$projects_count', str(count_subsections('projects', json_file)))

			if '$skills_count' in file_content:
				file_content = file_content.replace('$skills_count', str(count_subsections('skills', json_file)))

			if '$universities_count' in file_content:
				file_content = file_content.replace('$universities_count', str(json_file['universities_count']))
		
			if '$courses_count' in file_content:
				file_content = file_content.replace('$courses_count', str(count_subsections('courses', json_file)))
	
			f.seek(0)
			f.write(file_content)
			f.close()

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
		SKILLS_JSON_FILE_NAME = 'components' + os.path.sep + 'js' + os.path.sep + 'skills.json'
		file_content = json.load(open(SKILLS_JSON_FILE_NAME, 'r'))
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

def populate_header(file, json_file, active_lan):
	(filename, ext) = os.path.splitext(file.split(os.path.sep)[-1])
	with open(file, 'r+') as f:
		file_content = f.read()

		regex_lans = '{$list_lans}'
		regex_dropdown_sections = '{$dropdown_sections}'
		regex_menu_sections = '{$menu_sections}'

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

			file_content = file_content.replace(regex_lans, component_new_content)
			f.seek(0)
			f.write(file_content)
			c.close()

		if regex_dropdown_sections in file_content:
			component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'dropdown_section.html'
			component_new_content = ''
			for section_json in json_file['sections']:
				name_section = section_json["title_" + active_lan]
				with open(component_path, 'r+') as c:
					component_content = c.read()
					component_content = component_content.replace('$section', name_section)
					section_path = make_url_friendly(name_section)
					component_content = component_content.replace('$path_section', section_path)

					if name_section in filename:
						component_content = component_content.replace('$active', 'active')
					else:
						component_content = component_content.replace('$active', '')

					component_new_content = component_new_content + component_content

			file_content = file_content.replace(regex_dropdown_sections, component_new_content)
			f.seek(0)
			f.write(file_content)
			c.close()

		if regex_menu_sections in file_content:
			component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'menu_section.html'
			component_new_content = ''
			for section_json in json_file['sections']:
				name_section = section_json["title_" + active_lan]
				img_section = "../" + section_json["img"]
				alt_img_section = section_json["alt_" + active_lan]
				with open(component_path, 'r+') as c:
					component_content = c.read()
					component_content = component_content.replace('$section', name_section)
					section_path = make_url_friendly(name_section)
					component_content = component_content.replace('$path_section', section_path)
					component_content = component_content.replace('$img_section', img_section)
					component_content = component_content.replace('$alt_img_section', alt_img_section)

					if name_section in filename:
						component_content = component_content.replace('$active', 'active')
					else:
						component_content = component_content.replace('$active', '')

					component_new_content = component_new_content + component_content

			file_content = file_content.replace(regex_menu_sections, component_new_content)
			f.seek(0)
			f.write(file_content)
			c.close()

	f.close()

def populate_section(file, json_file, active_lan, active_section):
	(filename, ext) = os.path.splitext(file.split(os.path.sep)[-1])
	with open(file, 'r+') as f:
		file_content = f.read()

		file_content = file_content.replace('$section', active_section['title_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$meta_section_title', active_section['meta_title_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$meta_section_description', active_section['meta_description_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$alt_img_section', active_section['alt_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$img_section', '../' + active_section['img'])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$quote_section', active_section['quote_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$author_section', active_section['quote_author_' + active_lan])
		f.seek(0)
		f.write(file_content)

		regex_menu_subsections = '{$menu_subsections}'
		regex_cards_mosaic = '{$cards_mosaic}'
		regex_highlights_and_cards = '{$highlights_and_cards}'

		if regex_menu_subsections in file_content or regex_cards_mosaic in file_content:
			component_menu_section_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'menu_section.html'
			component_section_cards_mosaic_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'section_cards_mosaic.html'
			component_section_card_img_mosaic_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'section_card_img_mosaic.html'
			component_section_card_txt_mosaic_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'section_card_txt_mosaic.html'
			component_new_content = ''


			if 'subsections' in active_section:
				for subsection_json in active_section['subsections']:
					name_subsection = subsection_json["title_" + active_lan]
					img_subsection = "../" + subsection_json["img"]
					alt_img_subsection = subsection_json["alt_" + active_lan]
					with open(component_menu_section_path, 'r+') as c:
						component_content = c.read()
						component_content = component_content.replace('$section', name_subsection)
						subsection_path = make_url_friendly(name_subsection)
						component_content = component_content.replace('$path_section', subsection_path)
						component_content = component_content.replace('$img_section', img_subsection)
						component_content = component_content.replace('$alt_img_section', alt_img_subsection)

						if name_subsection in filename:
							component_content = component_content.replace('$active', 'active')
						else:
							component_content = component_content.replace('$active', '')

						component_new_content = component_new_content + component_content

				file_content = file_content.replace(regex_menu_subsections, component_new_content)
				file_content = file_content.replace(regex_highlights_and_cards, '')
				f.seek(0)
				f.write(file_content)
				c.close()

			elif 'body_en' in active_section:
				file_content = file_content.replace(regex_menu_subsections, active_section['body_' + active_lan])
				f.seek(0)
				f.write(file_content)

				if active_section['title_en'].lower() == 'transparency':

					with open(component_section_cards_mosaic_path, 'r+') as c:
						component_content = c.read()
						component_content = component_content.replace('$stat1', str(active_section['data']['stat1']))
						component_content = component_content.replace('$stat1_text', active_section['data']['stat1_text_' + active_lan])
						component_content = component_content.replace('$stat2', str(active_section['data']['stat2']))
						component_content = component_content.replace('$stat2_text', active_section['data']['stat2_text_' + active_lan])
						component_content = component_content.replace('$stat3', str(active_section['data']['stat3']))
						component_content = component_content.replace('$stat3_text', active_section['data']['stat3_text_' + active_lan])
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
								new_card_component = new_card_component.replace('$img_card', '../' + card['img'])
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

					file_content = file_content.replace(regex_highlights_and_cards, component_new_content)
					f.seek(0)
					f.write(file_content)
					c.close()

	f.close()

def populate_subsection(file, json_file, active_lan, active_subsection):
	(filename, ext) = os.path.splitext(file.split(os.path.sep)[-1])
	with open(file, 'r+') as f:
		file_content = f.read()
		link_component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'subsection_links.html'
		gallery_component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'subsection_gallery.html'
		gallery_card_component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'gallery_card.html'
		gallery_carousel_component_path = COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'gallery_carousel_item.html'

		file_content = file_content.replace('$subsection_title', active_subsection['title_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$meta_subsection_title', active_subsection['meta_title_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$meta_subsection_description', active_subsection['meta_description_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$alt_img_subsection', active_subsection['alt_' + active_lan])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$img_subsection', '../../' + active_subsection['img'])
		f.seek(0)
		f.write(file_content)

		file_content = file_content.replace('$subsection_body', active_subsection['body_' + active_lan])
		f.seek(0)
		f.write(file_content)

		links_component = ''

		if 'link1' in active_subsection:

			with open(link_component_path, 'r+') as link:
				links_component = link.read()
				link.close()

			links_component = links_component.replace('$subsection_link_1', active_subsection['link1'])
			links_component = links_component.replace('$subsection_link_text_1', active_subsection['text_link1_' + active_lan])
			links_component = links_component.replace('$hidden2', 'd-none')
			links_component = links_component.replace('$hidden3', 'd-none')

		if 'link2' in active_subsection:
			links_component = links_component.replace('$subsection_link_2', active_subsection['link2'])
			links_component = links_component.replace('$subsection_link_text_2', active_subsection['text_link2_' + active_lan])
			links_component = links_component.replace('$hidden2', '')
			links_component = links_component.replace('$hidden3', 'd-none')

		if 'link3' in active_subsection:
			links_component = links_component.replace('$subsection_link_3', active_subsection['link3'])
			links_component = links_component.replace('$subsection_link_text_3', active_subsection['text_link3_' + active_lan])
			links_component = links_component.replace('$hidden3', 'd-none')
			

		file_content = file_content.replace('{$subsection_links}', links_component)
		f.seek(0)
		f.write(file_content)

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
				gallery_card_component = gallery_card_component.replace('$img_gallery', '../../' + image['img'])
				gallery_card_component = gallery_card_component.replace('$alt_img_gallery', image['alt_' + active_lan])
				
				with open(gallery_carousel_component_path, 'r+') as carousel:
					gallery_new_carousel_component = carousel.read()
					carousel.close()
				gallery_carousel_component = gallery_carousel_component + gallery_new_carousel_component.replace('$img_gallery', '../../' + image['img'])
				gallery_carousel_component = gallery_carousel_component.replace('$alt_img_gallery', image['alt_' + active_lan])
				gallery_carousel_component = gallery_carousel_component.replace('$gallery_img_title', image['img_title_' + active_lan])
				gallery_carousel_component = gallery_carousel_component.replace('$gallery_img_description', image['img_description_' + active_lan])
				if img_index == 0:
					gallery_carousel_component = gallery_carousel_component.replace('$active', 'active')

				img_index = img_index + 1

		file_content = file_content.replace('{$subsection_gallery}', gallery_component)
		file_content = file_content.replace('{$gallery_cards}', gallery_card_component)
		file_content = file_content.replace('{$gallery_carousel_items}', gallery_carousel_component)
		f.seek(0)
		f.write(file_content)

	f.close()

def create_index_for_lans(lans, json_file):
	for lan in lans:
		index_path = WEB_FOLDER_NAME + os.path.sep + lan + os.path.sep + 'index.html'
		shutil.copy(COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'index.html', index_path)
		populate_independent_vars(index_path, json_file, lan)
		populate_header(index_path, json_file, lan)

def create_sections_for_lans(lans, json_file):
	for lan in lans:
		for section in json_file['sections']:
			section_filename = set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog')
			section_path = WEB_FOLDER_NAME + os.path.sep + lan + os.path.sep + section_filename + '.html'
			shutil.copy(COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'section.html', section_path)
			populate_independent_vars(section_path, json_file, lan)
			populate_header(section_path, json_file, lan)
			populate_section(section_path, json_file, lan, section)
			create_sub_sections_for_lans_and_section(lans, json_file, section, lan)

def create_sub_sections_for_lans_and_section(lans, json_file, section, lan):
	if 'subsections' in section:
		for subsection in section['subsections']:
			section_filename = set_file_name(section['title_' + lan], section['title_en'].lower() == 'blog')
			subsection_filename = set_file_name(subsection['title_' + lan], section['title_en'].lower() == 'blog')
			section_dir_path = WEB_FOLDER_NAME + os.path.sep + lan + os.path.sep + section_filename
			subsection_path = WEB_FOLDER_NAME + os.path.sep + lan + os.path.sep + section_filename + os.path.sep + subsection_filename + '.html'
			if not os.path.exists(section_dir_path):
				os.mkdir(section_dir_path)
			shutil.copy(COMPONENTS_FOLDER_NAME + os.path.sep + COMPONENTS_HTML_FOLDER_NAME + os.path.sep + 'subsection.html', subsection_path)
			populate_independent_vars(subsection_path, json_file, lan)
			populate_header(subsection_path, json_file, lan)
			populate_subsection(subsection_path, json_file, lan, subsection)
		
def clean_html_files():
	for file in Path(WEB_FOLDER_NAME).rglob('*.html'):
		with open(str(file.parents[0]) + os.path.sep + str(file.name), 'r+') as f:
			file_content = f.read()
			end_pos = file_content.find("</html>")
			if end_pos != -1:
				file_content = file_content[:(end_pos+len("</html>"))]
				f.seek(0)
				f.write(file_content)
				f.truncate()
				
			f.close()

def set_file_name(filename, is_blog):
	filename = make_url_friendly(filename.lower())
	filename = filename.split()[0]
	if not is_blog:
		filename = filename.split("-")[0]
		filename = filename.split("_")[0]
	return filename

if __name__=="__main__":
	json_file = json.load(open(WEB_JSON_FILE_NAME, 'r'))
	lans = json_file["lans"]
	create_folders_for_lans(lans)
	create_index_for_lans(lans, json_file)
	create_sections_for_lans(lans, json_file)
	clean_html_files()