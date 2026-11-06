# RPA Challenge — Power Automate Desktop e Python

Duas implementações para preencher as dez rodadas do [RPA Challenge](https://rpachallenge.com/) com os dados da planilha disponibilizada pelo próprio site.

## Estrutura

- `power-automate/fluxo.txt`: ações copiáveis para o Power Automate Desktop, incluindo os seletores dos elementos web.
- `python/challenge.py`: implementação em Python com Selenium e leitura de Excel via openpyxl.
- `tests/`: testes locais da leitura e do registro de resultados do Python com navegador simulado.

As duas versões leem os primeiros dez registros da planilha, encontram os campos por atributos estáveis e produzem um log de etapas, um resultado por registro com data/hora e uma captura da tela final com a pontuação. Uma falha durante o preenchimento interrompe as rodadas para não associar a linha seguinte à rodada errada.

**Significado de OK:** a automação concluiu a ação de envio; isso não é uma confirmação independente de que todos os valores foram avaliados como corretos pelo site. A avaliação global está na captura final. No Python, o avanço da rodada também é observado antes de registrar OK.

## Preparação

1. Instale Google Chrome e baixe `challenge.xlsx` no site do desafio. Use a planilha original, com os sete cabeçalhos: First Name, Last Name, Company Name, Role in Company, Address, Email e Phone Number.
2. As versões processam os primeiros dez registros. A planilha não é incluída no repositório.

## Power Automate Desktop

1. Instale o Power Automate Desktop, o Excel para Windows e a extensão oficial do Power Automate para Chrome (ou configure o WebDriver suportado pelo Power Automate).
2. Crie um fluxo de desktop vazio. Abra `power-automate/fluxo.txt`, copie todo o conteúdo e cole no painel central do editor. Os elementos web são incluídos no texto.
3. Na ação **Iniciar o Excel**, ajuste o caminho da planilha. O exemplo aponta para `C:\Users\User\Downloads\challenge.xlsx` e precisa refletir o seu computador.
4. Salve e execute o fluxo. As ações de preenchimento usam inserção direta, sem simular a digitação de cada caractere. Os arquivos são criados em `Documentos\RPA-Challenge`.

O arquivo é uma representação de ações para colar no editor; não é um pacote de solução `.zip`. O editor reconheceu as ações e seus elementos, mas o fluxo atualizado não foi executado automaticamente neste projeto. Teste a execução e confirme a pontuação na captura gerada.

## Python + Selenium

Requer Python 3.10 ou posterior e Chrome instalado. O Selenium Manager pode obter um driver compatível automaticamente na primeira execução.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python python\challenge.py --excel "$env:USERPROFILE\Downloads\challenge.xlsx"
```

Opcionalmente use `--output resultados/python` e `--timeout 15`. O Selenium abre o Chrome, preenche os sete campos em uma chamada ao navegador por rodada e aguarda o avanço antes de continuar. A pasta de saída recebe `etapas_*.log`, `resultados_*.csv` e, somente quando o resultado final estiver visível, `resultado_final_*.png`.

## Testes locais

```powershell
python -m unittest discover -s tests -v
```

Os testes usam um navegador simulado; não enviam o formulário nem verificam a pontuação real. O desempenho e o comportamento no site devem ser conferidos em uma execução real.
