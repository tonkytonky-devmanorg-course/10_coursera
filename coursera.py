import argparse
import random
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests


def _main():
    args = get_args(argparse.ArgumentParser())

    courses_urls = get_random_courses_urls(get_page_from_web(
        'https://www.coursera.org/sitemap~www~courses.xml'), args.number)
    courses = [
        get_course_info(get_page_from_web(course_url)) for
        course_url in courses_urls
    ]

    workbook = Workbook()
    output_courses_info_to_xlsx(workbook, courses)
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


def get_page_from_web(url, encoding='utf-8'):
    response = requests.get(url)
    return response.content.decode(encoding)


def get_random_courses_urls(courses_page, number):
    courses = ET.fromstring(courses_page)
    namespace = {'xmlns': "http://www.sitemaps.org/schemas/sitemap/0.9"}
    courses_urls = [
        loc.text for loc in courses.findall('.//xmlns:loc', namespace)
    ]

    return random.sample(courses_urls, k=number)


def get_course_info(course_page):
    course = BeautifulSoup(course_page, 'html.parser')

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
        'language': language_node.text if language_node else None,
        'start': start_node.text if start_node else None,
        'duration': int(''.join(
            char for char in duration_node.text if char.isdigit()
        )) if duration_node else None,
        'stars': stars_node.text if stars_node else None,
    }


def output_courses_info_to_xlsx(workbook, courses):
    worksheet = workbook.active
    headers = [
        'Название',
        'Язык',
        'Дата начала',
        'Количество недель',
        'Средняя оценка',
    ]
    worksheet.append(headers)

    for course in courses:
        worksheet.append([
            course['name'] or '-',
            course['language'] or '-',
            course['start'] or '-',
            course['duration'] or '-',
            course['stars'] or '-',
        ])


if __name__ == '__main__':
    _main()
