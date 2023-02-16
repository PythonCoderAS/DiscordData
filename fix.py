from os import walk
from shutil import copy2

from tqdm import tqdm

from msgs import chmkdir, _setup

lgr = _setup("Fixer")

if __name__ == '__main__':
    for n in tqdm(list(walk("App"))):
        try:
            a, b, c = n
            for i in c:
                if '.csv' in i:
                    fulldir = a + '\\' + i
                    g = []
                    with open(fulldir, 'r', encoding='utf-8') as f:
                        # noinspection PyRedeclaration
                        for j in f.readlines():
                            jj = j
                            try:
                                j = j[:-1]
                                if j[0] in '0123456789I' and ',' in j:
                                    g.append(j)
                            except Exception:
                                # noinspection PyUnboundLocalVariable
                                lgr.exception("Problem with line %s", jj.replace('\n', 'NL'))
                    with open(fulldir, 'r', encoding='utf-8') as f:
                        l = f.readlines()
                    if len(g) != len(l):
                        aa = a.replace("App", "Backup\\App")
                        chmkdir(aa, lgr)
                        copy2(fulldir, aa + '\\' + i)
                        lgr.info("File copied from %s to %s", fulldir, aa + '\\' + i)
                        with open(fulldir, 'w', encoding='utf-8') as f:
                            for k in g:
                                f.write(k + '\n')
                            lgr.info("File %s overwritten", fulldir)
        except Exception:
            lgr.exception("Error with %s", n)
