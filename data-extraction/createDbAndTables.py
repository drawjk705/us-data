import logging
import tempfile
import os


def createDbAndTables():
    """
    Runs the generated SQL scripts.
    (Unfortunately, at this point, they all need to be in the same file,
    because logging into an MS-SQL Server on Linux is complicated).
    """

    logging.info('executing SQL script...')
    sqlLoginSuccess = False

    # we create a tempfile to store the
    # output from `sqlcmd` so we can then add
    # it to the logfile
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
