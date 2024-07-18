import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_project_details(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    details = {}
    
    try:
        gstin = soup.find('td', text='GSTIN No').find_next('td').get_text(strip=True)
        pan = soup.find('td', text='PAN No').find_next('td').get_text(strip=True)
        name = soup.find('td', text='Name').find_next('td').get_text(strip=True)
        address = soup.find('td', text='Permanent Address').find_next('td').get_text(strip=True)
        
        details['GSTIN No'] = gstin
        details['PAN No'] = pan
        details['Name'] = name
        details['Permanent Address'] = address
    except AttributeError as e:
        print(f"Error parsing details from {url}: {e}")
        return None
    
    return details

def main():
    base_url = 'https://hprera.nic.in'
    projects_url = f'{base_url}/PublicDashboard/GetMainContent'

    params = {
        'ActiveTab': 'tab_project_main',
    }

    response = requests.get(projects_url, params=params, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Debug: Save the response content to a file to check its structure
    with open('main_page.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    # Finding the container with the project data
    project_links = soup.select('.clsCenterAlign table tbody tr a[href]')[:6]  # Select first 6 projects
    
    print(f"Found {len(project_links)} project links.")
    project_list = []

    for link in project_links:
        detail_page_link = link['href']
        detail_page_url = f'{base_url}{detail_page_link}'
        print(f"Scraping details from {detail_page_url}")
        project_details = get_project_details(detail_page_url)
        if project_details:
            project_list.append(project_details)

    if project_list:
        df = pd.DataFrame(project_list)
        df.to_csv('registered_projects.csv', index=False)
        print("Data saved to 'registered_projects.csv'")
    else:
        print("No project data found or scraped.")

if __name__ == '__main__':
    main()
