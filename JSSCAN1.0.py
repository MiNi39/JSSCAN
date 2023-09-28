#!/usr/bin/env python"
# coding: utf-8
# By MiNi

import requests
import argparse
import sys
import re
import os
import threading
from requests.packages import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import openpyxl

scanned_urls = set()
scanned_subdomains = set()
scanned_deep = set()
script_all =set()
lock = threading.Lock() 
script_directory = os.path.dirname(__file__)
            
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-u", "--url", help="The website")
    parser.add_argument("-c", "--cookie", help="The website cookie")
    parser.add_argument("-f", "--file", help="The file contains url or js")
    parser.add_argument("-ou", "--outputurl", help="Output file name. ")
    parser.add_argument("-os", "--outputsubdomain", help="Output file name. ")
    parser.add_argument("-j", "--js", help="Find in js file", action="store_true")
    parser.add_argument("-d", "--deep", type=int, choices=[1, 2, 3], help="Deep find (1, 2,3)")
    return parser.parse_args()

def extract_URL(JS):
	pattern_raw = r"""
	  (?:"|')                               # Start newline delimiter
	  (
	    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
	    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
	    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
	    |
	    ((?:/|\.\./|\./)                    # Start with /,../,./
	    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
	    [^"'><,;|()]{1,})                   # Rest of the characters can't be
	    |
	    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
	    [a-zA-Z0-9_\-/]{1,}                 # Resource name
	    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
	    (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
	    |
	    ([a-zA-Z0-9_\-]{1,}                 # filename
	    \.(?:php|asp|aspx|jsp|json|
	         action|html|js|txt|xml)             # . + extension
	    (?:\?[^"|']{0,}|))                  # ? mark with parameters
	  )
	  (?:"|')                               # End newline delimiter
	"""
	pattern = re.compile(pattern_raw, re.VERBOSE)
	result = re.finditer(pattern, str(JS))
	if result == None:
		return None
	js_url = []
	return [match.group().strip('"').strip("'") for match in result
		if match.group() not in js_url]

def process_script(script_tag, url, script_array):
    script_src = script_tag.get("src")
    if script_src is None:
        script_content = script_tag.get_text()
		
        script_content = "<html>" + script_content + "</html>"
        nested_scripts = BeautifulSoup(script_content, "html.parser").findAll("script")
        for nested_script in nested_scripts:
            process_script(nested_script, url, script_array)
    else:
        purl = process_url(url, script_src)
        script_array[purl] = Extract_html(purl)
		

def process_script_link(script_tag, url, script_array):
    script_href = script_tag.get("href")
    if script_href is not None:
        script_href_str = str(script_href)
        if script_href_str.endswith(".js"):
            purl = process_url(url, script_href)
            script_array[purl] = Extract_html(purl)
		

	
def Extract_html(URL):
	header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
	"Cookie": args.cookie}
	try:
		raw = requests.get(URL, headers = header, timeout=3, verify=False)
		raw = raw.content.decode("utf-8", "ignore")
		return raw
	except:
		return None

def process_domain_url(URL, re_URL):
	black_url = ["javascript:"]
	URL_raw = urlparse(URL)
	Api_raw = urlparse(re_URL)
	ab_URL = URL_raw.netloc
	host_URL = URL_raw.scheme
	dir_URL = URL_raw.path
	api_URL = Api_raw.path
	if re_URL[0:2] == "//":
		result = host_URL  + "://" + ab_URL+"/"+api_URL
	elif re_URL[0:4] == "http":
		result = re_URL
	elif re_URL[0:2] != "//" and re_URL not in black_url:
		if re_URL[0:1] == "/":
			result = host_URL + "://" + ab_URL + re_URL
		else:
			if re_URL[0:1] == ".":
				if re_URL[0:3] == "../":
					segments = dir_URL.split('/')
					base_dir = '/'.join(segments[:-2])
					result = host_URL + "://" + ab_URL + base_dir + '/' + re_URL[3:]
				else:
					result = host_URL + "://" + ab_URL + re_URL[1:]
			else:
				result = host_URL + "://" + ab_URL + "/" + re_URL
	else:
		result = URL
	return result

def process_url(URL, re_URL):
	black_url = ["javascript:"]
	URL_raw = urlparse(URL)
	ab_URL = URL_raw.netloc
	host_URL = URL_raw.scheme
	dir_URL = URL_raw.path
	if re_URL[0:2] == "//":
		result = host_URL  + ":" + re_URL
	elif re_URL[0:4] == "http":
		result = re_URL
	elif re_URL[0:2] != "//" and re_URL not in black_url:
		if re_URL[0:1] == "/":
			result = host_URL + "://" + ab_URL + re_URL
		else:
			if re_URL[0:1] == ".":
				if re_URL[0:3] == "../":
					segments = dir_URL.split('/')
					base_dir = '/'.join(segments[:-2])
					result = host_URL + "://" + ab_URL + base_dir + '/' + re_URL[3:]
				else:
					result = host_URL + "://" + ab_URL + re_URL[1:]
			else:
				result = host_URL + "://" + ab_URL + "/" + re_URL
	else:
		result = URL
	return result

def crawl_and_explore(url):
    global scanned_urls
    new_urls = find_by_url(url)
    if new_urls is not None:
        with lock:
            scanned_urls.update(new_urls)

def crawl_new_urls(url):
    global scanned_urls
    new_urls = [u for u in scanned_urls if u not in scanned_subdomains]
    if new_urls:
        threads = []
        for new_url in new_urls:
            thread = threading.Thread(target=crawl_and_explore, args=(new_url,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

def find_last(string,str):
	positions = []
	last_position=-1
	while True:
		position = string.find(str,last_position+1)
		if position == -1:break
		last_position = position
		positions.append(position)
	return positions

def http_host(url):
	if url[0:4] == "http":
		return url
	else:
		url = "http"+"://"+url
	return url

def find_by_url(url, js = False,file = False):
	if js == False:
		try:
			print("url:" + url)
		except:
			print("Please specify a URL like https://www.baidu.com")
		html_raw = Extract_html(url)
		# process_url(url, ",".join(html_api))
		if html_raw == None: 
			print("Fail to access " + url)
			return None
		#print(html_raw)
		html_new = "<html>" + html_raw + "</html>"
		html = BeautifulSoup(html_new, "html.parser")
		html_scripts = html.findAll("script")
		script_array = {}
		html_link = html.findAll("link")
        
		if html_link is not None:
			for link in html_link:
				process_script_link(link,url,script_array)
		for html_script in html_scripts:
			process_script(html_script, url, script_array)
		allurls = []
		script_array[url] = html_raw
		for script in script_array:
			if script not in script_all:
				script_all.add(script)
				print("JS调试输出:"+script)
				temp_urls = extract_URL(script_array[script])
				if len(temp_urls) == 0: continue
				for temp_url in temp_urls:
					temp2 = urlparse(temp_url)
					if file == True:
						if not any(temp2.path.endswith(extension) for extension in ['vue','.exe', '.png', '.jpg', '.svg','css','gif']) and '@' not in temp2.path:
							allurls.append(process_domain_url(http_host(url), temp_url))
					else:
						if not any(temp2.path.endswith(extension) for extension in ['vue','.exe', '.png', '.jpg', '.svg','css','gif']) and '@' not in temp2.path:
							allurls.append(process_domain_url(http_host(args.url), temp_url))
					if not any(temp2.path.endswith(extension) for extension in ['vue','gif','css','.exe', '.png', '.jpg', '.svg']) and '@' not in temp2.path:
						allurls.append(process_url(script, temp_url))
		result = []
		for singerurl in allurls:
			url_raw = urlparse(url)
			domain = url_raw.netloc
			positions = find_last(domain, ".")
			miandomain = domain
			if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
			suburl = urlparse(singerurl)
			subdomain = suburl.netloc
			if miandomain in subdomain or subdomain.strip() == "":
				if singerurl.strip() not in result:
					result.append(singerurl)
		return result
	return sorted(set(extract_URL(Extract_html(url)))) or None

def find_subdomain(urls, mainurl):
	url_raw = urlparse(mainurl)
	domain = url_raw.netloc
	miandomain = domain
	positions = find_last(domain, ".")
	if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
	subdomains = []
	for url in urls:
		suburl = urlparse(url)
		subdomain = suburl.netloc
		if subdomain.strip() == "": continue
		if miandomain in subdomain:
			if subdomain not in subdomains:
				subdomains.append(subdomain)
	return subdomains

def is_alive(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "Referer": "https://www.google.com/",
			"Cookie": args.cookie,
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False, verify=False)
        

        status_code = response.status_code
        content_length = len(response.content)

        return status_code, content_length
    except requests.exceptions.RequestException:
        return None, None

def check_url_alive(url, results, lock):
    status_code, content_length = is_alive(url)
    status_code = status_code if status_code is not None else "N/A"
    content_length = content_length if content_length is not None else "N/A"
    
    with lock:
        if status_code == 200:
            print(url + "\033[32m" + f"(Length: {content_length}, Status Code: {status_code})\033[0m")
        else:
            print(f"{url} (Length: {content_length}, Status Code: {status_code})")
        
        results[url] = (status_code, content_length)

def giveresult(urls, domain):
    if urls is None:
        return

    alive_urls = {}
    lock = threading.Lock()

    print("\033[32mFind " + str(len(urls)) + " URL:\033[0m")

    threads = []
    for url in urls:
        thread = threading.Thread(target=check_url_alive, args=(url, alive_urls, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    content_subdomain = ""
    
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["URL", "Status Code", "Content Size"])

    for url, (status_code, content_length) in alive_urls.items():
        content_url = f"{url} (Length: {content_length}, Status Code: {status_code})"
        ws.append([url, status_code, content_length])

    subdomains = find_subdomain(urls, domain)

    print("\nFind " + str(len(subdomains)) + " Subdomain:")
    for subdomain in subdomains:
        content_subdomain += subdomain + "\n"
        print(subdomain)

    if args.outputurl is not None:
        try:
            wb.save(args.outputurl)
            print("\nSaved Excel file with URL details.")
            print("Path:" + args.outputurl)
        except PermissionError:
            print("\033[31mError: Permission denied. Unable to save Excel file.\033[0m")

    print("\nOutput " + str(len(urls)) + " urls")

    if args.outputsubdomain is not None:
        with open(args.outputsubdomain, "a", encoding='utf-8') as fobject:
            fobject.write(content_subdomain)
        print("\nOutput " + str(len(subdomains)) + " subdomains")
        print("Path:" + args.outputsubdomain)

def read_txt_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []
	

if __name__ == "__main__":
	print("""
	   	
       ██╗███████╗███████╗ ██████╗ █████╗ ███╗   ██╗
       ██║██╔════╝██╔════╝██╔════╝██╔══██╗████╗  ██║
       ██║███████╗███████╗██║     ███████║██╔██╗ ██║
  ██   ██║╚════██║╚════██║██║     ██╔══██║██║╚██╗██║
  ╚█████╔╝███████║███████║╚██████╗██║  ██║██║ ╚████║
   ╚════╝ ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
                                                    
						[JSSCAN 1.2/BY: MiNi]
	   						https://github.com/MiNi39/JSSCAN
	""")
	urllib3.disable_warnings()
	args = parse_args()
	
	if args.file is None:
		urls = find_by_url(http_host(args.url))
		if args.deep is None:
			giveresult(urls, args.url)
		elif args.deep == 1:
			scanned_urls.update(urls)
			crawl_new_urls(args.url)
			giveresult(scanned_urls, args.url)
		elif args.deep == 2:
			while True:
				scanned_urls.update(urls)
				crawl_new_urls(args.url)
				all_scanned_urls = scanned_urls.union(scanned_subdomains)
				crawl_new_urls(all_scanned_urls)
				
				if len(all_scanned_urls) == len(scanned_subdomains):
					break
				scanned_subdomains.update(scanned_urls)
			giveresult(all_scanned_urls, args.url)
		elif args.deep == 3:
			while True:

				if urls is not None:
					scanned_urls.update(urls)
				else:
					print("连错错误或页面无数据")
				scanned_deep.update(scanned_urls)
				crawl_new_urls(scanned_urls)
				scanned_subdomains.update(scanned_deep)
				all_scanned_urls = scanned_urls.union(scanned_subdomains)
				if len(all_scanned_urls) == len(scanned_subdomains):
					break
				

			giveresult(all_scanned_urls, args.url)

			
		

