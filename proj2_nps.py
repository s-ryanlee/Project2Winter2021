################################
##### Name: Samantha Ryan-Lee
##### Uniqname: sryanlee
#################################

from bs4 import BeautifulSoup as bs
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
     def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''

    nat_parks_html = requests.get('https://www.nps.gov/index.htm')
    soup = bs(nat_parks_html.content, 'html_parser')

    all_a = soup.find_all('a')

    homepage = 'https://www.nps.gov'
    state_urls = []
    for a in all_a:
        if 'state' in a['href']:
            state_url = {a.text.strip().lower(): homepage + a['href']}
            state_urls.append(state_url)

    return state_urls

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    site_html = requests.get(site_url)
    site_bs = bs(site_html.content, 'html.parser')

    title = site_bs.find('title')
    name = title.text.strip(')').split('(')[0]
    category = title.text.strip(')').split('(')[1]

    all_span = isle_royale_bs.find_all('span')

    site_attrs = []
    for span in all_span:
        if span.get('itemprop') is not None:
            if 'addressLocality' in span['itemprop']:
                site_attrs.append({'city': span.text})
            elif 'addressRegion' in span['itemprop']:
                site_attrs.append({'state': span.text})
            elif 'postalCode' in span['itemprop']:
                site_attrs.append({'postal_code': span.text.strip()})
            elif 'telephone' in span['itemprop']:
                site_attrs.append({'telephone': span.text.strip('\n')})

    address = f"{site_attrs[0]['city']}, {site_attrs[1]['state']}"
    zipcode = site_attrs[2]['postal_code']
    phone = site_attrs[3]['telephone']

    return NationalSite(category, name, address, zipcode, phone)


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    pass


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    pass