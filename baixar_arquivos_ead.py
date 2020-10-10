#!/bin/python3
from requests import Response
import subprocess as run
from json import loads as carregar
from eadapi import SessionEad
from scrap_utils import getDataByDict as pegar_dados_por_dicionario
from time import sleep as dormir
import os.path as path
from EADscrapping import ScrapEAD

run_bash = run.run
caminho_de_base = str()
username = str()
password = str()
cursos = dict()
# numeros = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
# coisa do link que vais ser um arquivo : resource

mensagem = """Crie o arquivo 'login' com as seguintes informações:
- caminho onde ira salvar os arquivos
- login do usuario
- senha do usuario

Ex:
/home/user/desktop
username
passoword
""" 

def pegar_informacoes_do_usuario() -> bool:
    global caminho_de_base
    global username
    global password

    if path.exists('login'):
        with open('login', 'r') as dados_usuario:
            dados_lista	= dados_usuario.readlines()
            
            for (linha, i) in zip(dados_lista, range(len(dados_lista))):
                dados_lista[i] = linha.replace("\n", '')

            print(dados_lista)

            if len(dados_lista) < 3:
                print("Quantidades de dados insuficiente!")
                print(mensagem) 
                return False

            if not path.exists(dados_lista[0]):
                print("Caminho forcencido não aceitavel!")
                return False
            else:
                caminho_de_base = dados_lista[0]
                # print(caminho_de_base)

            username = dados_lista[1]
            password = dados_lista[2]

        return True

    else:
        print(mensagem)
        return False
			

def criar_pasta_em_desktop(path: str) -> None:
    # print(caminho_de_base)
    # print(f'mkdir -p "{caminho_de_base}/{path}"')
    run_bash([f'mkdir -p "{caminho_de_base}/{path}"'], shell=True)

    pass

def baixar_arquivos_da_tarefa(resposta: Response, caminho_do_curso: str, titulo_tarefa: str) -> None:   
    html_da_resposta = resposta.text
    
    tags = pegar_dados_por_dicionario(html_da_resposta, tag='div', filter={'class':'fileuploadsubmission'}, all=True)
    # print(tags)
    for tag_do_arquivo in tags:
        tag_de_links = tag_do_arquivo.find('a')
        link_de_download = tag_de_links.get('href')
        titulo_do_arquivo = tag_de_links.text.replace(' ', '-').replace('/', '-').replace("\\","-" ) 

        r = pegar_resposta_do_pedido_de_link(link_de_download)
        if (r.status_code == 200) and (not path.exists(f"{caminho_de_base}/{caminho_do_curso}/{titulo_tarefa}/{titulo_do_arquivo}")):
            with open(f"{caminho_de_base}/{caminho_do_curso}/{titulo_tarefa}/{titulo_do_arquivo}", 'wb') as doc:
                doc.write(r.content)
                print(f"Baixado o arquivo '{titulo_do_arquivo}'")

    
    pass

def baixar_arquivos_da_pagina_do_curso(link: str, pasta_do_curso: str, titulo_da_tarefa: str) -> None:
    link = link + "?forcedownload=1"

    r = pegar_resposta_do_pedido_de_link(link)

    if (r.status_code == 200) and (not path.exists(f"{caminho_de_base}/{pasta_do_curso}/{titulo_da_tarefa}")):
        # print(f"{caminho_de_base}/{pasta_do_curso}/{titulo_da_tarefa}")
        with open(f"{caminho_de_base}/{pasta_do_curso}/{titulo_da_tarefa}", 'wb') as doc:
            doc.write(r.content)
            print(f"Baixado o arquivo '{titulo_da_tarefa}'")
    pass

def pegar_resposta_do_pedido_de_link(link: str) -> Response:
    resposta_pedido = session.get(link, stream=True)
    
    return resposta_pedido

def definir_cursos():
    global cursos
    main =  ScrapEAD(username, passoword)
    main.setToken()
    main.login()
    main.setSessionKey()
    main.setCourses()
    main.setCoursesTasks()
    main.saveTaskJSON()
    cursos = main.getCourses()

    pass

def main() -> None:
    global session
    global cursos

    # print(caminho_de_base)
    if not pegar_informacoes_do_usuario():
        return None

    try:
        session =  SessionEad(username, password)
    except Exception :
        print("Seu login está errado, por favor verifique!")
        return None

    # pegar_links()

    # with open("./courses.json", 'r') as json:
    #     cursos = carregar(json.read())

    for curso in cursos:

        sigla_do_curso = str()
        for parte_nome_do_curso in curso.split(' '):
            primeira_4_letras_nome_do_curso = parte_nome_do_curso[:3] 

            letras_adicionadas_a_sliga = primeira_4_letras_nome_do_curso

            sigla_do_curso += letras_adicionadas_a_sliga

        criar_pasta_em_desktop(sigla_do_curso)

        dados_do_curso = cursos[curso]
        tarefas_do_curso = dados_do_curso['tasks']

        for dados_da_tarefa_do_curso in tarefas_do_curso:
            link_da_tarefa = dados_da_tarefa_do_curso['link'] if dados_da_tarefa_do_curso['link'] is not None else "sem link"
            titulo_da_tarefa = dados_da_tarefa_do_curso['title'].replace(' ', '-').replace('/', '-').replace("\\","-" ).replace(':', '').replace('?', '').replace('&', '').replace('*', '')

            if "sem link" not in link_da_tarefa :
                e_link_tarefa = False
                
                if "url" in link_da_tarefa:
                    # print("LinkExternoErrorSSL")
                    continue

                if "assign" in link_da_tarefa:
                    # print("LinkTarefa")
                    e_link_tarefa = True

                if "resource" not in link_da_tarefa:
                    # print("NaoBaixavelConteudo")
                    if not e_link_tarefa:
                        continue
                
                
                print(f"{sigla_do_curso} -> {link_da_tarefa}")
    
                if not e_link_tarefa:
                    baixar_arquivos_da_pagina_do_curso(link_da_tarefa, sigla_do_curso, titulo_da_tarefa)
                else:
                    criar_pasta_em_desktop(f"{sigla_do_curso}/{titulo_da_tarefa}")
                    resposta_do_pedido_do_link = pegar_resposta_do_pedido_de_link(link_da_tarefa)
                    baixar_arquivos_da_tarefa(resposta_do_pedido_do_link, sigla_do_curso, titulo_da_tarefa)
                dormir(0.5)


    pass

if __name__ == "__main__":
    main()
