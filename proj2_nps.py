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
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
headers = {'User-Agent': 'UMSI 507 Course Project - Python Web Scraping','From': 'sryanlee@umich.edu','Course-Info': 'https://www.si.umich.edu/programs/courses/507'}
API_KEY = secrets.API_KEY


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

    nat_parks_html = make_url_request_using_cache('https://www.nps.gov/index.htm', CACHE_DICT)
    soup = bs(nat_parks_html, 'html.parser')

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
    site_html = make_url_request_using_cache(site_url, CACHE_DICT)
    site_bs = bs(site_html, 'html.parser')

    site_attrs = {}
    title_parent = site_bs.find('div', class_='Hero-titleContainer clearfix')

    name_a = title_parent.find('a', class_='Hero-title')
    name = name_a.text.strip()
    site_attrs['name'] = name

    category = title_parent.find('span', class_='Hero-designation').text.strip()
    site_attrs['category'] = category

    footer_parent = site_bs.find('div', class_='ParkFooter-contact')
    footer_spans = footer_parent.find_all('span')

    for span in footer_spans:
        if span.get('itemprop') is not None:
            #if 'streetAddress' in span.get('itemprop'):
            #    site_attrs.append({'street_address': span.text.strip('\n')})
            if 'addressLocality' in span['itemprop']:
                site_attrs['city'] = span.text
            elif 'addressRegion' in span['itemprop']:
                site_attrs['state'] = span.text
            elif 'postalCode' in span['itemprop']:
                site_attrs['postal_code'] = span.text.strip()
            elif 'telephone' in span['itemprop']:
                site_attrs['telephone'] = span.text.strip('\n')
    #print(site_attrs)

    sitename = site_attrs['name']
    site_cat = site_attrs['category']
    if 'city' and 'postal_code' in site_attrs.keys():
        site_address = f"{site_attrs['city']}, {site_attrs['state']}"
        site_zipcode = site_attrs['postal_code']
    else:
        site_address = 'UNAVAILABLE'
        site_zipcode = ''
    if 'telephone' in site_attrs.keys():
        site_phone = site_attrs['telephone']
    else:
        site_phone = 'UNAVAILABLE'

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
    
    state_home_html = make_url_request_using_cache(state_url, CACHE_DICT)
    state_home_bs = bs(state_home_html, 'html.parser')

    state_sites_parent = state_home_bs.find('div', id='parkListResultsArea')
    state_site_lis = state_sites_parent.find_all('li')

    site_instances = []
    for state_site_li in state_site_lis:
        site_div = state_site_li.find('div', class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
        if site_div is not None:
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
    resource_url = 'http://www.mapquestapi.com/search/v2/radius'
    params = {
        'origin': site_object.address,
        'radius': 10,
        'maxMatches': 10,
        'ambiguities': 'ignore',
        'outFormat': 'json',
        'key': API_KEY
    }
    response_url = requests.get(resource_url, params=params).url
    #print(response_url)
    response = make_url_request_using_cache(response_url, CACHE_DICT)
    #print(response)
    search_results = json.loads(response)['searchResults']

    results_dict = {}

    for result in search_results:
        result_info = {}
        result_info['resultCount'] = result['resultNumber']
        result_info['name'] = result['name']
        result_info['category'] = result['fields']['group_sic_code_name_ext']
        result_info['address'] = result['fields']['address']
        result_info['city'] = result['fields']['city']

        for k,v in result_info.items():
            if k != 'name':
                if v is None:
                    result_info[k] == f'no {k}'
        results_dict[result['name']] = result_info
    #print(results_dict)
    return results_dict


def print_state_sites(state, site_instances):
    '''Prints numbered national site names, categories, and address details

    Parameters
    ----------
    site_instances: list
        a list of National Site instances

    Returns
    -------
    None
    '''
    print('-------------------------------------------')
    print(f'LIST OF NATIONAL SITES IN {state.upper()}')
    print('-------------------------------------------')
    i = 1
    for instance in site_instances:
        string = f'[{i}] {instance.info()}\n'
        print(string)
        i += 1


def print_nearby_places(nearby_places_dict, site_instance):
    '''Prints formatted name, category, address, and city of MapQuest API search results.

    Parameters
    ----------
    search_results: dictionary
        dictionary containing dictionaries of places nearby a national site
    site_instance: object
        NationalSite instance

    Returns
    -------
    None
    '''

    print('---------------------------------------------------------')
    print(f'PLACES NEARBY {site_instance.name.upper()} NATIONAL SITE')
    print('---------------------------------------------------------')
    for k,v in nearby_places_dict.items():
        print(f"- {k} ({v['category']}): {v['address']}, {v['city']}")


def load_cache():
    '''Tries to read and load cache file into a local dictionary.
    If unsuccessful, local dictionary remains empty.

    Parameters
    ----------
    None

    Returns
    -------
    chache: dictionary
        a dictionary containing the cache file
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    '''Adds new information to the saved cache file.

    Parameters
    ----------
    cache : dictionary
        local cache dictionary

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache, params=None):
    '''Makes a request to data saved in the local cache or directly from the webpage,
    depending on if url already exists within the cache.

    Parameters
    ----------
    url: string
        url for the requested webpage
    cache: dictionary
        local cache dictionary

    Returns
    -------
    cache[url]: string
        html code saved in the cache associated with the given url
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        if params is not None:
            print("Fetching")
            response = requests.get(url, params=params, headers=headers)
            cache[response.url] = response.text
            save_cache(cache)
            return cache[response.url]
        else:
            print("Fetching")
            response = requests.get(url, headers=headers)
            cache[response.url] = response.text
            save_cache(cache)
            return cache[response.url]



if __name__ == "__main__":

    # Load the cache, save in global variable
    CACHE_DICT = load_cache()

    # build url dict
    state_url_dict = build_state_url_dict()
    #print(state_url_dict['michigan'])

    # get user input, normalize, and validate
    state_input = ''
    while state_input not in state_url_dict.keys():
        state_input = input('Please enter the name of a US state or "exit":\n')
        if state_input.lower().strip() == 'exit':
            print("closing")
            break
        elif state_input.lower().strip() in state_url_dict.keys():
            state = state_input.lower().strip()

            state_sites = get_sites_for_state(state_url_dict[state])
            print_state_sites(state, state_sites)

            adv_search = input('For advanced search: select the number of a site. Otherwise enter "exit" or "back" \n')
            if adv_search.lower().strip() == 'exit':
                print("closing")
                pass
            elif adv_search.lower().strip() == 'back':
                print(f"previous entry: {state_input}")
                continue
            elif int(adv_search) in range(len(state_sites)):
                choice_num = int(adv_search) - 1
                places = get_nearby_places(state_sites[choice_num])
                print_nearby_places(places, state_sites[choice_num])
            else:
                print("[Error] invalid selection")
        else:
            print("[Error] invalid state name")




