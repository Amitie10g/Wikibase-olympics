#!/usr/bin/env python3
import requests, json, pywikibot, luadata
from os.path import exists
from pywikibot.page import Page

# Variables
summer		= os.environ['SUMMER'] or 'verano'
winter		= os.environ['WINTER'] or 'invierno'
tableModule	= os.environ['MODULE'] or 'Módulo:Ficha de país en los Juegos Olímpicos/datos'
siteValue	= os.environ['SITE']   or 'wikipedia:es'

# Setup
site		= pywikibot.Site(siteValue)
repo = site.data_repository()

# Query
url = 'https://query.wikidata.org/sparql'
query = """SELECT DISTINCT ?item WHERE {
	?item p:P31 ?statement0.
	?statement0 (ps:P31) wd:Q26213387.
}"""
r = requests.get(url, params = {'format': 'json', 'query': query})
parsed = []
data = r.json()
data = data['results']['bindings']

# Parse
result = {}
for f in data:
	value = {}
	itemID = f['item']['value'].replace('http://www.wikidata.org/entity/', '')

	item = pywikibot.ItemPage(repo, itemID)
	item.get()

	# Sitelink
	if item.sitelinks:
		if 'eswiki' in item.sitelinks:
			value['sitelink'] = item.sitelinks['eswiki'].toJSON()['title']

			# Country
			if 'P17' in item.claims:
				if 'P984' in item.claims['P17'][0].getTarget().claims:
					ICO = item.claims['P17'][0].getTarget().claims['P984'][0].toJSON()['mainsnak']['datavalue']['value']

					# Participed in (P1334)
					if item.claims:
						if 'P1344' in item.claims:
							participedIn = item.claims['P1344'][0].getTarget().claims

							# Participed in -> Date (P585) (year)
							if 'P585' in participedIn:
								year = participedIn['P585'][-1].getTarget().year

								# Participed in -> Instance of (P31)
								if 'P31' in participedIn:
									eventClassID = participedIn['P31'][0].toJSON()['mainsnak']['datavalue']['value']['numeric-id']
									if eventClassID == 159821:
										eventClass = summer + ' ' + str(year)
									elif eventClassID == 82414:
										eventClass = winter + ' ' + str(year)
									else:
										continue

									# Flag -> P18 or P41
									if 'P18' in item.claims: # item
										value['flag'] = 'File:' + item.claims['P18'][0].toJSON()['mainsnak']['datavalue']['value']
									elif 'P41' in item.claims: # item
										value['flag'] = 'File:' + item.claims['P41'][0].toJSON()['mainsnak']['datavalue']['value']
									elif 'P17' in item.claims: # country
										if 'P18' in item.claims['P17'][0].getTarget().claims:
											value['flag'] = 'File:' + item.claims['P17'][0].getTarget().claims['P18'][0].toJSON()['mainsnak']['datavalue']['value']
										elif 'P41' in item.claims['P17'][0].getTarget().claims:
											value['flag'] = 'File:' + item.claims['P17'][0].getTarget().claims['P41'][0].toJSON()['mainsnak']['datavalue']['value']
									elif 'P179' in item.claims: # series
										if 'P18' in item.claims['P179'][0].getTarget().claims:
											value['flag'] = 'File:' + item.claims['P179'][0].getTarget().claims['P18'][0].toJSON()['mainsnak']['datavalue']['value']
										elif 'P41' in item.claims['P179'][0].getTarget().claims:
											value['flag'] = 'File:' + item.claims['P179'][0].getTarget().claims['P41'][0].toJSON()['mainsnak']['datavalue']['value']

									# Delegation (pending until property creation)
									if 'PXX' in item.claims: # item
										value['delegation'] = item.claims['PXX'][0].getTarget().sitelinks['eswiki'].toJSON()['title']
									elif 'P179' in item.claims: # series
										if 'PXX' in item.claims['P179'][0].getTarget().claims:
											value['delegation'] =   item.claims['P179'][0].getTarget().claims['PXX'][0].getTarget().sitelinks['eswiki'].toJSON()['title']

									if not ICO in result:
										result[ICO] = {}

									if not eventClass in result[ICO]:
										result[ICO][eventClass] = {}

									result[ICO][eventClass] = value

# Edit module
Module = Page(site,tableModule)
Module.text = 'return ' + luadata.serialize(result, encoding="utf-8", indent="\t")
Module.save("test (using [[mw:Special:MyLanguage/Manual:Pywikibot|pywikibot]])")
