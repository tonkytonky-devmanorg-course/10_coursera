import argparse
import random
from os import path
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests


def _main():
    args = get_args(argparse.ArgumentParser())

    courses_list = get_courses_list(args.number)
    courses_info = [get_course_info(course) for course in courses_list]

    output_courses_info_to_xlsx(courses_info, args.path)


def get_args(parser):
    parser.add_argument(
        'path',
        help='Path to output file'
    )
    parser.add_argument(
        '-n',
        '--number',
        help='Number of courses to get',
        type=int,
        default=20
    )

    return parser.parse_args()


def get_random_courses_urls(number):
    print('Получение списка курсов...')
    courses = requests.get(
        'https://www.coursera.org/sitemap~www~courses.xml').text
    courses = ET.fromstring(courses)
    namespace = {'xmlns': "http://www.sitemaps.org/schemas/sitemap/0.9"}
    courses_urls = [
        loc.text for loc in courses.findall('.//xmlns:loc', namespace)]

    return random.sample(courses_urls, k=number)


def get_course_info(course_url):
    print('Получение информации по курсу: {}'.format(course_url))
    course_response = requests.get(course_url)
    course = BeautifulSoup(
        course_response.content.decode('utf-8'), 'html.parser')

    language_node = course.find('div', class_='rc-Language')
    language = language_node.text if language_node else '-'

    commitment_node = course.find('i', class_='cif-clock')
    if commitment_node:
        for parent in commitment_node.parents:
            if parent.name == 'tr':
                break
        commitment = parent.find('td', class_='td-data').text
    else:
        commitment = '-'

    stars_node = course.find('div', class_='ratings-info')
    stars = stars_node.find_all('div')[1].text if stars_node else '-'

    course_info = {
        'name': course.h1.text,
        'language': language,
        'commitment': commitment,
        'stars': stars,
    }
    return course_info


def output_courses_info_to_xlsx(courses_info, filepath):
    print('Запись в файл')
    headers = [
        'Название',
        'Язык',
        'Количество недель',
        'Средняя оценка',
    ]
    wb = Workbook()
    ws = wb.active
    ws.append(headers)

    for course_info in courses_info:
        ws.append([
            course_info['name'],
            course_info['language'],
            course_info['commitment'],
            course_info['stars'],
        ])

    wb.save(filepath)


if __name__ == '__main__':
    _main()
