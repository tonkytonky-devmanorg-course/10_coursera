import argparse
import random
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests


def _main():
    args = get_args(argparse.ArgumentParser())

    courses_urls = get_random_courses_urls(
        get_page_from_web('https://www.coursera.org/sitemap~www~courses.xml'),
        args.number
    )
    courses = [
        get_course(get_page_from_web(course_url))
        for course_url in courses_urls
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


def get_course(course_page):
    course = BeautifulSoup(course_page, 'html.parser')

    language_node = course.select_one('div.rc-Language')
    language = language_node.text if language_node else None
    start_node = course.select_one('div.startdate')
    start = start_node.text if start_node else None
    weeks_nodes = course.select('div.week-heading')
    if weeks_nodes:
        duration = int(''.join(
            char for char in weeks_nodes[-1].text if char.isdigit()
        ))
    else:
        duration = None
    stars_parent_node = course.select_one('div.rc-RatingsHeader')
    if stars_parent_node:
        stars = stars_parent_node.select_one('div.ratings-text').text
    else:
        stars = None

    return {
        'name': course.h1.text,
        'language': language,
        'start': start,
        'duration': duration,
        'stars': stars,
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
