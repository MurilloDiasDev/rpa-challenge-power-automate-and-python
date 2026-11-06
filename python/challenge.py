"""RPA Challenge com Selenium: leitura Excel, logs por registro e captura final."""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://rpachallenge.com/"
HEADERS = ("First Name", "Last Name", "Company Name", "Role in Company", "Address", "Email", "Phone Number")
ATTRIBUTES = ("labelFirstName", "labelLastName", "labelCompanyName", "labelRole", "labelAddress", "labelEmail", "labelPhone")
ROUND_SCRIPT = """
const names = arguments[0], values = arguments[1];
const fields = names.map(name => document.querySelector('input[ng-reflect-name="' + name + '"]'));
if (fields.some(field => !field)) throw new Error('Campo do formulário não encontrado');
const submit = document.querySelector('input[type="submit"]');
if (!submit) throw new Error('Botão Submit não encontrado');
const previous = fields[0].id;
fields.forEach((field, i) => {
  field.value = values[i];
  field.dispatchEvent(new Event('input', {bubbles: true}));
  field.dispatchEvent(new Event('change', {bubbles: true}));
});
submit.click();
return previous;
"""


def read_records(path: Path) -> list[list[str]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = [str(value).strip() if value is not None else "" for value in next(rows)]
        if any(headers.count(name) != 1 for name in HEADERS):
            raise ValueError("A planilha deve conter uma coluna para cada cabeçalho esperado.")
        positions = [headers.index(name) for name in HEADERS]
        records = []
        for row in rows:
            if not any(value is not None for value in row):
                continue
            values = [row[i] if i < len(row) else None for i in positions]
            if any(value is None or str(value).strip() == "" for value in values):
                raise ValueError(f"Registro {len(records) + 1} contém campo vazio.")
            records.append([str(value).strip() for value in values])
            if len(records) == 10:
                break
        if len(records) != 10:
            raise ValueError(f"São necessários 10 registros; encontrados {len(records)}.")
        return records
    finally:
        workbook.close()


def run(path: Path, output: Path, timeout: float) -> int:
    output.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logfile = output / f"etapas_{run_id}.log"
    resultfile = output / f"resultados_{run_id}.csv"
    screenshot = output / f"resultado_final_{run_id}.png"
    logger = logging.getLogger("rpa_challenge")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    for handler in (logging.StreamHandler(sys.stdout), logging.FileHandler(logfile, encoding="utf-8")):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    driver = None
    try:
        logger.info("Lendo planilha: %s", path)
        records = read_records(path)
        logger.info("Dez registros carregados; iniciando Chrome")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, timeout, poll_frequency=0.05)
        driver.get(URL)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-large"))).click()
        logger.info("Desafio iniciado")
        with resultfile.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(("linha_excel", "status", "observacao", "data_hora"))
            for index, values in enumerate(records, start=2):
                logger.info("Preenchendo linha %s", index)
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[ng-reflect-name="labelFirstName"]')))
                    previous_id = driver.execute_script(ROUND_SCRIPT, list(ATTRIBUTES), values)
                    if index < 11:
                        wait.until(lambda d: d.execute_script("const e=document.querySelector('input[ng-reflect-name=\"labelFirstName\"]'); return !!e && (e.id !== arguments[0] || e.value === '');", previous_id))
                    else:
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".congratulations .message2")))
                    writer.writerow((index, "OK", "Envio concluído e avanço de rodada observado", datetime.now().astimezone().isoformat(timespec="seconds")))
                    stream.flush()
                except Exception as error:
                    writer.writerow((index, "NOK", str(error).replace("\n", " ")[:1000], datetime.now().astimezone().isoformat(timespec="seconds")))
                    stream.flush()
                    logger.exception("Falha na linha %s; interrompendo para não deslocar as rodadas", index)
                    raise
        score = driver.find_element(By.CSS_SELECTOR, ".congratulations .message2").text
        if not driver.save_screenshot(str(screenshot)):
            raise RuntimeError("Não foi possível salvar a captura final.")
        logger.info("Resultado exibido pelo site: %s", score)
        logger.info("Captura final: %s", screenshot)
        return 0
    except Exception:
        logger.exception("Execução interrompida")
        return 1
    finally:
        if driver is not None:
            driver.quit()
        logger.info("Arquivos de execução em %s", output.resolve())
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve as dez rodadas do RPA Challenge.")
    parser.add_argument("--excel", type=Path, default=Path.home() / "Downloads" / "challenge.xlsx")
    parser.add_argument("--output", type=Path, default=Path("resultados/python"))
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout deve ser positivo")
    return run(args.excel, args.output, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
