import logging
import tempfile
import os


def createDbAndTables():
    logging.info('executing SQL script...')
    sqlLoginSuccess = False

    with tempfile.NamedTemporaryFile() as t:
        while not sqlLoginSuccess:
            os.system(
                f'sqlcmd -S localhost -U SA -i ../db-scripts/setup/db-init.sql | tee -a {t.name}')

            with open(t.name, 'r') as f:
                lines = f.readlines()

                if len(lines) == 1:
                    continue

                sqlLoginSuccess = True

                for line in lines[1:]:
                    logging.info(line.strip())

    logging.info('DONE')
