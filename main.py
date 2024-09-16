# from ebooklib import epub
# import os
#
# # Define the manga directory
# manga_directory = 'test/'
#
# # Get list of images (assuming they are sorted numerically)
# images = sorted([f for f in os.listdir(manga_directory) if f.endswith(('jpg'))])
#
# # Create a new EPUB book
# book = epub.EpubBook()
#
# # Set the title, author, and language of the book
# book.set_title('My Manga Title')
# book.set_language('ja')  # Japanese language code
#
# # Add metadata
# book.add_author('Manga Author')
# style = '''
# body, html {
#     margin: 0;
#     padding: 0;
#     width: 100%;
#     height: 100%;
#     text-align: center;
# }
# img {
#   max-width: 100%; height: auto;
# }
# '''
# # Create chapters/pages for each image
# for i, image_file in enumerate(images):
#     # Open the image file
#     with open(os.path.join(manga_directory, image_file), 'rb') as img:
#         # Create an item for each image, making it an XHTML page
#         img_content = img.read()
#         img_name = f'image_{i+1}.jpg'  # Name the image
#         image_item = epub.EpubItem(
#             uid=f'image_{i+1}',  # Unique ID for the image
#             file_name=img_name,  # Set file name
#             media_type='image/jpeg',  # MIME type of the image
#             content=img_content
#         )
#         book.add_item(image_item)  # Add image to the EPUB
#
#         # Create a blank HTML chapter that references the image
#         chapter = epub.EpubHtml(
#             title=f'Page {i+1}',
#             file_name=f'page_{i+1}.xhtml',
#             lang='ja'
#         )
#         chapter.content = f'<html><body><img src="{img_name}" /></body></html>'
#         book.add_item(chapter)
#
#         # Add chapter to the spine
#         book.spine.append(chapter)
#
# # Define the table of contents
# book.toc = [(epub.Section('Manga'), [epub.Link(f'page_{i+1}.xhtml', f'Page {i+1}', f'page_{i+1}') for i in range(len(images))])]
#
# # Add default CSS (optional)
# nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
# book.add_item(nav_css)
#
# # Add the default NCX and Navigation files (important for EPUB format)
# book.add_item(epub.EpubNcx())
# book.add_item(epub.EpubNav())
#
# # Create the final EPUB file
# epub.write_epub('manga.epub', book)
import json
import os.path

import requests

api = 'https://api.mangadex.org'

manga_id = '63ea21e4-5ea8-4f73-87e1-ddf10563650c'
manga_info_url = f'{api}/manga/{manga_id}'
manga_info = requests.get(manga_info_url).json()
if manga_info['result'] != 'ok':
    print('Manga info not ok!')
    quit()
manga_info = manga_info['data']
manga_name = manga_info['attributes']['links']['nu']

manga_path = f'manga/{manga_name}'

if not os.path.exists(manga_path):
    os.mkdir(manga_path)
chapters = requests.get(f'{api}/manga/{manga_id}/feed').json()['data']

volumes = {}

for chapter in chapters:
    chapter_attributes = chapter['attributes']
    if chapter_attributes['translatedLanguage'] != 'en':
        continue
    chapter_id = chapter['id']
    a_volume = int(chapter_attributes['volume'])
    a_chapter = int(chapter_attributes['chapter'])
    if a_volume not in volumes:
        volumes[a_volume] = {}
    if a_chapter not in volumes[a_volume]:
        volumes[a_volume][a_chapter] = [chapter_id, chapter_attributes['pages'], chapter_attributes['title']]
    else:
        if volumes[a_volume][a_chapter][1] < chapter_attributes['pages']:
            volumes[a_volume][a_chapter] = [chapter_id, chapter_attributes['pages'], chapter_attributes['title']]


print(f'Manga: {manga_name}')
for volume_i in dict(sorted(volumes.items())):
    volume_path = f'manga/{manga_name}/volume_{volume_i}'
    print(f'Volume: {volume_i}')

    if not os.path.exists(volume_path):
        os.mkdir(volume_path)

    for chapter_i in dict(sorted(volumes[volume_i].items())):
        chapter = volumes[volume_i][chapter_i]

        chapter_id = chapter[0]
        chapter_url = 'https://api.mangadex.org/at-home/server/' + chapter_id

        chapter_name = f'chapter_{chapter_i}'
        if chapter[2] != None:
            chapter_name += f'_{chapter[2]}'

        print(chapter_name)

        chapter_path = f'{volume_path}/{chapter_name}'

        if not os.path.exists(chapter_path):
            os.mkdir(chapter_path)
        chapter_res = requests.get(chapter_url).json()
        if chapter_res['result'] == 'ok':
            chapter_res = chapter_res['chapter']
            image_base_url = 'https://uploads.mangadex.org/data/'
            for page_i in range(len(chapter_res['data'])):
                page = chapter_res['data'][page_i]
                image_url = image_base_url + chapter_res['hash'] + '/' + page
                page_path = f'{chapter_path}/page_{page_i+1}.png'
                print(f'Page: {page_i}')
                if os.path.exists(page_path):
                    continue
                with open(page_path, 'wb') as image:
                    image.write(requests.get(image_url).content)
