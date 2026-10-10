"""Sistema de Análise de Dados.

Lê um arquivo CSV com as colunas email, cpf, telefone e data, valida cada
campo com expressões regulares (módulo re), trata os erros com
try/except/else/finally e gera o relatório final com f-strings.

Uso:
    python analise_dados.py              (lê o dados.csv)
    python analise_dados.py outro.csv    (lê outro arquivo)
"""

import csv
import re
import sys
from datetime import datetime

ARQUIVO_PADRAO = "dados.csv"
ARQUIVO_RELATORIO = "relatorio.txt"
COLUNAS_OBRIGATORIAS = ("email", "cpf", "telefone", "data")


PADRAO_EMAIL = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"
PADRAO_CPF = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
PADRAO_TELEFONE = r"^\(\d{2}\)\s\d{4,5}-\d{4}$"
PADRAO_DATA = r"^\d{2}/\d{2}/\d{4}$"



class FormatoInvalidoError(Exception):
    """Algum campo do registro está fora do formato esperado."""

    def __init__(self):
        super().__init__("Um ou mais campos possuem formato inválido.")



def _texto_limpo(valor):
    """Converte para texto e tira espaços das pontas (None vira vazio)."""
    return str(valor or "").strip()


def validar_email(valor):
    """True se o e-mail tem o formato usuario@dominio.sufixo."""
    return re.match(PADRAO_EMAIL, _texto_limpo(valor)) is not None


def validar_cpf(valor):
    """True se o CPF está no formato 000.000.000-00."""
    return re.match(PADRAO_CPF, _texto_limpo(valor)) is not None


def validar_telefone(valor):
    """True se o telefone está no formato (00) 90000-0000 ou (00) 0000-0000."""
    return re.match(PADRAO_TELEFONE, _texto_limpo(valor)) is not None


def validar_data(valor):
    """True se a data está no formato dd/mm/aaaa e realmente existe."""
    texto = _texto_limpo(valor)
    if re.match(PADRAO_DATA, texto) is None:
        return False
    try:
        datetime.strptime(texto, "%d/%m/%Y")
    except ValueError:
        
        return False
    return True


VALIDADORES = {
    "email": validar_email,
    "cpf": validar_cpf,
    "telefone": validar_telefone,
    "data": validar_data,
}


def validar_registro(registro):
    """Valida um registro; levanta FormatoInvalidoError se algo estiver errado.

    KeyError -> a coluna não existe no registro
    """
    if None in registro:
        
        raise FormatoInvalidoError()

    for campo, validador in VALIDADORES.items():
        valor = registro[campo]  
        if not validador(valor):
            raise FormatoInvalidoError()



def ler_registros(caminho):
    """Lê o CSV e devolve uma lista de dicionários (um por linha).

    FileNotFoundError -> arquivo não existe
    KeyError          -> falta alguma coluna obrigatória no cabeçalho
    """
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas_do_arquivo = leitor.fieldnames or []
        for coluna in COLUNAS_OBRIGATORIAS:
            if coluna not in colunas_do_arquivo:
                raise KeyError(coluna)
        return list(leitor)


def analisar_registros(registros):
    """Devolve uma lista de (identificador, é_válido, motivo)."""
    resultados = []

    for registro in registros:
        identificador = _texto_limpo(registro["email"])
        try:
            validar_registro(registro)
        except FormatoInvalidoError as erro:
            resultados.append((identificador, False, str(erro)))
        else:
            resultados.append((identificador, True, ""))

    return resultados



def gerar_relatorio(resultados):
    """Monta o texto do relatório final."""
    total_validos = sum(1 for _, valido, _ in resultados if valido)
    total_invalidos = len(resultados) - total_validos

    linhas = [
        "===== RELATÓRIO FINAL =====",
        f"Registros válidos: {total_validos}",
        f"Registros inválidos: {total_invalidos}",
    ]
    for identificador, valido, motivo in resultados:
        if valido:
            linhas.append(f"{identificador} - Válido")
        else:
            linhas.append(f"{identificador} - Inválido: {motivo}")

    return "\n".join(linhas)


def salvar_relatorio(texto, caminho=ARQUIVO_RELATORIO):
    """Grava o relatório em um arquivo de texto."""
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto + "\n")
    except OSError as erro:
        print(f"Não foi possível salvar o relatório: {erro}")
    else:
        print(f"\nRelatório salvo em '{caminho}'.")



def main():
    """Lê o arquivo, analisa os dados e mostra o relatório."""
    caminho = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_PADRAO
    print(f"Lendo o arquivo: {caminho}\n")

    try:
        registros = ler_registros(caminho)
        resultados = analisar_registros(registros)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não foi encontrado.")
    except KeyError as erro:
        print(f"Erro: coluna ausente no CSV: {erro}")
    else:
        relatorio = gerar_relatorio(resultados)
        print(relatorio)
        salvar_relatorio(relatorio)
    finally:
        print("\nAnálise finalizada.")


if __name__ == "__main__":
    main()