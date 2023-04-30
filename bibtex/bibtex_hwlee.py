import sys
import os
import requests
from datetime import datetime

if len(sys.argv) > 1 and not sys.argv[1].isnumeric():
  print("Usage: python3 {0} yyyy [file_name]\n       Second argument should be a number(zero for the current year).".format(sys.argv[0]))
  exit(-1)

token="************************************"
current_year = datetime.now().year
if len(sys.argv) > 1:
  current_year = int(sys.argv[1])
if current_year == 0:
  current_year = datetime.now().year
current_month = datetime.now().month
current_month_text = datetime.now().strftime('%h')
author_file_name = "kgwg_authors.dat"
if len(sys.argv) > 2:
  author_file_name = sys.argv[2]
if os.path.exists(author_file_name):
  pass
else:
  print("ERROR- Author list file {0} does not exist, please specify a correct file name.".format(author_file_name))
  exit(-1)

def get_title(bibitem):
  lines = bibitem.split('\n')
  for line in lines:
    if 'title' in line:
      start = line.find('{')
      end = line.find('}')
      title = line[start+1: end]
      return title

def generate_list_item(text_file, bibitem, bibcode):
  text_file.write("<li>")
  text_file.write("<a href='https://ui.adsabs.harvard.edu/#abs/{0}/abstract'>{1}</a>\n".format(bibcode, get_title(bibitem)))
  text_file.write("</li>\n")

def generate_html(year, bibitems, bibcodes):
  html_file = "kgwg_publications_"+str(year)+".html"
  with open(html_file, "w") as text_file:
    text_file.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n<title>Year {0}: List of Publications for KGWG</title></head>\n".format(year))
    text_file.write("<body>\n<h1>List of Publications for KGWG in year {0}</h1>\n".format(year))
    text_file.write("<ol>\n")
    for idx in range(len(bibitems)):
      generate_list_item(text_file, bibitems[idx], bibcodes[idx])
    text_file.write("</ol>\n")
    text_file.write("</body>\n")

def get_bibcodes(author, year):
  url = "https://api.adsabs.harvard.edu/v1/search/query?q=(%3Dauthor%3A%22"+author+"%22%20AND%20year%3A"+str(year)+")&fl=bibcode&rows=200&sort=date%20desc%2C%20bibcode%20desc"
  #query is https://api.adsabs.harvard.edu/v1/search/query?q=(=author:"Lee, H.M." and year:2022)&fl=bibcode&rows=200&sort=date+desc,bibcode+desc

  # the query parameters can be included as part of the URL
  r = requests.get(url, headers={'Authorization': 'Bearer ' + token})
  #print(r.json())
  response = r.json()['response']
  docs = response['docs']
  numbers = response['numFound']
  bibcodes = []
  for idx in range(len(docs)):
    bibcodes.append(docs[idx]['bibcode'])
  return bibcodes

def get_authors(file_name):
  with open(file_name, "r") as author_file:
    lines = author_file.read()
    authors = lines.split('\n')
  authors0 = [author for author in authors if len(author)>0]
  return authors0

def get_bibitems_year(file_name, year):
  bibtex_url = "https://api.adsabs.harvard.edu/v1/export/bibtex"

  authors = get_authors(file_name)
  print("authors = {0}".format(authors))
  bibcodes = []
  for idx in range(len(authors)):
    bibcodes0 = get_bibcodes(authors[idx], year)
    bibcodes = list(set(bibcodes) | set(bibcodes0)) #exclude the same bibcode

  exports = {'bibcode':bibcodes , 'sort':'no sort', 'maxauthor':3}
  bibtex = requests.post(bibtex_url,  headers={'Authorization': 'Bearer ' + token, 'Content-Type':'application/json'}, json=exports)
  #print(bibtex.json())
  print("=====================================================================================================")
  print("     Total {0} bibitems for year {1}".format(len(bibcodes), year))
  print("=====================================================================================================")
  bibitems = bibtex.json()['export']
  bibitems1 = bibitems.split('@')
  bibitems2 = [bibitem for bibitem in bibitems1 if len(bibitem) > 0]
  print("len(bibitems) = {0}, len(bibitems2) = {1}, len(bibcodes) = {2}".format(len(bibitems), len(bibitems2), len(bibcodes)))
  file_name = "kgwg_publications_"+str(year)+"_"+current_month_text+".bib"
  with open(file_name, "w") as text_file:
    text_file.write("{0}".format(bibitems))
  generate_html(year, bibitems2, bibcodes)

for year in range(current_year - 2, current_year+1):
  get_bibitems_year(author_file_name, year)
