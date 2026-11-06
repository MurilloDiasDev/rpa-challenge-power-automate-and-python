# RPA Challenge — Power Automate Desktop e Python

Duas implementações para preencher as dez rodadas do [RPA Challenge](https://rpachallenge.com/) com os dados da planilha disponibilizada pelo próprio site.

## Estrutura

- `power-automate/fluxo.txt`: ações copiáveis para o Power Automate Desktop, incluindo os seletores dos elementos web.
- `python/challenge.py`: implementação em Python com Selenium e leitura de Excel via Pandas (usando openpyxl como mecanismo de leitura).
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
4. Na barra inferior do editor, ajuste **Atraso na execução** para **1 ms** (mínimo aceito). Essa configuração controla a pausa entre ações na execução pelo editor e não faz parte do texto de ações em `fluxo.txt`.
5. Salve e execute o fluxo. As ações de preenchimento usam inserção direta, sem simular a digitação de cada caractere. Os arquivos são criados em `Documentos\RPA-Challenge`.

O arquivo é uma representação de ações para colar no editor; não é um pacote de solução `.zip`. O fluxo foi executado no Power Automate Desktop em 06/11/2026 e concluiu as dez rodadas com 100% de acerto (70/70 campos). Consulte os [prints e logs reais](evidencias/README.md).

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

## Resultados das execuções reais — 06/11/2026

| Implementação | Acerto | Tempo informado pelo site |
| --- | --- | --- |
| Power Automate Desktop — atraso de 1 ms | 100% (70/70 campos) | 96.738 ms (96,738 s) |
| Python + Selenium + Pandas | 100% (70/70 campos) | 622 ms (0,622 s) |

Os tempos correspondem às dez rodadas cronometradas pelo site, sem incluir leitura do Excel e abertura do navegador. Com o atraso do editor reduzido de 40 para 1 ms, o Power Automate passou de 109.629 para 96.738 ms: redução observada de 12.891 ms (11,76%), mantendo 100% de acerto. São execuções individuais; a diferença inclui variações normais do ambiente. O código das ações foi preservado. Essa configuração não elimina o custo das interações web. [Capturas originais e logs por linha](evidencias/README.md).
