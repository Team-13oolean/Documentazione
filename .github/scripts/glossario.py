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
  3. negli altri documenti (esclusi i verbali, vedi EXCLUDED_DIRS) sostituisce la
     prima occorrenza di ogni termine (in ordine di lettura, contando anche i file
     inclusi con \input) con
         \termine{<etichetta>}{<parola come è scritta>}
     che stampa la parola con la G a pedice e il link al Glossario online.

In termini.txt ogni riga è "Nome | forma, forma": dopo la barra si possono aggiungere
a mano le altre forme della parola da riconoscere nel testo (plurali, verbi...).

Le parole vengono cercate solo nel testo normale: sono esclusi preambolo, commenti,
formule, titoli di sezione, didascalie, tabelle, frontespizio, codice (\texttt) e
gli argomenti di tutti i comandi tranne quelli testuali (vedi TEXT_COMMANDS). Una riga
che termina con il commento "% noglossario" non viene mai modificata, e un termine già
marcato a mano con \termine non viene marcato di nuovo.

Se il documento non carica hyperref, \termine stampa solo la parola, senza link né G.

Uso:
  glossario.py --solo-termini                                (aggiorna solo termini.txt)
  glossario.py --url URL_DEL_GLOSSARIO [--prova] DOCUMENTO.tex ...
  glossario.py --url URL --roots roots.list                  (elenco separato da NUL)
"""

import argparse
import bisect
import re
import sys
import unicodedata
from pathlib import Path

GLOSSARY_DIR = Path("src/Documentazione interna/Glossario")
TERMS_TEX = GLOSSARY_DIR / "chapter" / "termini.tex"
# Elenco dei termini con le loro forme: sta nella stessa cartella dello script.
TERMS_FILE = Path(__file__).resolve().parent / "termini.txt"
# Documenti in cui i termini non vengono marcati (verbali interni ed esterni).
EXCLUDED_DIRS = [Path("src/Verbali")]

# Comandi i cui argomenti sono testo normale, in cui i termini vanno marcati.
# Gli argomenti di tutti gli altri comandi (\section, \label, \autoref, \lstinputlisting,
# comandi personalizzati...) vengono copiati così come sono: così un termine che compare
# in un'etichetta o in un percorso non rompe la compilazione.
TEXT_COMMANDS = {
    "textbf", "textit", "textsl", "textsc", "textup", "textmd", "textrm", "textsf",
    "textnormal", "emph", "underline", "uline", "footnote", "footnotetext", "item",
    "mbox", "fbox", "enquote", "marginpar",
}
# Comandi con delimitatori qualsiasi, come \verb|...|: il contenuto non è mai testo.
VERB_COMMANDS = {"verb", "verb*", "lstinline", "mintinline"}
# Ambienti saltati per intero.
EXCLUDED_ENVIRONMENTS = {
    "titlepage", "table", "table*", "tabular", "tabular*", "tabularx", "longtable",
    "tblr", "longtblr", "figure", "figure*", "equation", "equation*", "align", "align*",
    "alignat", "alignat*", "gather", "gather*", "multline", "multline*", "flalign",
    "flalign*", "eqnarray", "eqnarray*", "displaymath", "math", "tikzpicture",
    "verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment",
}
NO_GLOSSARY = re.compile(r"%\s*noglossario\s*$")
TERM_LINE = re.compile(r"^(\s*\\item\s*)(?:\\hypertarget\{glo:[^}]*\}\{\}\s*)?\\textbf\{([^}]*?):?\}")
COMMAND = re.compile(r"\\([a-zA-Z]+\*?|.)", re.S)
ENV_NAME = re.compile(r"\s*\{([^}]*)\}")
BEGIN_DOCUMENT = re.compile(r"^[^%\n]*\\begin\{document\}", re.M)
TXT_HEADER = """\
# Termini del glossario, uno per riga, generati da glossario.py a partire dal Glossario.
# I nomi vengono aggiornati in automatico: non modificarli qui, ma nel Glossario.
# Dopo "|" si possono aggiungere a mano le altre forme da cercare nel testo,
# separate da virgole (ad esempio: Requisito | requisiti).
"""

MACRO = r"""
% --- Aggiunto in CI da .github/scripts/glossario.py ---
\providecommand{\urlglossario}{URL_GLOSSARIO}
\ifdefined\href
  \providecommand{\termine}[2]{\href{\urlglossario\#nameddest=glo:#1}{#2}\textsubscript{G}}
\else
  \providecommand{\termine}[2]{#2}
\fi
"""


def make_label(name):
    """'Analisi dei Requisiti' -> 'analisi-dei-requisiti' (senza accenti)."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def read_forms():
    """Forme scritte a mano in termini.txt: {nome in minuscolo: [forme]}."""
    forms = {}
    if TERMS_FILE.is_file():
        for line in TERMS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, _, others = line.partition("|")
            forms[name.strip().lower()] = [f.strip() for f in others.split(",") if f.strip()]
    return forms


def read_terms(write=True):
    """Legge i termini dal Glossario, aggiorna termini.txt e restituisce [(etichetta, nome, [forme])]."""
    names = []
    for line in TERMS_TEX.read_text(encoding="utf-8").splitlines():
        m = TERM_LINE.match(line)
        if m and m.group(2).strip():
            names.append(m.group(2).strip())

    forms = read_forms()
    added = [n for n in names if n.lower() not in forms]
    removed = sorted(set(forms) - {n.lower() for n in names})

    terms, rows = [], []
    for name in names:
        # Forme ricavate in automatico: per "Copertura dei Test (Code Coverage)" si cercano
        # anche le due parti separate. Non vengono scritte in termini.txt.
        automatic = []
        m = re.fullmatch(r"(.+?)\s*\((.+)\)", name)
        if m:
            automatic = [m.group(1), m.group(2)]
        # Forme scritte a mano, senza doppioni e senza quelle già ricavate in automatico.
        manual = []
        for form in forms.get(name.lower(), []):
            if form.lower() not in {x.lower() for x in [name] + automatic + manual}:
                manual.append(form)
        terms.append((make_label(name), name, [name] + manual + automatic))
        rows.append((name, manual))

    if write:
        text = TXT_HEADER + "".join(
            name + (" | " + ", ".join(manual) if manual else "") + "\n"
            for name, manual in sorted(rows, key=lambda r: r[0].lower()))
        # Il file viene riscritto solo se cambia davvero: così il bot non crea commit inutili.
        if not TERMS_FILE.is_file() or TERMS_FILE.read_text(encoding="utf-8") != text:
            TERMS_FILE.write_text(text, encoding="utf-8")
    seen = {}
    for label, name, _ in terms:
        if not label:
            print(f"ATTENZIONE: il termine \"{name}\" non produce un'etichetta valida", file=sys.stderr)
        elif label in seen:
            print(f"ATTENZIONE: \"{seen[label]}\" e \"{name}\" hanno la stessa etichetta "
                  f"glo:{label}: i link porteranno allo stesso punto", file=sys.stderr)
        seen.setdefault(label, name)
    if TERMS_FILE.is_file() and (added or removed):
        print(f"termini.txt: {len(added)} termini aggiunti, {len(removed)} rimossi")
        for name in added:
            print(f"  + {name}")
        for name in removed:
            print(f"  - {name}")
    return terms


def build_search(terms):
    """Una sola espressione regolare con tutte le forme, dalla più lunga alla più corta.

    Le sigle e le parole con maiuscole interne (API, GitHub) sono cercate rispettando le
    maiuscole, così "api" (l'insetto) non diventa "API"; le altre ignorano le maiuscole.
    Il controllo è fatto parola per parola: "Analisi dei Requisiti" trova anche
    "analisi dei requisiti", mentre "Servizio API" trova "servizio API" ma non "servizio api".
    Le parole possono essere separate da spazi, a capo o "~".
    """
    entries = sorted(
        ((form, label) for label, _, forms in terms for form in forms),
        key=lambda e: len(e[0]), reverse=True,
    )
    alternatives, label_by_group = [], {}
    for i, (form, label) in enumerate(entries):
        parts = []
        for word in form.split():
            word_re = re.escape(word)
            if not any(c.isupper() for c in word[1:]):
                word_re = f"(?i:{word_re})"
            parts.append(word_re)
        body = r"[\s~]+".join(parts)
        alternatives.append(f"(?P<t{i}>{body})")
        label_by_group[f"t{i}"] = label
    regex = re.compile(r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)")
    return regex, label_by_group


def group_end(text, i, opener, closer):
    """Indice subito dopo il gruppo bilanciato che inizia in text[i] == opener."""
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def skip_arguments(text, i):
    """Salta spazi e gruppi [..] e {..} consecutivi dopo un comando."""
    while True:
        j = i
        while j < len(text) and text[j] in " \t":
            j += 1
        if j < len(text) and text[j] in "[{":
            i = group_end(text, j, text[j], "]" if text[j] == "[" else "}")
        else:
            return i


def text_segments(text, start):
    """Restituisce gli intervalli (a, b) di testo normale da start alla fine.

    Rileva anche gli \\input trovati nel testo, restituiti come (posizione, "input", percorso),
    e i \\termine già presenti, come (posizione, "marked", etichetta).
    """
    segments, includes = [], []
    i, a = start, start

    def close(end):
        if end > a:
            segments.append((a, end))

    while i < len(text):
        c = text[i]
        if c == "%":
            close(i)
            i = text.find("\n", i)
            i = len(text) if i < 0 else i
            a = i
        elif c == "$":
            close(i)
            double = text.startswith("$$", i)
            end = text.find("$$" if double else "$", i + (2 if double else 1))
            i = len(text) if end < 0 else end + (2 if double else 1)
            a = i
        elif c == "\\":
            close(i)
            m = COMMAND.match(text, i)
            if not m:  # "\" come ultimo carattere del file
                break
            name = m.group(1)
            j = m.end()
            if name in VERB_COMMANDS and j < len(text) and text[j] != "{":
                # \verb|...|: si salta fino al delimitatore di chiusura.
                end = text.find(text[j], j + 1)
                j = len(text) if end < 0 else end + 1
            elif name in ("(", "["):
                end = text.find("\\)" if name == "(" else "\\]", j)
                j = len(text) if end < 0 else end + 2
            elif name in ("begin", "end"):
                m2 = ENV_NAME.match(text, j)
                environment = m2.group(1) if m2 else ""
                j = m2.end() if m2 else j
                if name == "begin" and environment in EXCLUDED_ENVIRONMENTS:
                    end = text.find("\\end{%s}" % environment, j)
                    j = len(text) if end < 0 else end
                elif name == "begin":
                    j = skip_arguments(text, j)
            elif name in ("input", "include"):
                end = skip_arguments(text, j)
                m2 = ENV_NAME.match(text, j)
                if m2:
                    includes.append((i, "input", m2.group(1).strip()))
                j = end
            elif name == "termine":
                m2 = ENV_NAME.match(text, j)
                if m2:
                    includes.append((i, "marked", m2.group(1).strip()))
                j = skip_arguments(text, j)
            elif name == "\\" or (name[0].isalpha() and name.rstrip("*") not in TEXT_COMMANDS):
                j = skip_arguments(text, j)
            i = a = j
        else:
            i += 1
    close(i)
    return segments, includes


class Document:
    """Un documento principale con i file che include, marcati in ordine di lettura."""

    def __init__(self, main_file, regex, label_by_group, url):
        self.main_file = main_file
        self.folder = main_file.parent
        self.regex, self.label_by_group, self.url = regex, label_by_group, url
        self.used = set()    # termini già marcati: ognuno solo alla prima occorrenza
        self.open_files = [] # file in elaborazione, per evitare \input circolari
        self.changes = {}    # file -> nuovo contenuto
        self.marked = []     # (file, riga, parola)

    def resolve(self, path):
        p = self.folder / path
        p = p if p.suffix == ".tex" else p.with_name(p.name + ".tex")
        # Si seguono solo i file nella cartella del documento: quelli condivisi
        # (src/shared) sono inclusi anche da altri documenti e non vanno toccati.
        try:
            p.resolve().relative_to(self.folder.resolve())
        except ValueError:
            return None
        return p if p.is_file() else None

    def process(self, file, is_main=False):
        text = file.read_text(encoding="utf-8")
        start = 0
        if is_main:
            m = BEGIN_DOCUMENT.search(text)
            if not m:
                return
            start = m.end()
        line_starts = [0] + [m.end() for m in re.finditer("\n", text)]
        segments, includes = text_segments(text, start)

        # Ordine di lettura: testo e \input in base alla posizione nel file.
        events = sorted([(a, "text", (a, b)) for a, b in segments] +
                        includes)
        replacements = []
        for _, kind, data in events:
            if kind == "marked":
                # Termine già marcato (a mano o da un'esecuzione precedente).
                self.used.add(data)
                continue
            if kind == "input":
                included = self.resolve(data)
                if included and included.resolve() not in self.open_files:
                    self.open_files.append(file.resolve())
                    self.process(included)
                    self.open_files.pop()
                continue
            a, b = data
            for m in self.regex.finditer(text, a, b):
                label = self.label_by_group[m.lastgroup]
                line_no = bisect.bisect_right(line_starts, m.start())
                line_end = text.find("\n", m.start())
                line = text[line_starts[line_no - 1]: len(text) if line_end < 0 else line_end]
                if NO_GLOSSARY.search(line) or label in self.used:
                    continue
                self.used.add(label)
                replacements.append((m.start(), m.end(), "\\termine{%s}{%s}" % (label, m.group(0))))
                self.marked.append((file, line_no, m.group(0)))

        if is_main:
            pos = BEGIN_DOCUMENT.search(text).start()
            # In LaTeX "%" e "#" sono caratteri speciali: nell'indirizzo vanno preceduti da "\".
            url = re.sub(r"(?<!\\)([%#])", r"\\\1", self.url)
            replacements.append((pos, pos, MACRO.replace("URL_GLOSSARIO", url) + "\n"))
        if replacements:
            for a, b, new in sorted(replacements, reverse=True):
                text = text[:a] + new + text[b:]
            self.changes[file] = text


def add_anchors(terms):
    """Nel Glossario: \\item \\textbf{Nome:} -> \\item \\hypertarget{glo:etichetta}{}\\textbf{Nome:}"""
    lines = TERMS_TEX.read_text(encoding="utf-8").splitlines(keepends=True)
    for k, line in enumerate(lines):
        m = TERM_LINE.match(line.rstrip("\r\n"))
        if m and "\\hypertarget{glo:" not in line:
            label = make_label(m.group(2).strip())
            lines[k] = line.replace(m.group(1), m.group(1) + "\\hypertarget{glo:%s}{}" % label, 1)
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("documents", nargs="*", type=Path, metavar="documenti",
                        help="file .tex principali")
    parser.add_argument("--roots", type=Path, help="file con l'elenco dei documenti separati da NUL")
    parser.add_argument("--url", help="indirizzo pubblico del PDF del Glossario")
    parser.add_argument("--solo-termini", dest="terms_only", action="store_true",
                        help="aggiorna solo termini.txt, senza marcare i documenti")
    parser.add_argument("--prova", dest="dry_run", action="store_true",
                        help="mostra cosa verrebbe marcato senza modificare i file")
    args = parser.parse_args()
    if not args.terms_only and not args.url:
        parser.error("serve --url (oppure --solo-termini)")

    documents = list(args.documents)
    if args.roots:
        documents += [Path(p) for p in args.roots.read_text(encoding="utf-8").split("\0") if p]

    terms = read_terms(write=not args.dry_run)
    print(f"Termini nel glossario: {len(terms)}")
    if args.terms_only:
        return
    regex, label_by_group = build_search(terms)

    for main_file in documents:
        if any(d.resolve() in main_file.resolve().parents for d in EXCLUDED_DIRS):
            print(f"\n{main_file}: escluso")
            continue
        if GLOSSARY_DIR.resolve() in main_file.resolve().parents:
            print(f"\n{main_file}: aggiunti i punti di arrivo per {len(terms)} termini")
            if not args.dry_run:
                TERMS_TEX.write_text(add_anchors(terms), encoding="utf-8")
            continue
        doc = Document(main_file, regex, label_by_group, args.url)
        doc.process(main_file, is_main=True)
        print(f"\n{main_file}: {len(doc.marked)} termini marcati")
        for file, line_no, word in doc.marked:
            print(f"  {file.relative_to(doc.folder)}:{line_no}  {word}")
        if not args.dry_run:
            for file, text in doc.changes.items():
                file.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
