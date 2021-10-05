######################################
### GitHub API - Search for a term ###
### Code written by Bence Kollanyi ###
######################################

import requests
import json
import math
import time

token = '****ADD YOUR TOKEN HERE****'
src = 'https://api.github.com/search/repositories?q='
usr = 'https://api.github.com/users/'
term = '****ADD YOUR SEARCH TERM HERE****'
head = {'Authorization':'token %s' % token}

def chk_limit():
    '''Check the remaining API calls (5000/hours per limit), and wait if the script reached 99 percent of the limit.'''
    api_limit = requests.get('https://api.github.com/rate_limit', headers=head).json()
    if api_limit['rate']['remaining'] < 50:
        reset_remaining_time = math.ceil(abs(time.time() - api_limit['rate']['reset']))
        print('The API rate limit is close to being reached. Now sleeping: %s seconds!' % reset_remaining_time)
        time.sleep(reset_remaining_time)
        print('Data collection has resumed.')

def date_period(year,quarter):
    if quarter == 1:
        date_formatted = f'"{year}-01-01..{year}-03-31"'
    elif quarter == 2:
        date_formatted = f'"{year}-04-01..{year}-06-30"'
    elif quarter == 3:
        date_formatted = f'"{year}-07-01..{year}-09-30"'
    elif quarter == 4:
        date_formatted = f'"{year}-10-01..{year}-12-31"'
    return(date_formatted)

def count_total(cre):
    ## Search for a term and and time (created at)
    url = f'{src}{term}+created:{cre}'
    head = {'Authorization': 'token %s' % token}
    response = requests.get(url, headers=head).json()
    total = response['total_count']
    print(f'Results for the {cre} period: {total}')
    return(total)

def get_new_repos(url, target):
    new_repositories = []
    page_nr = 0
    while len(new_repositories) != target:
        page_nr += 1
        par = {'page': page_nr, 'per_page': 100}
        head = {'Authorization': 'token %s' % token}
        response = requests.get(url, params=par, headers=head).json()
        new_repositories.extend(response['items'])
    return(new_repositories)

print('Welcome to the GitHub Search API Extractor', '\n')

url = src + term

## Printing the number of results for the term
response = requests.get(url).json()
termtotal = response['total_count']
print('Number of results for the search term:', termtotal, '\n')

## Setting the time period (years) for the data collection
years = [2018, 2019, 2020]

repositories = []

## Collecting the results from every quarter within the above specified time period
for year in years:
    for q in range(4):
        cre = date_period(year, q+1)
        target = count_total(cre)
        url = f'{src}{term}+created:{cre}'
        repositories.extend(get_new_repos(url, target))
        chk_limit()

## Save the output in JSON
with open('GitHub_search_results.json', 'w') as file:
    json.dump(repositories, file)
