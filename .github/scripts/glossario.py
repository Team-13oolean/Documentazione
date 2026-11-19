#!/usr/bin/env python3
r"""Gestisce i termini del glossario e li marca in automatico nei documenti LaTeX.

Pensato per girare nella CI, prima della compilazione, sulla copia di lavoro del
runner: i sorgenti LaTeX vengono modificati sul posto e quelle modifiche NON vanno
committate.

Cosa fa:
  1. legge i termini dal Glossario (src/Documentazione interna/Glossario/chapter/termini.tex),
     cioè dalle righe "\item \textbf{Nome:} definizione", e aggiorna il file
     termini.txt che si trova nella stessa cartella di questo script: aggiunge i termini
     nuovi, toglie quelli eliminati e conserva le forme già scritte a mano;
  2. nel Glossario aggiunge a ogni termine un punto di arrivo (glo:<etichetta>);
  3. negli altri documenti (esclusi i verbali, vedi CARTELLE_ESCLUSE) sostituisce ogni
     occorrenza dei termini con
         \termine{<etichetta>}{<parola come è scritta>}
     che stampa la parola con la G a pedice e il link al Glossario online.

In termini.txt ogni riga è "Nome | forma, forma": dopo la barra si possono aggiungere
a mano le altre forme della parola da riconoscere nel testo (plurali, verbi...).

Le parole vengono cercate solo nel testo normale: sono esclusi preambolo, commenti,
formule, titoli di sezione, didascalie, tabelle, frontespizio, codice (\texttt) e
gli argomenti dei comandi non testuali. Una riga che termina con il commento
"% noglossario" non viene mai modificata.

Uso:
  glossario.py --solo-termini                                (aggiorna solo termini.txt)
  glossario.py --url URL_DEL_GLOSSARIO [--solo-prima] [--prova] DOCUMENTO.tex ...
  glossario.py --url URL --roots roots.list                  (elenco separato da NUL)
"""

import argparse
import bisect
import re
import sys
import unicodedata
from pathlib import Path

CARTELLA_GLOSSARIO = Path("src/Documentazione interna/Glossario")
TERMINI = CARTELLA_GLOSSARIO / "chapter" / "termini.tex"
# Elenco dei termini con le loro forme: sta nella stessa cartella dello script.
FILE_TERMINI = Path(__file__).resolve().parent / "termini.txt"
# Documenti in cui i termini non vengono marcati (verbali interni ed esterni).
CARTELLE_ESCLUSE = [Path("src/Verbali")]

# Comandi i cui argomenti non sono testo da marcare: vengono copiati così come sono.
COMANDI_ESCLUSI = {
    "part", "chapter", "section", "subsection", "subsubsection", "paragraph",
    "caption", "label", "ref", "pageref", "eqref", "cite", "url", "href", "hyperref",
    "hypertarget", "hyperlink", "lnk", "input", "include", "includegraphics",
    "addcontentsline", "texttt", "verb", "termine", "gls", "Gls", "glspl", "Glspl",
    "vspace", "hspace", "setlength", "fontsize", "rule", "newgeometry", "rowcolor",
    "color", "colorlet", "textcolor", "pagestyle", "thispagestyle", "pagenumbering",
    "graphicspath", "usepackage", "newcommand", "renewcommand", "providecommand",
}
# Ambienti saltati per intero.
AMBIENTI_ESCLUSI = {
    "titlepage", "table", "tabular", "tabularx", "longtable", "figure", "equation",
    "equation*", "align", "align*", "verbatim", "lstlisting", "minted",
}
NOGLOSSARIO = re.compile(r"%\s*noglossario\s*$")
RIGA_TERMINE = re.compile(r"^(\s*\\item\s*)\\textbf\{([^}]*?):?\}")
INTESTAZIONE_TXT = """\
# Termini del glossario, uno per riga, generati da glossario.py a partire dal Glossario.
# I nomi vengono aggiornati in automatico: non modificarli qui, ma nel Glossario.
# Dopo "|" si possono aggiungere a mano le altre forme da cercare nel testo,
# separate da virgole (ad esempio: Requisito | requisiti).
"""

MACRO = r"""
% --- Aggiunto in CI da .github/scripts/glossario.py ---
\providecommand{\urlglossario}{URL_GLOSSARIO}
\providecommand{\termine}[2]{\href{\urlglossario\#nameddest=glo:#1}{#2}\textsubscript{G}}
"""


def etichetta(nome):
    """'Analisi dei Requisiti' -> 'analisi-dei-requisiti' (senza accenti)."""
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def leggi_forme():
    """Forme scritte a mano in termini.txt: {nome in minuscolo: [forme]}."""
    forme = {}
    if FILE_TERMINI.is_file():
        for riga in FILE_TERMINI.read_text(encoding="utf-8").splitlines():
            riga = riga.strip()
            if not riga or riga.startswith("#"):
                continue
            nome, _, altre = riga.partition("|")
            forme[nome.strip().lower()] = [f.strip() for f in altre.split(",") if f.strip()]
    return forme


def leggi_termini(scrivi=True):
    """Legge i termini dal Glossario, aggiorna termini.txt e restituisce [(etichetta, nome, [forme])]."""
    nomi = []
    for riga in TERMINI.read_text(encoding="utf-8").splitlines():
        m = RIGA_TERMINE.match(riga)
        if m and m.group(2).strip():
            nomi.append(m.group(2).strip())

    forme = leggi_forme()
    nuovi = [n for n in nomi if n.lower() not in forme]
    rimossi = sorted(set(forme) - {n.lower() for n in nomi})
    termini = [(etichetta(n), n, [n] + forme.get(n.lower(), [])) for n in nomi]
    # "Copertura dei Test (Code Coverage)": si cercano anche le due parti separate.
    for _, nome, tutte in termini:
        m = re.fullmatch(r"(.+?)\s*\((.+)\)", nome)
        if m:
            tutte += [m.group(1), m.group(2)]

    if scrivi:
        righe = []
        for _, nome, tutte in sorted(termini, key=lambda t: t[1].lower()):
            righe.append(nome + (" | " + ", ".join(tutte[1:]) if len(tutte) > 1 else ""))
        FILE_TERMINI.write_text(INTESTAZIONE_TXT + "\n".join(righe) + "\n", encoding="utf-8")
    if FILE_TERMINI.is_file() and (nuovi or rimossi):
        print(f"termini.txt: {len(nuovi)} termini aggiunti, {len(rimossi)} rimossi")
        for n in nuovi:
            print(f"  + {n}")
        for n in rimossi:
            print(f"  - {n}")
    return termini


def costruisci_ricerca(termini):
    """Una sola espressione regolare con tutte le forme, dalla più lunga alla più corta.

    Le sigle e le parole con maiuscole interne (API, GitHub) sono cercate rispettando le
    maiuscole, così "api" (l'insetto) non diventa "API"; le altre ignorano le maiuscole.
    """
    voci = sorted(
        ((forma, etic) for etic, _, forme in termini for forma in forme),
        key=lambda v: len(v[0]), reverse=True,
    )
    alternative, per_gruppo = [], {}
    for i, (forma, etic) in enumerate(voci):
        corpo = r"\s+".join(re.escape(p) for p in forma.split())
        if not any(c.isupper() for c in forma[1:]):
            corpo = f"(?i:{corpo})"
        alternative.append(f"(?P<t{i}>{corpo})")
        per_gruppo[f"t{i}"] = etic
    regex = re.compile(r"(?<![\w\\])(?:" + "|".join(alternative) + r")(?!\w)")
    return regex, per_gruppo


def fine_gruppo(testo, i, apre, chiude):
    """Indice subito dopo il gruppo bilanciato che inizia in testo[i] == apre."""
    livello = 0
    while i < len(testo):
        c = testo[i]
        if c == "\\":
            i += 2
            continue
        if c == apre:
            livello += 1
        elif c == chiude:
            livello -= 1
            if livello == 0:
                return i + 1
        i += 1
    return len(testo)


def salta_argomenti(testo, i):
    """Salta spazi e gruppi [..] e {..} consecutivi dopo un comando."""
    while True:
        j = i
        while j < len(testo) and testo[j] in " \t":
            j += 1
        if j < len(testo) and testo[j] in "[{":
            i = fine_gruppo(testo, j, testo[j], "]" if testo[j] == "[" else "}")
        else:
            return i


def segmenti_di_testo(testo, inizio):
    """Restituisce gli intervalli (a, b) di testo normale da inizio alla fine.

    Rileva anche gli \\input trovati nel testo, restituiti come (posizione, percorso).
    """
    segmenti, inclusi = [], []
    i, a = inizio, inizio

    def chiudi(fine):
        if fine > a:
            segmenti.append((a, fine))

    while i < len(testo):
        c = testo[i]
        if c == "%":
            chiudi(i)
            i = testo.find("\n", i)
            i = len(testo) if i < 0 else i
            a = i
        elif c == "$":
            chiudi(i)
            doppio = testo.startswith("$$", i)
            fine = testo.find("$$" if doppio else "$", i + (2 if doppio else 1))
            i = len(testo) if fine < 0 else fine + (2 if doppio else 1)
            a = i
        elif c == "\\":
            chiudi(i)
            m = re.match(r"\\([a-zA-Z]+\*?|.)", testo[i:])
            nome = m.group(1)
            j = i + len(m.group(0))
            if nome in ("(", "["):
                fine = testo.find("\\)" if nome == "(" else "\\]", j)
                j = len(testo) if fine < 0 else fine + 2
            elif nome in ("begin", "end"):
                m2 = re.match(r"\s*\{([^}]*)\}", testo[j:])
                ambiente = m2.group(1) if m2 else ""
                j += len(m2.group(0)) if m2 else 0
                if nome == "begin" and ambiente in AMBIENTI_ESCLUSI:
                    fine = testo.find("\\end{%s}" % ambiente, j)
                    j = len(testo) if fine < 0 else fine
                elif nome == "begin":
                    j = salta_argomenti(testo, j)
            elif nome in ("input", "include"):
                fine = salta_argomenti(testo, j)
                m2 = re.match(r"\s*\{([^}]*)\}", testo[j:])
                if m2:
                    inclusi.append((i, m2.group(1).strip()))
                j = fine
            elif nome.rstrip("*") in COMANDI_ESCLUSI:
                j = salta_argomenti(testo, j)
            i = a = j
        else:
            i += 1
    chiudi(i)
    return segmenti, inclusi


class Documento:
    """Un documento principale con i file che include, marcati in ordine di lettura."""

    def __init__(self, principale, regex, per_gruppo, tutte):
        self.principale = principale
        self.cartella = principale.parent
        self.regex, self.per_gruppo, self.tutte = regex, per_gruppo, tutte
        self.usati = set()
        self.modifiche = {}  # file -> nuovo contenuto
        self.marcati = []    # (file, riga, parola)

    def risolvi(self, percorso):
        p = (self.cartella / percorso)
        p = p if p.suffix == ".tex" else p.with_name(p.name + ".tex")
        # Si seguono solo i file nella cartella del documento: quelli condivisi
        # (src/shared) sono inclusi anche da altri documenti e non vanno toccati.
        try:
            p.resolve().relative_to(self.cartella.resolve())
        except ValueError:
            return None
        return p if p.is_file() else None

    def elabora(self, file, principale=False):
        testo = file.read_text(encoding="utf-8")
        inizio = 0
        if principale:
            m = re.search(r"^[^%\n]*\\begin\{document\}", testo, re.M)
            if not m:
                return
            inizio = m.end()
        righe = [0] + [m.end() for m in re.finditer("\n", testo)]
        segmenti, inclusi = segmenti_di_testo(testo, inizio)

        # Ordine di lettura: testo e \input in base alla posizione nel file.
        eventi = sorted([(a, "testo", (a, b)) for a, b in segmenti] +
                        [(pos, "input", perc) for pos, perc in inclusi])
        sostituzioni = []
        for _, tipo, dato in eventi:
            if tipo == "input":
                incluso = self.risolvi(dato)
                if incluso:
                    self.elabora(incluso)
                continue
            a, b = dato
            for m in self.regex.finditer(testo, a, b):
                etic = self.per_gruppo[m.lastgroup]
                n_riga = bisect.bisect_right(righe, m.start())
                fine_riga = testo.find("\n", m.start())
                riga = testo[righe[n_riga - 1]: len(testo) if fine_riga < 0 else fine_riga]
                if NOGLOSSARIO.search(riga) or (etic in self.usati and not self.tutte):
                    continue
                self.usati.add(etic)
                sostituzioni.append((m.start(), m.end(), "\\termine{%s}{%s}" % (etic, m.group(0))))
                self.marcati.append((file, n_riga, m.group(0)))

        if principale:
            pos = re.search(r"^[^%\n]*\\begin\{document\}", testo, re.M).start()
            # In LaTeX "%" e "#" sono caratteri speciali: nell'indirizzo vanno preceduti da "\".
            url = re.sub(r"(?<!\\)([%#])", r"\\\1", self.url)
            sostituzioni.append((pos, pos, MACRO.replace("URL_GLOSSARIO", url) + "\n"))
        if sostituzioni:
            for a, b, nuovo in sorted(sostituzioni, reverse=True):
                testo = testo[:a] + nuovo + testo[b:]
            self.modifiche[file] = testo


def aggiungi_ancore(termini):
    """Nel Glossario: \\item \\textbf{Nome:} -> \\item \\hypertarget{glo:etichetta}{}\\textbf{Nome:}"""
    righe = TERMINI.read_text(encoding="utf-8").splitlines(keepends=True)
    for k, riga in enumerate(righe):
        m = RIGA_TERMINE.match(riga.rstrip("\r\n"))
        if m:
            etic = etichetta(m.group(2).strip())
            righe[k] = riga.replace(m.group(1), m.group(1) + "\\hypertarget{glo:%s}{}" % etic, 1)
    return "".join(righe)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("documenti", nargs="*", type=Path, help="file .tex principali")
    parser.add_argument("--roots", type=Path, help="file con l'elenco dei documenti separati da NUL")
    parser.add_argument("--url", help="indirizzo pubblico del PDF del Glossario")
    parser.add_argument("--solo-termini", action="store_true",
                        help="aggiorna solo termini.txt, senza marcare i documenti")
    parser.add_argument("--solo-prima", action="store_true",
                        help="marca solo la prima occorrenza di ogni termine in ogni documento")
    parser.add_argument("--prova", action="store_true", help="mostra cosa verrebbe marcato senza modificare i file")
    args = parser.parse_args()
    if not args.solo_termini and not args.url:
        parser.error("serve --url (oppure --solo-termini)")

    documenti = list(args.documenti)
    if args.roots:
        documenti += [Path(p) for p in args.roots.read_text(encoding="utf-8").split("\0") if p]

    termini = leggi_termini(scrivi=not args.prova)
    print(f"Termini nel glossario: {len(termini)}")
    if args.solo_termini:
        return
    regex, per_gruppo = costruisci_ricerca(termini)

    for principale in documenti:
        if any(c.resolve() in principale.resolve().parents for c in CARTELLE_ESCLUSE):
            print(f"\n{principale}: escluso")
            continue
        if CARTELLA_GLOSSARIO.resolve() in principale.resolve().parents:
            print(f"\n{principale}: aggiunti i punti di arrivo per {len(termini)} termini")
            if not args.prova:
                TERMINI.write_text(aggiungi_ancore(termini), encoding="utf-8")
            continue
        if "hyperref" not in principale.read_text(encoding="utf-8"):
            print(f"\n{principale}: saltato, manca il pacchetto hyperref", file=sys.stderr)
            continue
        doc = Documento(principale, regex, per_gruppo, not args.solo_prima)
        doc.url = args.url
        doc.elabora(principale, principale=True)
        print(f"\n{principale}: {len(doc.marcati)} termini marcati")
        for file, riga, parola in doc.marcati:
            print(f"  {file.relative_to(doc.cartella)}:{riga}  {parola}")
        if not args.prova:
            for file, testo in doc.modifiche.items():
                file.write_text(testo, encoding="utf-8")


if __name__ == "__main__":
    main()
