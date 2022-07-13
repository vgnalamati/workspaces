import requests
import re
import logging
import argparse
from bs4 import BeautifulSoup
from prettytable import PrettyTable

Salary_table = PrettyTable()
Salary_table.field_names = ['Company', 'Role', 'Salary', 'Location', 'Start Date']


logger = logging.getLogger(__name__)

def labor_filing(args):
    if any([args.company, args.role_starts_with, args.location]):
        search_string = args.role_contains if args.role_contains else args.role_starts_with
        H1B_WEBLINK = f"https://h1bdata.info/index.php?em={'+'.join(args.company.split())}&job={'+'.join(args.role_starts_with.split())}&city={'+'.join(args.location.split())}&year={'+'.join(args.year.split())}"
        logger.info(f"Search URL: {H1B_WEBLINK}")
        req = requests.get(H1B_WEBLINK)
        logger.info(f'Status Code: {req.status_code}')
        soup = BeautifulSoup(req.text, 'html.parser')
        rows =  soup.table.tbody.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [element.text.strip() for element in cols]
            if len(cols)>4 and re.search(search_string, cols[1], re.IGNORECASE):
                Salary_table.add_row([cols[0].title(), cols[1].title(), cols[2], cols[3], cols[5]])
        print(Salary_table)
    else:
        logger.critical("Not enough Query Parameters. If you want to search try using -rs")


if __name__ == '__main__':
    salary = argparse.ArgumentParser()
    salary.add_argument(
        "--company",
        default = "",
        type = lambda x: x.title(),
        help="Company Name to search",
    )
    salary.add_argument(
        "--year",
        default="All Years",
        help="Year to search",
    )
    salary.add_argument(
        "--location",
        default='',
        type = lambda x: x.upper(),
        help="Location to search (City)",
    )
    salary.add_argument(
        "--role_starts_with",
        "-rs",
        default='',
        type = lambda x: x.upper(),
        help="Search Role that starts with",
    )

    salary.add_argument(
        "--role_contains",
        "-rc",
        default='',
        type = lambda x: x.upper(),
        help="Search Role that contains",
    )
    labor_filing(salary.parse_args())

