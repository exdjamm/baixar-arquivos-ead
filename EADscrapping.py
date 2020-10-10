from requests import Session
from bs4 import BeautifulSoup
import os.path
from json import dumps, loads
from filterPages import getDataByDict
from time import sleep

class ScrapEAD(Session):
	"""docstring for ScrapEAD"""
	def __init__(self, username, password):
		super(ScrapEAD, self).__init__()
		self.__courses = {}
		self.__num_of_courses = 0
		self.__filter_courses = ['2020-2', '2020/2', 'F4']

		self.__tasks = {}
		self.__url = "https://ead.ifms.edu.br/"
		self.__ssl_cert = "ead-ifms-edu-br-chain.pem"
		self.headers.update({'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'})
		self.__html_doc = None
		self.__type =  'html.parser'

		self.__username = username
		self.__password = password
		self.__login_token = ""
		self.__session_key = ""

		self._payload = None

		self.__setTaskVar()		
		pass

	def __setTaskVar(self):
		if os.path.exists("tasks.json"):
			self.__exists = True
			self.makeCloneFile('tasks.json')
			with open("tasks.json", 'r') as doc:
				self.__tasks = loads(doc.read())
		else:
			self.__exists = False

	def setSessionKey(self):
		print("[SCRAP]\t\t>> get SessionKey...")
		self.__session_key = getDataByDict(self.__html_doc, tag='a', filter={'data-title':'logout,moodle'}, value='href').split('=')[1]
		#BeautifulSoup(self.__html_doc, self.__type).find("a", {'data-title':'logout,moodle'})["href"].split("=")[1]
		print("[SCRAP]\t\t>> Done")
		pass

	def setToken(self):
		print("[SCRAP]\t\t>> get Token...")
		self.__html_doc = self.get(self.__url, verify=self.__ssl_cert).text
		self.__login_token = getDataByDict(self.__html_doc, tag='input', filter={'name':'logintoken'}, value='value')
		#self.__login_token = BeautifulSoup(self.__html_doc, self.__type).find('input', {'name':'logintoken'}).get("value")
		print("[SCRAP]\t\t>> Done")
		pass

	def setCourses(self):
		print("[SCRAP]\t\t>> filter courses...")
		self._payload = {"sesskey":self.__session_key}
		self.__html_doc =self.get(self.__url+"blocks/custom_course_menu/interface.php", params=self._payload, verify=self.__ssl_cert).text
		tags_a = getDataByDict(self.__html_doc, tag='a', filter={"class":"courselist_course scrollable"}, all=True)
		#tags_a = BeautifulSoup(self.__html_doc, self.__type).find_all('a', {"class":"courselist_course scrollable"})
		for a in tags_a:
			course_name = a.span.string 

			if any(term in course_name for term in self.__filter_courses):
				course_name = course_name.split('-')[-1].strip()
				self.__courses[course_name] = {"link":a['href'], 'tasks':[]}
		print("[SCRAP]\t\t>> Done.")
		pass

	def setCoursesTasks(self):
		print("[SCRAP]\t\t>> make sintax of Task...")
		for course in self.__courses:
			url = self.__courses[course]['link']
			sleep(0.01)
			self.__html_doc = self.get(url).text
			self.__html_doc = BeautifulSoup(self.__html_doc, self.__type)

			if course not in self.__tasks:
				self.__tasks[course] = {'tasks':[]}

			tags = self.__html_doc.find_all(attrs={"class":"instancename"})

			for tag in tags:
				title = tag.get('data-title')
				if title is None:
					title = tag.text

				# task_type = title.split(' ')[-1]
				# title =  task_type + " - " + title.replace(task_type, '')

				if title not in self.__tasks[course]['tasks']:
					
					tarefaUrl = tag.get('href')	
					if tarefaUrl is None:
						tarefaUrl = tag.parent.get('href')
					
					self.__courses[course]['tasks'].append({"title":title, "notes":tarefaUrl})
					self.__tasks[course]['tasks'].append(title)
			else : 
				for section in range(len(self.__html_doc.find_all(attrs={'class':'tile'}))):
					self.__html_doc = self.get(url + f"&section={section}").text
					self.__html_doc = BeautifulSoup(self.__html_doc, self.__type)
					# print(self.__html_doc.find_all(attrs={'class':'tile'})[section].text)
					tags = self.__html_doc.find_all(attrs={"class":"instancename"})
					for tag in tags:
						title = tag.get('data-title')
						if title is None:
							title = tag.text

						# task_type = title.split(' ')[-1]
						# title =  task_type + " - " + title.replace(task_type, '')

						if title not in self.__tasks[course]['tasks']:
							
							tarefaUrl = tag.get('href')	
							if tarefaUrl is None:
								tarefaUrl = tag.parent.get('href')
							
							self.__courses[course]['tasks'].append({"title":title, "notes":tarefaUrl})
							self.__tasks[course]['tasks'].append(title)
			
		
		print("[SCRAP]\t\t>> Done")
		pass

	def login(self):
		print("[SCRAP]\t\t>> login...")
		self._payload = {"username":self.__username, "password":self.__password, "logintoken":self.__login_token}
		self.__html_doc = self.post(self.__url+'login/index.php', data=self._payload, verify=self.__ssl_cert).text
		print("[SCRAP]\t\t>> Done")
		self.get('https://ead.ifms.edu.br/?canceljssession=1')
		pass

	def getCourses(self):
		print("[SCRAP]\t\t>> returning courses...")
		self.saveTaskJSON()
		print("[SCRAP]\t\t>> Done")
		return self.__courses

	def makeCloneFile(self, file):
		with open(file, 'r') as original:
			with open('copy.json', 'w') as copy:
				copy.write(dumps(loads(original.read())))


	def saveTaskJSON(self):
		print("[SCRAP]\t\t>> Saving task.json...")
		with open("tasks.json", 'w') as doc:
			doc.write(dumps(self.__tasks))
		print("[SCRAP]\t\t>> Done")
		pass

if __name__ == '__main__':
	login = input("Digite o seu login >>> ")
	senha = input("Digite a sua senha >>> ")
	main =  ScrapEAD(login, senha)
	main.setToken()
	main.login()
	main.setSessionKey()
	main.setCourses()
	main.setCoursesTasks()
	main.saveTaskJSON()
	courses = main.getCourses()
	for course in courses:
		for task in courses[course]['tasks']:
			print(str(task['title']))
	#print(res.status_code)