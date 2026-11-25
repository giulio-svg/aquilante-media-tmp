#!/usr/bin/env python3
"""KIT GIULIO CAVALLI - tutti i controlli in un file. Uso: python3 kit.py <comando> argomenti
qc bozza.md claims.tsv --formato buongiorno|colonna|articolo|newsletter|urto|gaza|libero [--target N] [--libri] [--core] [--bozza]
   esegue selftest, cancello, fedelta, voce, conta, scan e stampa la tabella compatta (exit 0 solo se tutto pulito)
selftest: verifica che la copia del kit sia integra (riga "0 kit" della tabella qc)
cancello|fedelta bozza.md claims.tsv · voce bozza.md [--libri|--core|--bozza|--dove] · conta bozza.md --formato X [--target N]
scan bozza.md [--radio] · seo candidati.txt (righe S:/T:/H:/N:/A:/B:, A e B = prompt immagine, obbligatori) · agenzie file.txt... · fixbdr file.docx
claims.tsv: id | affermazione | fonte | data | tipo | livello | nota [| testo_fonte | pezzo] (schema in stile-nucleo.md §1-bis)
   testo_fonte: estratto breve della norma o della frase della fonte, senza tabulazioni ne' a capo
   pezzo: B, U, BU (o altre lettere); con --pezzo X cancello e fedelta guardano solo le righe di quel pezzo
Profili voce: --profilo opinione|radio|inchiesta|giornalismo (qc lo sceglie dal formato), --libri, --core
ARCHIVIO: https://raw.githubusercontent.com/giulio-svg/aquilante-media-tmp/main/kit-editoriali/kit.py
   Si esegue la copia del Progetto. Ogni modifica si fa su GitHub e si ricarica identica nel Progetto, aggiornando VERSIONE.
NOTA: i caratteri invisibili e i trattini si scrivono SOLO come codici \\uXXXX, mai letterali.
"""
import sys
VERSIONE = "2026-11-24"
BANDE = {"giornalismo":{"lung_frase_mean":[21.38,39.82,29.43],"lung_frase_cv":[0.49,0.93,0.66],"para_mean":[2.67,6.79,4.4],"para_cv":[0.17,0.66,0.35],"virgole_frase":[0.66,2.28,1.14],"subord_frase":[0.6,1.99,1.09],"ttr":[0.74,0.8,0.77],"f_corte":[3.46,23.08,11.11],"f_medie":[5.0,38.1,23.33],"f_lunghe":[13.38,56.72,29.41]},"libri":{"lung_frase_mean":[11.28,25.52,18.24],"lung_frase_cv":[0.61,1.29,0.79],"para_mean":[55.4,125.4,82.0],"para_cv":[0.4,0.4,0.4],"virgole_frase":[0.43,1.87,1.25],"subord_frase":[0.39,1.2,0.75],"ttr":[0.75,0.81,0.78],"f_corte":[6.27,43.26,22.83],"f_medie":[10.98,34.51,21.43],"f_lunghe":[2.22,24.29,8.22]}}
import copy as _copy
def _profilo(base, mean, cv, lunghe_max):
    b = _copy.deepcopy(BANDE[base]); b["lung_frase_mean"][:2] = mean; b["lung_frase_cv"][:2] = cv
    b["f_lunghe"][1] = lunghe_max; return b
# stile-nucleo §17.9: opinione 25-32 / 0,60-0,80 / lunghe fino al 45%; inchiesta 24-32 / 0,60-0,80 / fino al 35%;
# radio = opinione con frasi piu' corte (minimo del corpus, tetto 32)
BANDE["opinione"] = _profilo("giornalismo", [25.0, 32.0], [0.60, 0.80], 45.0)
BANDE["inchiesta"] = _profilo("giornalismo", [24.0, 32.0], [0.60, 0.80], 35.0)
BANDE["radio"] = _profilo("giornalismo", [21.38, 32.0], [0.60, 0.80], 45.0)
BANDE["opinione"]["virgole_frase"][:2] = [1.0, 1.5]   # §17.9: virgole per frase 1,0-1,5 nel registro opinione
BANDE["radio"]["virgole_frase"][:2] = [1.0, 1.5]
PROFILO_FORMATO = {"buongiorno": "opinione", "colonna": "opinione", "urto": "radio",
                   "articolo": "inchiesta", "newsletter": "inchiesta", "gaza": "inchiesta"}

def _argomenti():
    # argomenti posizionali, esclusi i flag e i valori dei flag che ne hanno uno
    out, salta = [], False
    for a in sys.argv[1:]:
        if salta: salta = False; continue
        if a in ("--pezzo", "--profilo", "--formato", "--target"): salta = True; continue
        if a.startswith("--"): continue
        out.append(a)
    return out

def _del_pezzo(riga):
    # True se la riga vale per il pezzo richiesto con --pezzo (righe senza colonna pezzo valgono per tutti)
    if "--pezzo" not in sys.argv: return True
    voluto = sys.argv[sys.argv.index("--pezzo")+1].upper()
    col = riga[8].strip().upper() if len(riga) > 8 else ""
    return not col or voluto in col

def cancello():
    import sys, csv

    def main(bozza_path, claims_path):
        problemi = []
        righe = []
        with open(claims_path, encoding="utf-8") as f:
            for n, r in enumerate(csv.reader(f, delimiter="\t"), 1):
                if not r or r[0].strip().startswith("#"):
                    continue
                if len(r) < 5:
                    problemi.append(f"riga {n}: meno di 5 colonne")
                    continue
                if not _del_pezzo(r):
                    continue
                cid, aff, fonte, data, tipo = (c.strip() for c in r[:5])
                righe.append((cid, aff, fonte, data, tipo))
        if not righe:
            problemi.append("claims.tsv vuoto")
        for cid, aff, fonte, data, tipo in righe:
            if not fonte:
                problemi.append(f"[{cid}] fonte mancante: \"{aff[:60]}\"")
            if not data:
                problemi.append(f"[{cid}] data mancante: \"{aff[:60]}\"")
            if tipo == "nome_persona" and "PRIMARIA" not in fonte.upper():
                problemi.append(
                    f"[{cid}] NOME PROPRIO senza primaria: \"{aff[:60]}\" "
                    f"-> generico o togliere")
        if problemi:
            print("CANCELLO CHIUSO. Consegna bloccata. Problemi:")
            for p in problemi:
                print("  - " + p)
            print(f"\nTotale: {len(problemi)}. Risolvere PRIMA di mostrare.")
            sys.exit(1)
        print(f"CANCELLO APERTO. {len(righe)} affermazioni, tutte agganciate.")
        print("Nomi propri: tutti su primaria. Consegna consentita.")
        sys.exit(0)

    a = _argomenti()
    if len(a) != 2:
        print("uso: python3 kit.py cancello bozza.md claims.tsv [--pezzo X]")
        sys.exit(2)
    main(a[0], a[1])


def fedelta():
    import sys, csv, re

    QUANT = r"\b(pochi|poche|molti|molte|alcuni|alcune|numerosi|parecchi|la maggior parte|gran parte|quasi tutti|quasi tutte|la stragrande maggioranza|diversi|svariati)\b"
    ASSERT = r"\b(annuncia|annunciato|conferma|confermato|decide|deciso|stabilisce|fissa|promette)\b"
    SCOPE = r"\b(dichiara|dichiarano|certifica|certificano|documenta|dimostra|attesta|prova che|sancisce)\b"

    def frasi(t):
        return [f.strip() for f in re.split(r'(?<=[\.\?\!])\s+', t) if f.strip()]

    def main(bozza, claimsf):
        testo = open(bozza, encoding="utf-8").read().replace("**", "")
        righe = []
        with open(claimsf, encoding="utf-8") as f:
            for r in csv.reader(f, delimiter="\t"):
                if not r or r[0].strip().startswith("#") or not _del_pezzo(r):
                    continue
                righe.append([c.strip() for c in (r + [""] * 7)[:7]])

        blocchi, avvisi = [], []

        for cid, aff, fonte, data, tipo, liv, nota in righe:
            if liv.upper() not in ("PRIMARIA", "SECONDARIA_DOPPIA", "SECONDARIA_SINGOLA"):
                blocchi.append(f"[{cid}] livello di fonte non dichiarato")
                continue
            if liv.upper() != "SECONDARIA_SINGOLA":
                continue
            m = re.search(r"TESTATA:\s*([^|]+)\|(.+)", nota)
            if not m:
                blocchi.append(f"[{cid}] fonte singola senza TESTATA:<nome>|<ancora> in nota")
                continue
            testata, ancora = m.group(1).strip(), m.group(2).strip()
            ospiti = [f for f in frasi(testo) if ancora in f]
            if not ospiti:
                blocchi.append(f"[{cid}] ancora '{ancora}' assente dal testo")
            for f in ospiti:
                if testata.lower() not in f.lower():
                    blocchi.append(
                        f"[{cid}] fatto su fonte singola senza '{testata}' "
                        f"NELLA STESSA FRASE: \"{f[:70]}\"")

        for cid, aff, fonte, data, tipo, liv, nota in righe:
            if tipo == "stima":
                att = nota.split("|")[0].strip()
                anc = nota.split("|")[1].strip() if "|" in nota else ""
                if not att:
                    blocchi.append(f"[{cid}] stima senza attributore dichiarato")
                elif not anc:
                    blocchi.append(f"[{cid}] stima senza ancora numerica dichiarata in claims")
                else:
                    ospiti = [f for f in frasi(testo) if anc in f]
                    if not ospiti:
                        blocchi.append(f"[{cid}] ancora '{anc}' assente dal testo")
                    for f in ospiti:
                        if att not in f:
                            blocchi.append(f"[{cid}] stima '{anc}' di {att} senza attributore NELLA STESSA FRASE: \"{f[:70]}\"")

        for f in frasi(testo):
            for m in re.finditer(QUANT, f, re.I):
                coda = f[m.end():m.end()+14].lower()
                if re.match(r"\s*(mesi|mese|ore|ora|giorni|giorno|anni|anno|settimane|minuti|secondi|righe|volte)", coda):
                    continue                      # espressione di tempo o di misura, non deriva
                if "«" in f or '"' in f:
                    continue                      # dentro citazione altrui
                blocchi.append(f"quantificatore vago '{m.group(0)}' -> mettere la cifra: \"{f[:70]}\"")

        cond = [r for r in righe if "CONDIZIONALE" in r[6].upper()]
        for cid, aff, fonte, data, tipo, liv, nota in cond:
            chiave = re.split(r"[:,]", aff)[0].split()[0]
            for f in frasi(testo):
                if chiave.lower() in f.lower() and re.search(ASSERT, f, re.I):
                    blocchi.append(f"[{cid}] fonte condizionale resa assertiva: \"{f[:70]}\"")

        for f in frasi(testo):
            for m in re.finditer(SCOPE, f, re.I):
                avvisi.append(f"'{m.group(0)}' -> confermare che il perimetro della fonte copra l'intera frase: \"{f[:70]}\"")

        if avvisi:
            print("FERMATE DI PERIMETRO (da confermare a mano, una per una):")
            for a in avvisi:
                print("  ? " + a)
            print()
        if blocchi:
            print("FEDELTA NEGATA. Consegna bloccata. Derive rilevate:")
            for b in blocchi:
                print("  - " + b)
            print(f"\nTotale: {len(blocchi)}.")
            sys.exit(1)
        print(f"FEDELTA CONFERMATA. {len(righe)} righe, nessuna deriva.")
        print("Provenienza, attribuzione, quantificatori e modalita: puliti.")
        sys.exit(0)

    a = _argomenti()
    main(a[0], a[1])


def voce():
    import sys, re, json
    import numpy as np

    M = BANDE
    SUB=re.compile(r"\b(che|cui|quando|mentre|perch[eé]|poich[eé]|sebbene|ben[cq]h[eé]|dopo che|prima che|se|qualora|nonostante|dove)\b")
    def tok(t): return re.findall(r"\b[a-zàèéìòóùü']+\b", t.lower())
    def sents(t): return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", t) if len(s.strip())>1]
    def paras(t): return [p for p in t.split("\n\n") if len(p.strip())>20]

    def analizza(path):
        t=open(path,encoding="utf-8").read().replace("**","")
        toks=tok(t); ss=sents(t)
        sl=np.array([len(tok(s)) for s in ss if tok(s)])
        pl=np.array([len(sents(p)) for p in paras(t)]) if len(paras(t))>1 else np.array([len(ss)])
        ttr=[]
        for i in range(0,max(1,len(toks)-100),100):
            w=toks[i:i+100]
            if len(w)==100: ttr.append(len(set(w))/100)
        return dict(n_token=len(toks), n_frasi=len(sl),
          lung_frase_mean=float(np.mean(sl)), lung_frase_cv=float(np.std(sl)/np.mean(sl)),
          para_mean=float(np.mean(pl)), para_cv=float(np.std(pl)/np.mean(pl)) if len(pl)>1 else .4,
          virgole_frase=sum(s.count(",") for s in ss)/len(ss),
          subord_frase=sum(len(SUB.findall(s.lower())) for s in ss)/len(ss),
          ttr=float(np.mean(ttr)) if ttr else .77,
          f_corte=100*float(np.mean(sl<=6)), f_medie=100*float(np.mean((sl>=16)&(sl<=25))),
          f_lunghe=100*float(np.mean(sl>35)))

    LABELS={
     "lung_frase_mean":"lunghezza frase media (parole)",
     "lung_frase_cv":"burstiness frase (cv) [FIRMA] — più alto = più umano",
     "para_mean":"lunghezza paragrafo (frasi)",
     "para_cv":"varianza lunghezza paragrafi",
     "virgole_frase":"virgole per frase [FIRMA] — la tua sintassi a incisi",
     "subord_frase":"subordinate per frase",
     "ttr":"ricchezza lessicale TTR-100 [FIRMA]",
     "f_corte":"% frasi molto corte (<=6)",
     "f_medie":"% frasi medie (16-25) — se troppo alta = firma LLM",
     "f_lunghe":"% frasi lunghe (>35) — tuo marcatore forte",
    }
    CORE={"lung_frase_cv","virgole_frase","ttr"}  # assi costanti tra generi

    STOP=set("il lo la i gli le un uno una di a da in con su per tra fra e o ma che chi cui non si ci ne è era sono ha hanno del della dei delle dello degli al alla ai alle allo agli dal dalla dai dalle nel nella nei nelle sul sulla sui sulle come più anche se poi già solo questo questa quello quella lui lei loro suo sua suoi sue mi ti vi c' l' un' d' all' dell' nell' sull'".split())

    def dove(path, probl, B):
        # Indica DOVE guardare. Non suggerisce fusioni, tagli, sinonimi o ripetizioni: la correzione resta
        # una riscrittura che fa dire meglio la stessa cosa alla frase (stile-nucleo §16.24-B).
        t=open(path,encoding="utf-8").read().replace("**","")
        ss=[s for s in sents(t) if tok(s)]
        n=[len(tok(s)) for s in ss]
        def fascia(k): return "C" if k<=6 else ("m" if 16<=k<=25 else ("L" if k>35 else "b"))
        print(">> Mappa frasi (n:parole; C<=6, b 7-15, m 16-25, L>35): " + " ".join(f"{i+1}:{k}{fascia(k)}" for i,k in enumerate(n)))
        def lista(idx): return ", ".join(str(i+1) for i in idx[:8])
        if {"lung_frase_mean","lung_frase_cv","f_medie","f_lunghe","f_corte"} & set(probl):
            med=[i for i,k in enumerate(n) if 16<=k<=25]
            if med: print(f">> Frasi in fascia media da rileggere (riscrivere solo se la frase migliora): {lista(med)}")
        if "virgole_frase" in probl:
            nude=[i for i,s in enumerate(ss) if n[i]>12 and s.count(",")==0]
            if nude: print(f">> Frasi oltre 12 parole senza incisi da rileggere: {lista(nude)}")
        if "ttr" in probl:
            toks=tok(t); lo,hi=B["ttr"][0],B["ttr"][1]
            for i in range(0,max(1,len(toks)-100),100):
                w=toks[i:i+100]
                if len(w)<100: continue
                v=len(set(w))/100
                if v>hi or v<lo:
                    verso="troppo vario" if v>hi else "troppo ripetitivo"
                    print(f">> Finestra parole {i+1}-{i+100}: TTR {v:.2f}, lessico {verso}. Inizia con: \"{' '.join(w[:8])}...\"")
        print()

    def main(path, profilo, solo_core, soglia=1):
        B=M[profilo]
        a=analizza(path)
        print(f"=== CANCELLO VOCE — {path}  [profilo: {profilo}{' / solo firma' if solo_core else ''}] ===")
        print(f"token: {a['n_token']}  frasi: {a['n_frasi']}\n")
        probl=[]
        for k,lab in LABELS.items():
            if solo_core and k not in CORE: continue
            if k=="para_mean" and a["para_mean"]>40: continue  # blocco unico non paragrafato: salto
            lo,hi,med=B[k]; v=a[k]
            ok=lo<=v<=hi
            if not ok: probl.append(k)
            seg="  OK " if ok else ">>>> "
            dire="" if ok else (" [ALZA]" if v<lo else " [ABBASSA]")
            print(f"{seg}{lab}: {v:.2f}  (tuo {lo}–{hi}, mediana {med}){dire}")
        print()
        if not solo_core:
            if a["f_medie"]>B["f_medie"][1]:
                print(">> Troppe frasi medie: rileggi quelle in fascia media (voce --dove) e riscrivi solo quelle che migliorano (§16.24-B).")
            if a["f_lunghe"]<B["f_lunghe"][0] and profilo!="libri":
                print(">> Poche frasi lunghe: il periodo oltre 35 parole è un tuo marcatore. Cercalo dove il ragionamento lo chiede, mai fondendo frasi per spostare il numero (§16.24-B).")
            if a["lung_frase_cv"]<B["lung_frase_cv"][0]:
                print(">> Ritmo uniforme (metronomo): segnale N.1 dei detector. Aumenta la varianza.")
            if a["virgole_frase"]<B["virgole_frase"][0]:
                print(">> Poche virgole: mancano gli incisi. La tua frase si apre a metà, non fila dritta.")
            print()
        if probl or "--dove" in sys.argv:
            dove(path, probl, B)
        BLOCCO=len(probl)>=soglia
        print(f"Assi fuori range: {len(probl)} (blocco a partire da {soglia})")
        if not BLOCCO:
            if probl: print(f"VOCE ENTRO TOLLERANZA. Ai margini: {', '.join(probl)}. Accettabile, valuta un ritocco.")
            else: print("VOCE CONFERMATA. Profilo distribuzionale dentro il tuo range autentico.")
            sys.exit(0)
        print(f"VOCE DA CORREGGERE (blocco). {len(probl)} assi fuori: {', '.join(probl)}")
        sys.exit(1)

    args=_argomenti()
    if len(args)!=1:
        print("uso: python3 kit.py voce bozza.md [--profilo X] [--libri] [--core] [--dove]"); sys.exit(2)
    prof="libri" if "--libri" in sys.argv else (sys.argv[sys.argv.index("--profilo")+1] if "--profilo" in sys.argv else "giornalismo")
    main(args[0], prof, "--core" in sys.argv, 3 if "--bozza" in sys.argv else 1)


def conta():
    import sys, re

    FORMATI = {  # target, tolleranza (None = morbida)
        "buongiorno": (1600, 0.02), "colonna": (2200, 0.02), "articolo": (3800, 0.02),
        "newsletter": (6000, None), "urto": (4000, 0.02), "gaza": (1800, 0.02),
    }

    def titolo(righe, i):
        r = righe[i].strip()
        if r.startswith("#"):
            return True
        sopra = i == 0 or not righe[i-1].strip()
        sotto = i == len(righe)-1 or not righe[i+1].strip()
        return bool(r) and sopra and sotto and len(r) < 90 and not re.search(r"[.!?:;»\"”)]$", r)

    def conta(testo):
        righe = testo.rstrip("\n").split("\n")
        titoli = [righe[i].strip() for i in range(len(righe)) if titolo(righe, i)]
        corpo = "\n".join(r for i, r in enumerate(righe) if not titolo(righe, i)).strip("\n")
        corpo = re.sub(r"\n{3,}", "\n\n", corpo)
        return len(corpo.replace("**", "")), titoli

    def main():
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        if not args:
            print(__doc__); sys.exit(2)
        n, titoli = conta(open(args[0], encoding="utf-8").read())
        fmt = sys.argv[sys.argv.index("--formato")+1] if "--formato" in sys.argv else None
        print(f"BATTUTE: {n}  (titoli interni esclusi: {len(titoli)})")
        for t in titoli:
            print(f"  titolo: {t}")
        if "--target" in sys.argv:
            target, tol = int(sys.argv[sys.argv.index("--target")+1]), 0.02
            fmt = f"target {target}"
        elif not fmt or fmt == "libero":
            sys.exit(0)
        else:
            target, tol = FORMATI[fmt]
        if tol is None:
            print(f"Formato {fmt}: target ~{target}, tolleranza morbida. OK.")
            sys.exit(0)
        lo, hi = round(target*(1-tol)), round(target*(1+tol))
        ok = lo <= n <= hi
        print(f"Formato {fmt}: banda {lo}-{hi} -> {'DENTRO' if ok else 'FUORI'}"
              f"{'' if ok else f' ({n-hi:+d})' if n > hi else f' ({n-lo:+d})'}")
        sys.exit(0 if ok else 1)

    main()


# Caratteri vietati nel testo, scritti come codici: una copia del file non li puo' trasformare in spazi.
TRATTINI = r"[\u2014\u2013]"                          # em dash, trattino medio
INVISIBILI = r"[\u200b\u202f\u2009\u00a0\ufeff]"      # zero-width, narrow nbsp, thin space, nbsp, BOM


def scan():
    import sys, re

    BLOCCHI = [
        (TRATTINI, "em dash / trattino medio"),
        (INVISIBILI, "carattere Unicode invisibile"),
        (r",\s+ma\b", "virgola prima di 'ma'"),
        (r"(?i)\bfacciamo un passo indietro\b", "formula vietata sempre"),
        (r"(?i)\bda leggere piano\b", "locuzione-tic da evitare"),
        (r"(?i)\bc'è qualcosa di\b", "apertura metacognitiva"),
        (r"(?i)\b(in un mondo sempre più|nell'era digitale|nel panorama attuale|nel contesto odierno|in un'epoca in cui|mai come oggi|è interessante notare|vale la pena riflettere)\b", "apertura/formula bandita §3"),
    ]
    FERMATE = [
        (r"\b[Nn]on\b[^.!?\n]{1,80}?[,;:]?\s+(ma|bensì)\b", "possibile 'non X, ma Y' (ammesso solo: fatto puntuale, litote, antitesi fra categorie diverse)"),
        (r"\b[Nn]on (è|era|sono)\b[^.!?\n,]{1,50},\s+(è|era|sono)\b", "'non è X, è Y' intra-frase"),
        (r"\b[Nn]on (è|era|sono|si tratta di)\b[^.!?\n]{1,60}[.!?]\s+(È|Era|Sono|Si tratta)\b", "parallelismo-rivelazione cross-frase"),
        (r"[.!?]\s+Non (per|solo|da)\b[^.!?\n]{0,60}[.!?]\s+(Per|Ma|Da)\b", "pattern oppositivo frammentato"),
        (r"(?i)\b(certo|a prima vista|in superficie|mentre .{0,30}potrebbe sembrare|sebbene .{0,30}appaia)\b,", "forma sneaky"),
        (r"(?i)\b(cruciale|fondamentale|imprescindibile|panorama|scenario|ambito|epocale|senza precedenti|navigar\w*|plasmar\w*|abbracciar\w*|approfondi\w*|evidenziando|sottolineando|inoltre|tuttavia|in definitiva|detto questo|al contempo|rappresenta|costituisce|funge da|vanta|si configura)\b", "lessico bandito §3/§4"),
        (r"(?i)\b(al|nel) cuore d", "'cuore' metaforico"),
    ]

    def frase(t, pos):
        a = max(t.rfind(".", 0, pos), t.rfind("\n", 0, pos)) + 1
        b = min([x for x in (t.find(".", pos), t.find("\n", pos)) if x != -1] or [len(t)])
        return t[a:b+1].strip()[:110]

    def main():
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        if not args:
            print(__doc__); sys.exit(2)
        t = open(args[0], encoding="utf-8").read()
        pieno = t
        t = re.sub(r'«[^»]*»|"[^"\n]*"|“[^”]*”', lambda m: " " * len(m.group()), t)
        blocchi, fermate = [], []
        if "--radio" in sys.argv and "**" in t:
            blocchi.append(("grassetto in testo radiofonico", "**"))
        for pat, lab in BLOCCHI:
            testo = pieno if lab in ("em dash / trattino medio", "carattere Unicode invisibile") else t
            for m in re.finditer(pat, testo):
                blocchi.append((lab, frase(pieno, m.start())))
        for pat, lab in FERMATE:
            for m in re.finditer(pat, t):
                fermate.append((lab, m.group(0)[:60], frase(pieno, m.start())))
        if fermate:
            print("FERMATE (giudicare a mano):")
            for lab, hit, fr in fermate:
                print(f"  ? {lab} [{hit}]: \"{fr}\"")
        if blocchi:
            print(f"SCAN NEGATO. {len(blocchi)} blocchi:")
            for lab, fr in blocchi:
                print(f"  - {lab}: \"{fr}\"")
            sys.exit(1)
        print(f"SCAN PULITO. Blocchi: 0. Fermate da giudicare: {len(fermate)}.")
        sys.exit(0)

    main()


def selftest():
    import sys, os, tempfile, subprocess

    me = os.path.abspath(__file__)
    errori = []
    sorgente = open(me, encoding="utf-8").read()
    for c in "\u200b\u202f\u2009\u00a0\ufeff":
        if c in sorgente:
            errori.append(f"il sorgente contiene U+{ord(c):04X} letterale: va scritto come codice")
    casi = [("testo pulito", "Testo con spazi normali, tutto in regola.\n", 0)]
    casi += [(f"U+{ord(c):04X}", f"Testo{c}con un carattere nascosto.\n", 1) for c in "\u200b\u202f\u2009\u00a0\ufeff"]
    casi += [(f"U+{ord(c):04X}", f"Testo {c} con un trattino.\n", 1) for c in "\u2014\u2013"]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prova.md")
        for nome, testo, atteso in casi:
            open(p, "w", encoding="utf-8").write(testo)
            rc = subprocess.run([sys.executable, me, "scan", p], capture_output=True, text=True).returncode
            if rc != atteso:
                esito = "bloccato" if rc else "lasciato passare"
                errori.append(f"scan ha {esito} il caso '{nome}'")
    if errori:
        print("KIT CORROTTO. La copia in lavoro non e' fedele: riscriverla dal Progetto, mai rattoppare.")
        for e in errori:
            print("  - " + e)
        sys.exit(1)
    print(f"KIT INTEGRO. Versione {VERSIONE}. {len(casi)} casi di prova superati.")
    sys.exit(0)


def seo():
    import sys, re

    # Prompt immagine (aggiunto il 20 novembre 2026, dopo un prompt A uscito fotografico).
    # Righe A: (simbolico, Nanobanana/Gemini) e B: (figure reali, ChatGPT, in inglese).
    # Regole: composizione grafica elegante stile New Yorker, mai resa fotografica,
    # mai caricatura, nessuna scritta, formato dentro il testo, B = un'unica immagine
    # composita con i volti presi dalle foto vere allegate.
    APERTURA = "elegant graphic composition in the style of the new yorker, may include stylized photographic elements"
    NEGAZIONI = r"\b(no|non|nessun|nessuna|nessuno|niente|mai|senza|without|not|né|nor)\b"
    VIETATI = [
        (r"photo ?realis|fotorealis|iperrealis|hyperrealis|realistic|realistica|realistico|realismo", "resa realistica"),
        (r"photo style|photographic style|editorial photo|stile fotografico|resa fotografica|\bfotografia\b|fotografia (simbolica|editoriale)|\bscatto\b|\bshot on\b|\bphotograph(y|ed)\b", "linguaggio fotografico"),
        (r"golden hour|bokeh|fuori fuoco|out of focus|depth of field|profondità di campo|\blens\b|obiettivo|grandangol|wide[- ]angle|\bluce (fredda|calda|naturale|morbida|radente|dell)|\blighting\b|illuminazione|cinematic|cinematografic|studio light|luce da set", "luce o ottica da fotografia"),
        (r"caricatur|cartoon|vignett|satiric|enlarged head|big head|teste ingrandit|exaggerated|esagerat|grotesque|grottesc", "caricatura o satira"),
    ]
    VIETATI_B = [
        (r"redraw|re-draw|ridisegn|reinvent|reinvent|illustrated faces?|volti? (disegnat|illustrat|stilizzat)|stylized faces?|generated faces?|lookalike|somiglian", "volti non presi dalle foto vere"),
        (r"separate (images|graphics|elements)|grafiche separate|immagini separate|più immagini|multiple images", "immagini separate invece di una composita"),
    ]

    def negato(s, pos):
        segmento = re.split(r"[,.;:]", s[max(0, pos-60):pos])[-1]
        return re.search(NEGAZIONI, segmento, re.I) is not None

    def controlla_prompt(k, s):
        errori = []
        corpo = s.strip().strip("\"'«»“”").strip()
        basso = corpo.lower()
        if not basso.startswith(APERTURA):
            errori.append("manca la formula d'apertura obbligatoria (\"Elegant graphic composition in the style of The New Yorker, may include stylized photographic elements\")")
        if not re.search(r"\b(16:9|3:2)\b", corpo[:300]):
            errori.append("formato orizzontale (16:9 o 3:2) assente dall'apertura del prompt")
        if not re.search(r"\bno text\b|nessun testo|niente testo", basso):
            errori.append("manca il divieto esplicito di testo (\"no text\" / \"nessun testo\")")
        if re.search(r"[«»“”]|\"[^\"]{2,}\"", corpo):
            errori.append("virgolette dentro il prompt: possibile scritta da far comparire nell'immagine")
        regole = VIETATI + (VIETATI_B if k == "B" else [])
        for pat, lab in regole:
            for m in re.finditer(pat, corpo, re.I):
                if not negato(corpo, m.start()):
                    errori.append(f"{lab}: \"{m.group(0)}\"")
        if k == "A" and not re.search(r"flat ink|inchiostro piatto|inchiostro", basso):
            errori.append("prompt A: manca la resa a inchiostro piatto (flat ink)")
        if k == "A" and not re.search(r"desaturat", basso):
            errori.append("prompt A: manca la palette desaturata")
        if k == "B":
            if not re.search(r"\bno lettering\b", basso):
                errori.append("prompt B: manca \"no lettering\"")
            if not re.search(r"real photograph|photos i upload|photographs i upload", basso):
                errori.append("prompt B: i volti devono venire dalle foto vere caricate (\"real photographs I upload\")")
            if not re.search(r"one single|single finished|single composite", basso):
                errori.append("prompt B: deve chiedere un'unica immagine composita finita (\"one single finished composite image\")")
            if re.search(r"\b(della|delle|dei|con|una|nella|sullo|sfondo|composizione)\b", basso):
                errori.append("prompt B: va scritto in inglese per ChatGPT")
        return errori

    def main():
        if len(sys.argv) != 2:
            print(__doc__); sys.exit(2)
        visti, bloccato = set(), False
        for riga in open(sys.argv[1], encoding="utf-8"):
            riga = riga.rstrip("\n")
            if len(riga) < 3 or riga[1] != ":":
                continue
            k, s = riga[0].upper(), riga[2:].strip()
            visti.add(k)
            n, w = len(s), len(s.split())
            if k in ("A", "B"):
                errori = controlla_prompt(k, s)
                if errori:
                    bloccato = True
                    print(f"[{k}] PROMPT FUORI REGOLA:")
                    for e in errori:
                        print(f"      - {e}")
                else:
                    print(f"[{k}] PROMPT OK  {s[:90]}...")
                continue
            if k == "S":
                esito = "OK 130" if n == 130 else f"{n-130:+d}"
                bloccato |= n != 130
            elif k == "T":
                esito = "OK" if n <= 60 else f"+{n-60} oltre 60"
                bloccato |= n > 60
            elif k == "N":
                esito = "OK" if 9 <= w <= 17 and "?" not in s else "FUORI REGOLA §12-bis"
            else:
                esito = ""
            print(f"[{k}] {n:>3} car {w:>2} par  {esito:<16} {s}")
        if "S" in visti and not {"A", "B"} <= visti:
            bloccato = True
            print("PACCHETTO INCOMPLETO: mancano le righe A: e/o B: con i prompt immagine.")
        if bloccato:
            print("SEO NEGATO. Correggere prima di consegnare.")
            sys.exit(1)
        print("SEO CONFERMATO. Misure e prompt in regola.")
        sys.exit(0)

    main()


def agenzie():
    import sys, os, re

    KW = (r"gaza|israel|palestin|cisgiordania|west bank|hamas|idf|tsahal|netanyahu|unrwa|ocha|"
          r"rafah|khan y[uo]nis|jabalia|deir al|nuseirat|cessate il fuoco|tregua|flotilla|"
          r"cig|corte internazionale|cpi|aiuti umanitari|coloni|ostaggi|beirut|hezbollah")
    ESCLUSI = r"\b(calcio|borsa|meteo|sport|serie a|champions|campionato|spread|ftse)\b"

    def leggi(path):
        raw = open(path, "rb").read()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            t = raw.decode("cp1252", errors="ignore")
        t = t.replace("\r", "")
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", t)

    def main():
        files = [a for a in sys.argv[1:] if not a.startswith("--")]
        kw = KW
        if "--kw" in sys.argv:
            extra = sys.argv[sys.argv.index("--kw")+1]
            files = [f for f in files if f != extra]
            kw = KW + "|" + extra
        if not files:
            print(__doc__); sys.exit(2)
        os.makedirs("agenzie_pulite", exist_ok=True)
        visti, n = set(), 0
        for f in files:
            t = leggi(f)
            nome = os.path.basename(f)
            open(os.path.join("agenzie_pulite", nome), "w", encoding="utf-8").write(t)
            for i, riga in enumerate(t.split("\n"), 1):
                r = riga.strip()
                if not r or not re.search(kw, r, re.I) or re.search(ESCLUSI, r, re.I):
                    continue
                chiave = r[:120].lower()
                if chiave in visti:
                    continue
                visti.add(chiave)
                n += 1
                print(f"{nome}:{i}:{r[:220]}")
        print(f"\n{n} righe indicizzate da {len(files)} file. Copie pulite in agenzie_pulite/.")

    main()


def fixbdr():
    import sys, re, zipfile, shutil, os

    ORDINE = ["top", "left", "start", "bottom", "right", "end", "between", "bar"]
    FIGLIO = re.compile(r"<w:(\w+)\b[^>]*?(?:/>|>.*?</w:\1>)", re.S)

    def riordina(xml):
        def fix(m):
            interno = m.group(2)
            figli = [(f.group(1), f.group(0)) for f in FIGLIO.finditer(interno)]
            figli.sort(key=lambda x: ORDINE.index(x[0]) if x[0] in ORDINE else 99)
            return m.group(1) + "".join(f for _, f in figli) + "</w:pBdr>"
        return re.sub(r"(<w:pBdr\b[^>]*>)(.*?)</w:pBdr>", fix, xml, flags=re.S)

    def main():
        if len(sys.argv) < 2:
            print(__doc__); sys.exit(2)
        for path in sys.argv[1:]:
            tmp = path + ".tmp"
            n = 0
            with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                        x = data.decode("utf-8")
                        y = riordina(x)
                        if y != x:
                            n += 1
                            data = y.encode("utf-8")
                    zout.writestr(item, data)
            shutil.move(tmp, path)
            print(f"{os.path.basename(path)}: {n} parti XML riordinate")

    main()


def qc():
    import sys, os, subprocess

    D = os.path.dirname(os.path.abspath(__file__))

    def run(nome, argv):
        p = subprocess.run([sys.executable, os.path.abspath(__file__), nome.replace(".py", "")] + argv,
                           capture_output=True, text=True)
        return p.returncode, (p.stdout + p.stderr).strip()

    def main():
        if "--formato" not in sys.argv:
            print(__doc__); sys.exit(2)
        fmt = sys.argv[sys.argv.index("--formato")+1]
        tgt = sys.argv[sys.argv.index("--target")+1] if "--target" in sys.argv else None
        args = _argomenti()
        if len(args) != 2:
            print(__doc__); sys.exit(2)
        bozza, claims = args
        flags_voce = [f for f in ("--libri", "--core", "--bozza") if f in sys.argv]
        prof = sys.argv[sys.argv.index("--profilo")+1] if "--profilo" in sys.argv else PROFILO_FORMATO.get(fmt, "giornalismo")
        if "--libri" not in sys.argv: flags_voce += ["--profilo", prof]
        pez = ["--pezzo", sys.argv[sys.argv.index("--pezzo")+1]] if "--pezzo" in sys.argv else []
        import json
        fgiri = os.path.join(os.path.dirname(os.path.abspath(bozza)), "qc_giri.json")
        try: giri = json.load(open(fgiri, encoding="utf-8"))
        except Exception: giri = {}
        chiave = os.path.basename(bozza); giri[chiave] = giri.get(chiave, 0) + 1
        json.dump(giri, open(fgiri, "w", encoding="utf-8"))
        passi = [
            ("0 kit", "selftest", []),
            ("1 provenienza", "cancello.py", [bozza, claims] + pez),
            ("2 fedeltà", "fedelta.py", [bozza, claims] + pez),
            ("3 voce", "voce.py", [bozza] + flags_voce),
            ("battute", "conta.py", [bozza, "--formato", fmt] + (["--target", tgt] if tgt else [])),
            ("scan formale", "scan.py", [bozza] + (["--radio"] if fmt == "urto" else [])),
        ]
        log, righe, tutto_ok = [], [], True
        for etichetta, script, argv in passi:
            rc, out = run(script, argv)
            log.append(f"===== {script} (exit {rc}) =====\n{out}\n")
            ok = rc == 0
            tutto_ok &= ok
            linee = out.splitlines()
            sintesi = next((l for l in reversed(linee) if l.strip() and not l.startswith(("  ", "\t"))), "")
            if script == "conta.py":
                sintesi = " | ".join(l for l in linee if l.startswith(("BATTUTE", "Formato")))
            dettagli = [l.strip() for l in linee
                        if l.startswith(("  - ", "  ? ", ">>>> ", ">> "))]
            righe.append((etichetta, "OK" if ok else "BLOCCO", sintesi, dettagli))
        open(os.path.join(os.path.dirname(os.path.abspath(bozza)), "qc_log.txt"), "w",
             encoding="utf-8").write("\n".join(log))
        print("| Cancello | Esito | Sintesi |\n|---|---|---|")
        for e, esito, s, _ in righe:
            print(f"| {e} | {esito} | {s.replace('|', '/')} |")
        g = giri[chiave]
        print(f"| giro qc | {'OK' if g <= 2 else 'OLTRE IL TETTO'} | {chiave}: giro {g} di 2 · profilo voce {prof if '--libri' not in sys.argv else 'libri'}{' · pezzo ' + pez[1] if pez else ''} |")
        for e, _, _, det in righe:
            if det:
                print(f"\n{e}:")
                for d in det:
                    print(f"  {d}")
        sys.exit(0 if tutto_ok else 1)

    main()

COMANDI = {"cancello": cancello, "fedelta": fedelta, "voce": voce, "conta": conta, "scan": scan,
           "seo": seo, "agenzie": agenzie, "fixbdr": fixbdr, "qc": qc, "selftest": selftest}
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDI:
        print(__doc__); sys.exit(2)
    cmd = sys.argv.pop(1)
    COMANDI[cmd]()
