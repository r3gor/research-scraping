from bs4 import BeautifulSoup
from urllib.parse import urlencode
from html2text import html2text
from time import time
import requests
import pandas as pd
import os

PREFIX = 'https://pe.indeed.com'

def safe_get_text(node):
    if (node): return node.text.replace("\n","").strip()
    return 'None'

def make_url(query, location, start=0):
    params = urlencode({'q': query, 'l': location, 'start:': start})
    url = f"{PREFIX}/jobs?{params}"
    return url

def objs_to_csv(objs, output_file):
    df = pd.DataFrame(objs)
    df.to_csv(output_file, index=False)

class Job:
    def __init__(self, title, company, company_location, salary, url, description):
        self.title = title
        self.company = company
        self.company_location = company_location
        self.salary = salary
        self.url = url
        self.description = description
    
    def __str__(self):
        return f'''
            title: {self.title}
            company: {self.company}
            company_location: {self.company_location}
            salary: {self.salary}
            url: {self.url}
            description: {self.description}
        '''

    def __repr__(self):
        return f'''
            title: {self.title}
            company: {self.company}
            company_location: {self.company_location}
            salary: {self.salary}
            url: {self.url[:50]}
            description: {self.description[:50]}
        '''

    def serialize(self):
        return {
            'title': self.title,
            'company': self.company,
            'company_location': self.company_location,
            'salary': self.salary,
            'url': self.url,
            'description': self.description,
        }

class ScraperJob:
    def __init__(self, html):
        self.bs = BeautifulSoup(html, "html.parser")
        self.job = self.get_job()
        print(f'Scraper: {self.job.title}')

    def get_title(self):
        return safe_get_text(self.bs.find('h2').findChildren('span', recursive=False)[0])

    def get_company(self):
        return safe_get_text(self.bs.find('span', class_='companyName'))

    def get_company_location(self):
        return safe_get_text(self.bs.find('div', class_='companyLocation'))

    def get_salary(self):
        return safe_get_text(self.bs.find('div', class_='salary-snippet'))

    def get_url(self):
        return PREFIX + self.bs.find('a')['href']

    def get_description(self):
        url = self.get_url()
        html = requests.get(url)
        bs = BeautifulSoup(html.text, "html.parser")
        return html2text(str(bs.find('div', attrs={'id': 'jobDescriptionText'})))

    def get_job(self):
        return Job(
            title=self.get_title(),
            company=self.get_company(),
            company_location=self.get_company_location(),
            salary=self.get_salary(),
            url=self.get_url(),
            description=self.get_description(),
        )

class ScraperPage:
    def __init__(self, html):
        self.bs = BeautifulSoup(html, "html.parser")
    
    def get_jobs_html(self):
        return self.bs.find_all('a', class_="tapItem")

def get_jobs(Q, L, i):
    url = make_url(Q, L, i*10)
    html = requests.get(url)
    scraper_page = ScraperPage(html.text)
    # scraper_jobs = [ScraperJob(str(html)) for html in scraper_page.get_jobs_html()[:3]]
    scraper_jobs = [ScraperJob(str(html)) for html in scraper_page.get_jobs_html()]
    return [sj.job for sj in scraper_jobs]

def query_processes(Q, L, i, out_dir):
    start_time = time()
    jobs = get_jobs(Q, L, i)
    time_exec = (time() - start_time)
    print(f"Total: {len(jobs)} \t {time_exec} seg.")

    output_file = out_dir + '/' + (Q+'@'+L+'@'+str(i)).replace(' ', '-') + '.csv'
    print(f'Writing: {output_file}')
    # import pdb; pdb.set_trace()
    objs_to_csv([j.serialize() for j in jobs], output_file)

    return time_exec

if __name__ == '__main__':

    # Q = 'Desarrollador Web'
    # L = 'Lima'
    # PAGES = 1

    # jobs = [
    #     job 
    #     for i in range(PAGES)
    #     for job in get_jobs(Q, L, i) 
    # ]

    # print(f"Total: {len(jobs)}")

    # output_file = (Q+'_'+L+'_'+str(PAGES)).replace(' ', '-') + '.csv'

    # df = pd.DataFrame([j.serialize() for j in jobs])
    # df.to_csv(output_file, index=False)
    pass