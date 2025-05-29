import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou coloque o domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def baixar_txt_drive(id_arquivo, nome_saida):
    url = f"https://drive.google.com/uc?export=download&id={id_arquivo}"
    resposta = requests.get(url)
    with open(nome_saida, "wb") as f:
        f.write(resposta.content)


def gerar_html_audios(input_txt, output_txt):
    html_output = [
        "<script>\n"
        "function toggleAlbum(id) {\n"
        "  const div = document.getElementById(id);\n"
        "  div.style.display = div.style.display === 'none' ? 'block' : 'none';\n"
        "}\n"
        "</script>\n\n"
    ]
    artista_album = None
    album_id = 1

    with open(input_txt, "r", encoding="utf-8") as file:
        linhas = [linha.strip() for linha in file if linha.strip()]

    faixa_num = 1
    for linha in linhas:
        if linha.startswith("#"):
            if artista_album is not None:
                html_output.append("</div>\n\n")
            artista_album = linha[1:].strip()
            div_id = f"album{album_id}"
            # Removido busca de capa do álbum
            html_output.append(
                f"<button onclick=\"toggleAlbum('{div_id}')\">Mostrar/Ocultar {artista_album}</button><br>\n"
                f'<div id="{div_id}" style="display:none;">\n'
                f"<h2>{artista_album}</h2>\n"
            )
            album_id += 1
            faixa_num = 1
        else:
            link = linha
            if "/" in link:
                nome_com_extensao = link.split("/")[-1]
                if "." in nome_com_extensao:
                    nome_arquivo = nome_com_extensao.rsplit(".", 1)[0]
                else:
                    nome_arquivo = nome_com_extensao
            else:
                nome_arquivo = f"Faixa {faixa_num}"

            bloco_html = f"""<p>{nome_arquivo}</p>
<audio controls preload="none">
  <source src="{link}" type="audio/ogg; codecs=opus">
</audio>\n"""
            html_output.append(bloco_html)
            faixa_num += 1

    if artista_album is not None:
        html_output.append("</div>\n")

    with open(output_txt, "w", encoding="utf-8") as file:
        file.writelines(html_output)


@app.get("/gerar_html")
def gerar_html(
    id_arquivo: str = Query(..., description="ID do arquivo do Google Drive")
):
    input_txt = "links_dos_arquivos.txt"
    output_txt = "saida.txt"
    baixar_txt_drive(id_arquivo, input_txt)
    gerar_html_audios(input_txt, output_txt)
    return FileResponse(output_txt, filename="saida.txt", media_type="text/plain")
