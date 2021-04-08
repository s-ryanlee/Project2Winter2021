################################
##### Name: Samantha Ryan-Lee
##### Uniqname: sryanlee
#################################

from bs4 import BeautifulSoup as bs
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'
END_URL = 'index.htm'

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
    soup = bs(nat_parks_html.content, 'html.parser')

    all_a = soup.find_all('a')

    homepage = 'https://www.nps.gov'
    state_urls = {}
    for a in all_a:
        if 'state' in a['href']:
            state_urls[a.text.strip().lower()] = homepage + a['href']

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
    site_bs = bs(site_html.text, 'html.parser')

    site_attrs = []
    title_parent = site_bs.find('div', class_='Hero-titleContainer clearfix')

    name_a = title_parent.find('a', class_='Hero-title')
    name = name_a.text.strip()
    site_attrs.append({'name': name})

    category = title_parent.find('span', class_='Hero-designation').text.strip()
    site_attrs.append({'category': category})

    footer_parent = site_bs.find('div', class_='ParkFooter-contact')
    footer_spans = footer_parent.find_all('span')

    for span in footer_spans:
        if span.get('itemprop') is not None:
            #if 'streetAddress' in span.get('itemprop'):
            #    site_attrs.append({'street_address': span.text.strip('\n')})
            if 'addressLocality' in span['itemprop']:
                site_attrs.append({'city': span.text})
            elif 'addressRegion' in span['itemprop']:
                site_attrs.append({'state': span.text})
            elif 'postalCode' in span['itemprop']:
                site_attrs.append({'postal_code': span.text.strip()})
            elif 'telephone' in span['itemprop']:
                site_attrs.append({'telephone': span.text.strip('\n')})
    #print(site_attrs)

    sitename = site_attrs[0]['name']
    site_cat = site_attrs[1]['category']
    site_address = f"{site_attrs[2]['city']}, {site_attrs[3]['state']}"
    site_zipcode = site_attrs[4]['postal_code']
    site_phone = site_attrs[5]['telephone']

    return NationalSite(site_cat, sitename, site_address, site_zipcode, site_phone)



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
    state_home_html = requests.get(state_url)
    state_home_bs = bs(state_home_html.text, 'html.parser')

    state_sites_parent = state_home_bs.find('div', id='parkListResultsArea')
    state_site_lis = state_sites_parent.find_all('li')

    site_instances = []
    for state_site_li in nat_site_lis:
        site_div = state_site_li.find('div', class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
        if site_div is not NOne:
            site_link_tag = site_div.find('a')
            if site_link_tag is not None:
                site_details_path = site_link_tag['href']
                site_details_url = BASE_URL + site_details_path + END_URL
                site_instance = get_site_instance(site_details_url)
                #print(site_instance.info())
                if site_instance is not None:
                    site_instances.append(site_instance)
    return site_instances



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
    # build url dict
    state_url_dict = build_state_url_dict()
    print(state_url_dict['michigan'])

    # get user input, normalize, and validate
    state_input = ''
    while state_input not in state_url_dict.keys():
        state_input = input('Please input the name of a US state:\n')
        state_input = state_input.lower().strip()
        print(state_input)
