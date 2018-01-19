import os
from pathlib import Path
import sys
import re
import imaplib
import email
from pathlib import Path
import sqlite3
from zipfile import ZipFile
import pandas as pd
import warnings
warnings.simplefilter('ignore')

cwd = os.path.dirname(os.path.realpath(__file__))
outdir = os.path.join(cwd, 'data')
zip_path = os.path.join(outdir, 'zips')
db_path = os.path.join(outdir, 'exchange_data.db')

if not os.path.exists(outdir):
    os.mkdir(outdir)

if os.path.exists(zip_path):
    os.remove(zip_path)

if not os.path.exists(zip_path):
    os.mkdir(zip_path)

if os.path.exists(db_path):
    os.remove(db_path)

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('nick.morley111@googlemail.com','tvwhzhunlexpeagj')
mail.list()
mail.select("inbox")
result, data = mail.search(None, 'Subject', '"Exchange data 2"')
uids = data[0].split()
print('downloading...')
for i, uid in enumerate(uids):
    print(i + 1, '/', len(uids), end='\r')
    result, data = mail.fetch(uid, '(RFC822)')
    msg = data[0][1].decode()
    msg = email.message_from_string(msg)
    attachment = msg.get_payload()[0]
    filename = attachment.get_filename()
    saved = False
    outpath = os.path.join(zip_path, filename)
    while not saved:
        if not os.path.exists(outpath):
            with open(outpath, 'wb') as fp:
                fp.write(attachment.get_payload(decode=True))
                saved = True
        else:  # Path exists
            prefix = re.findall(r'([a-z]+_)', outpath.split('.')[0])[0]
            suffix = str(int(re.findall(r'(\d+)', outpath)[0]) + 1)
            outpath = os.path.join(zip_path, prefix + suffix + '.zip')


zips = [os.path.join(zip_path, fp) for fp in os.listdir(zip_path) if '.zip' in fp]
print('inserting into', db_path, '...')
with sqlite3.connect(db_path) as con:
    cur = con.cursor()

    for fp in zips:
    	with ZipFile(fp) as zf:
            for member in zf.infolist():
                with zf.open(member) as file:
                    df = pd.read_csv(file)
                    df.to_sql('exchange_data', con, if_exists='append', index=False)

print('done')
