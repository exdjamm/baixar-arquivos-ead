#!/bin/python3.8
# from __future__ import annotations
from requests import Session
from scrap_utils import getDataByDict


# class for files in tasks : fileuploadsubmission

class SessionEad(Session):
	def __init__(self, username: str, password: str) -> None:
		super(SessionEad, self).__init__()

		self.headers.update({'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'})
		self.verify = "ead-ifms-edu-br-chain.pem"

		self._filter_data = getDataByDict

		self.__url_base = "https://ead.ifms.edu.br/"
		self._login_token = str() 
		self._session_key = str()

		self.__login(username, password)
		pass

	def __login(self, username: str, password: str) -> None:
		self.__set_login_token()
		responde_text_login_request = self.__send_login_request(username, password)
		self.__set_session_key(responde_text_login_request)
		
		pass
	
	def _url(self, path=str()) -> str:
		# isso poderia ser feito por uma classe acima?
		url = self.__url_base + path #+ "?"

		return url

	def __set_login_token(self) -> None:
		response_text = self.get(self._url(), ).text
		login_token = self._filter_data(response_text, tag="input", filters={"name":"login_token"}, value="value")

		self._login_token = login_token
		pass

	def __set_session_key(self, to_filter_text: str) -> None:
		session_key = getDataByDict(to_filter_text, tag='a', filter={'data-title':'logout,moodle'}, value='href').split('=')[1]
		
		self._session_key = session_key
		pass
	
	def __send_login_request(self, username: str, password: str) -> str:
		payload = {"username":username, "password":password, "logintoken":self._login_token}
		responde_text = self.post(self._url("login/index.php"), data=payload).text

		return responde_text


if __name__ == '__main__':
	login = input("Digite o seu login >>> ")
	senha = input("Digite a sua senha >>> ")
	main =  SessionEad(login, senha)
