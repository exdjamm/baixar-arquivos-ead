from bs4 import BeautifulSoup
"""
Objetivos:
Mandar um dicionario para filtrar as informaçoes de uma pagina.
tag= , filters={}, value=
e.g

getDataByDict(docHtml, tag='a', filters={'class':'google', id:'123'}) 
R: tag html
getDataByDict(docHtml, tag='a', filters={'class':'google', id:'123'}, value="href")
R: www.example.com 
"""

	
def getDataByDict(html, **filterDict):
	# Use get para evitar erros de não atribuição 
	#filterDict['filter']
	page = BeautifulSoup(html,"html.parser")
	
	nameTag = filterDict.get('tag')
	tagFilter = filterDict.get('filter')

	if nameTag == None:
		if filterDict.get("all"):
			data = page.find_all(attrs=tagFilter)
			return data
		else:
			data = page.find(attrs=tagFilter)
	else:
		if filterDict.get("all"):
			data = page.find_all(nameTag, attrs=tagFilter)
			return data
		else:
			data = page.find(nameTag, attrs=tagFilter)

	if filterDict.get('value') == None:
		return data
	else:
		if filterDict['value'] == 'text':
			dataValue = data.text
		else:
			dataValue = data.get(filterDict['value'])

	return dataValue


if __name__ == '__main__':
	
	page = """<html>
				<a class='teste' id='4321'>Teste 1</a>
				<a class='teste' id='3214'>Teste 2</a>
				<a class='teste' id='1234'>Teste 3</a>
			</html>"""
	print("Class of first tag <a> with class teste:\n" + str(getDataByDict(page, tag='a', filter={'class':"teste"}, value='class')) + "\n")
	print("Id of first tag <a> with class teste\n" + str(getDataByDict(page, filter={'class':"teste"}, value='id')) + "\n")
	print("Text of tag <a> with id 1234 \n" + str(getDataByDict(page, filter={'id':"1234"}, value='text')) + "\n")
	print("Show all tags only\n" + str(getDataByDict(page, tag='a', value='text', all=True)) + "\n")
	print("Show all tags\n" + str(getDataByDict(page, tag='a', all=True)) + "\n")