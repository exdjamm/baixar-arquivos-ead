from json import loads, dumps
import subprocess as run
run_in_bash = run.run

config = dict()

def definir_pasta():
	a = run_in_bash(['zenity --title "Selecione a pasta onde será salvo os arquivos" --width 250 --height 300 --text "Selecione a pasta" --file-selection --directory'], shell=True, capture_output=True)
	
	config['path'] = a.stdout.decode("utf-8").replace('\n', '') 

def definir_login():
	login = dict()

	a = run_in_bash([f'zenity --title "De o nome as pastas" --width 250  --text "Da o nome!!" --forms --separator="," --add-entry="Login" --add-password="Password"'], shell=True, capture_output=True)	
	saida = a.stdout.decode('utf-8').split(',')
	for (i, ble) in zip(saida, ('username', "password")):
		login[ble] = i.replace('\n', '')
	config['login'] = login
	pass

def definir_pastas(materias):
	global configs

	pastass = dict()
	entradas = str()
	for i in materias:
		entradas += " " + f'--add-entry="{i}"'
	a = run_in_bash([f'zenity --title "De o nome as pastas" --width 250 --height 300 --text "Da o nome!!" --forms --separator="," {entradas}'], shell=True, capture_output=True)

	lista = a.stdout.decode("utf-8").split(',')
	for (nome, materia) in zip(lista, materias):
		pastass[materia.replace('\n', '')] = nome.replace('\n', '')

	config['nome_pastas'] = pastass
	save()
	pass

def save():
	# print(config)
	with open("configs.json", 'w') as configs_json:
		configs_json.write(dumps(config))

def main():
	definir_pasta()
	definir_login()
	save()
	pass

def test():
	definir_pasta()
	definir_login()
	definir_pastas(['math', 'pt'])
	
	print(config)
	pass

if __name__ == '__main__':
	test()

