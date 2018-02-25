import argparse
import random
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests


def _main():
    args = get_args(argparse.ArgumentParser())

    courses_list = get_random_courses_urls(args.number)
    courses_info = [get_course_info(course) for course in courses_list]

    workbook = Workbook()
    output_courses_info_to_xlsx(workbook, courses_info)
    workbook.save(args.path)


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


def write_to_log(message):
    print(message)


def get_random_courses_urls(number):
    write_to_log('Получение списка курсов...')
    courses = requests.get(
        'https://www.coursera.org/sitemap~www~courses.xml').text
    courses = ET.fromstring(courses)
    namespace = {'xmlns': "http://www.sitemaps.org/schemas/sitemap/0.9"}
    courses_urls = [
        loc.text for loc in courses.findall('.//xmlns:loc', namespace)
    ]

    return random.sample(courses_urls, k=number)


def get_course_info(course_url):
    write_to_log('Получение информации по курсу: {}'.format(course_url))
    course_response = requests.get(course_url)
    course = BeautifulSoup(
        course_response.content.decode('utf-8'), 'html.parser')

    language_node = course.find('div', class_='rc-Language')

    start_node = course.find('div', class_='startdate')

    weeks_nodes = course.find_all('div', class_='week-heading')
    duration_node = None
    if weeks_nodes:
        duration_node = weeks_nodes[-1]

    stars_parent_node = course.find('div', class_='rc-RatingsHeader')
    stars_node = None
    if stars_parent_node:
        stars_node = stars_parent_node.find('div', class_='ratings-text')

    return {
        'name': course.h1.text,
        'language': language_node.text if language_node else '-',
        'start': start_node.text if start_node else '-',
        'duration': ''.join(
            char for char in duration_node.text if char.isdigit()
        ) if duration_node else '-',
        'stars': stars_node.text if stars_node else '-',
    }


def output_courses_info_to_xlsx(workbook, courses_info):
    write_to_log('Запись в файл')
    headers = [
        'Название',
        'Язык',
        'Дата начала'
        'Количество недель',
        'Средняя оценка',
    ]
    ws = workbook.active
    ws.append(headers)

    for course_info in courses_info:
        ws.append([
            course_info['name'],
            course_info['language'],
            course_info['start'],
            course_info['duration'],
            course_info['stars'],
        ])


if __name__ == '__main__':
    _main()
