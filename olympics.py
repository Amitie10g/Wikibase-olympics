#!/usr/bin/env python3
import requests, json, pywikibot, luadata
from os.path import exists
from pywikibot.page import Page

# Variables
site				= pywikibot.Site('wikipedia:es')
wiki				= 'eswiki'
instanceOf	= 'Q26213387' # Olympics
#instanceOf	= 'Q46195901' # Paralympics

# Modules
if instanceOf == 'Q46195901':
	wholeDataModule				= 'Módulo:Ficha de país en los Juegos Olímpicos/Juegos Paralímpicos/datos'
	participedDataModule	= 'Módulo:Ficha de país en los Juegos Olímpicos/Juegos Paralímpicos/participaciones'
else:
	wholeDataModule				= 'Módulo:Ficha de país en los Juegos Olímpicos/Juegos Olímpicos/datos'
	participedDataModule	= 'Módulo:Ficha de país en los Juegos Olímpicos/Juegos Olímpicos/participaciones'

# Localisation
summer	= 'verano'
winter	= 'invierno'
at			= ' en los '

repo = site.data_repository()

url = 'https://query.wikidata.org/sparql'
query = """SELECT DISTINCT ?item WHERE {
		?item p:P31 ?statement0.
		?statement0 (ps:P31) wd:%s.
}""" % (instanceOf)

r = requests.get(url, params = {'format': 'json', 'query': query})
parsed = []
data = r.json()
data = data['results']['bindings']

wholeData				= {}
participedData	= {}
count = 0
for f in data:
	value = {}
	itemID = f['item']['value'].replace('http://www.wikidata.org/entity/', '')

	item = pywikibot.ItemPage(repo, itemID)
	item.get()

	# Sitelink
	if item.sitelinks:
		if wiki in item.sitelinks:
			value['sitelink'] = item.sitelinks[wiki].toJSON()['title']

			# Country
			if 'P17' in item.claims:
				if 'P984' in item.claims['P17'][0].getTarget().claims and wiki in item.claims['P17'][0].getTarget().sitelinks:
					ICO = item.claims['P17'][0].getTarget().claims['P984'][0].toJSON()['mainsnak']['datavalue']['value']
					countryID = 'Q' + str(item.claims['P17'][0].toJSON()['mainsnak']['datavalue']['value']['numeric-id'])
					countryTitle = item.claims['P17'][0].getTarget().sitelinks[wiki].toJSON()['title']

					# Participed in (P1334)
					if item.claims:
						if 'P1344' in item.claims:
							participedInObj = item.claims['P1344'][0].getTarget().claims
							if wiki in item.claims['P1344'][0].getTarget().sitelinks:
								participedIn	= item.claims['P1344'][0].getTarget().sitelinks[wiki].toJSON()['title']

								# Participed in -> Date (P585) (year)
								if 'P585' in participedInObj:
									year = participedInObj['P585'][-1].getTarget().year

									# Participed in -> Instance of (P31)
									if 'P31' in participedInObj:
										eventClassID = participedInObj['P31'][0].toJSON()['mainsnak']['datavalue']['value']['numeric-id']
										if eventClassID == 159821 or eventClassID == 3327913:
											eventClass = summer + ' ' + str(year)
											eventClassKey = 0
										elif eventClassID == 82414 or eventClassID == 3317976:
											eventClass = winter + ' ' + str(year)
											eventClassKey = 1
										else:
											continue

										# ICO
										if ICO:
											value['ICO'] = ICO

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
												value['delegation'] = item.claims['PXX'][0].getTarget().sitelinks[wiki].toJSON()['title']
											elif 'P179' in item.claims: # series
												if 'PXX' in item.claims['P179'][0].getTarget().claims:
													value['delegation'] =   item.claims['P179'][0].getTarget().claims['PXX'][0].getTarget().sitelinks[wiki].toJSON()['title']

											# Set tables
											if not ICO in wholeData:
												wholeData[countryID] = {}

											if not countryID in participedData:
												participedData[countryID] = {}
												participedData[countryID][0] = {}
												participedData[countryID][1] = {}

											if not eventClass in wholeData[countryID]:
												wholeData[countryID][eventClass] = {}

											# Fill final tables
											wholeData[countryID][eventClass] = value

											if participedIn:
												participedData[countryID][eventClassKey][year] = "[[" + countryTitle + at + participedIn +"|" + str(year) + "]]"
											else:
												participedData[countryID][eventClassKey][year] = str(year)

wholeDataModuleObj = Page(site,wholeDataModule)
wholeDataModuleObj.text='return ' + luadata.serialize(wholeData, encoding="utf-8", indent="\t")
wholeDataModuleObj.save("test (using [[mw:Special:MyLanguage/Manual:Pywikibot|pywikibot]])")

participedDataModuleObj = Page(site, participedDataModule)
participedDataModuleObj.text='return ' + luadata.serialize(participedData, encoding="utf-8", indent="\t")
participedDataModuleObj.save("test (using [[mw:Special:MyLanguage/Manual:Pywikibot|pywikibot]])")
