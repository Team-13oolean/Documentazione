# Elenco dei casi d'uso — AIRA (13oolean)

**122 casi d'uso** (70 di primo livello, 52 sotto-UC), di cui 85 obbligatori, 19 desiderabili e 18 opzionali. Ogni UC ha il proprio diagramma UML nello zip (`uml_uc/`), più `Attori.png` con la gerarchia degli attori.

**Convenzioni**
- Numerazione gerarchica come nel documento di riferimento: `UC N.k` è un sotto-UC di `UC N` (estensione, tipicamente un errore, oppure inclusione); `UC N.k.m` è un sotto-UC di `UC N.k`.
- Nome file: `UC` + codice con i punti sostituiti da `_` (UC 1.1.1 → `UC1_1_1.png`), così non ci sono punti nei nomi file per `\includegraphics`.
- Importanza dell'UC = quella del requisito più importante da cui deriva.
- Ogni fallimento che porta a «non riuscita» include **UC 34** (marcatura), che a sua volta include **UC 37** (registrazione nei log); gli errori che richiedono solo il log includono direttamente UC 37.
- Negli UC di errore la colonna Attori riporta «come UCx»: l'attore è quello del UC base, come nel vostro esempio.


## Macroarea 1 — Acquisizione delle richieste dai canali

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC1 | Acquisizione e-mail dalla casella monitorata | Mittente, Canale di ingresso | — | R1-F | Obbligatorio | `UC1.png` |
| UC1.1 | &nbsp;&nbsp;Acquisizione degli allegati PDF e immagine dell'e-mail | (come UC1) | estende UC1 | R2-F | Obbligatorio | `UC1_1.png` |
| UC1.1.1 | &nbsp;&nbsp;&nbsp;&nbsp;Segnalazione allegato non supportato o non leggibile | (come UC1.1) | estende UC1.1; include UC34 | R3-F | Obbligatorio | `UC1_1_1.png` |
| UC2 | Acquisizione messaggio vocale WhatsApp | Mittente, Canale di ingresso | — | R4-F | Obbligatorio | `UC2.png` |
| UC3 | Acquisizione messaggio testuale WhatsApp | Mittente, Canale di ingresso | — | R5-F | Desiderabile | `UC3.png` |
| UC4 | Acquisizione immagine WhatsApp | Mittente, Canale di ingresso | — | R5-F | Desiderabile | `UC4.png` |
| UC5 | Acquisizione file da cartella del filesystem | Mittente, Canale di ingresso | — | R6-F | Desiderabile | `UC5.png` |
| UC6 | Gestione errore di accesso al canale | — | estende UC1, UC2, UC3, UC4, UC5; include UC37 | R7-F | Obbligatorio | `UC6.png` |

## Macroarea 2 — Filtro di sicurezza in ingresso

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC7 | Identificazione del mittente | Mittente | — | R8-F | Obbligatorio | `UC7.png` |
| UC7.1 | &nbsp;&nbsp;Blocco della richiesta di un mittente non autenticato | (come UC7) | estende UC7; include UC37 | R9-F | Obbligatorio | `UC7_1.png` |
| UC8 | Verifica dell'autorizzazione del tenant | Mittente | — | R10-F | Obbligatorio | `UC8.png` |
| UC8.1 | &nbsp;&nbsp;Blocco della richiesta di un tenant non autorizzato | (come UC8) | estende UC8; include UC37 | R11-F | Obbligatorio | `UC8_1.png` |
| UC9 | Controllo anti-spam delle e-mail | Mittente | — | R13-F | Obbligatorio | `UC9.png` |
| UC9.1 | &nbsp;&nbsp;Scarto dell'e-mail classificata come spam | (come UC9) | estende UC9; include UC37 | R13-F | Obbligatorio | `UC9_1.png` |
| UC10 | Rilevamento delle richieste duplicate | Mittente | — | R14-F | Obbligatorio | `UC10.png` |
| UC10.1 | &nbsp;&nbsp;Scarto della richiesta duplicata | (come UC10) | estende UC10; include UC37 | R14-F | Obbligatorio | `UC10_1.png` |
| UC11 | Anonimizzazione delle informazioni private | Mittente | — | R15-F | Obbligatorio | `UC11.png` |
| UC11.1 | &nbsp;&nbsp;Errore di anonimizzazione | (come UC11) | estende UC11; include UC34 | R16-F | Obbligatorio | `UC11_1.png` |
| UC12 | Aggiornamento dell'anagrafica clienti tramite elaborazione batch | Amministratore | — | R17-F | Obbligatorio | `UC12.png` |
| UC12.1 | &nbsp;&nbsp;Segnalazione di errori di formato o contenuto nell'anagrafica | (come UC12) | estende UC12 | R18-F | Obbligatorio | `UC12_1.png` |
| UC13 | Consultazione dell'anagrafica clienti | Utente in sola lettura | — | R19-F | Desiderabile | `UC13.png` |

## Macroarea 3 — Estrazione dei dati multimodale

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC14 | Trascrizione del messaggio vocale | Mittente, Motore di estrazione (OCR / Speech-to-Text) | — | R20-F | Obbligatorio | `UC14.png` |
| UC14.1 | &nbsp;&nbsp;Errore di trascrizione audio | (come UC14) | estende UC14; include UC34 | R21-F | Obbligatorio | `UC14_1.png` |
| UC15 | Estrazione del testo da immagine allegata | Mittente, Motore di estrazione (OCR / Speech-to-Text) | — | R22-F | Obbligatorio | `UC15.png` |
| UC15.1 | &nbsp;&nbsp;Errore di estrazione OCR | (come UC15) | estende UC15, UC16, UC17.1; include UC34 | R24-F | Obbligatorio | `UC15_1.png` |
| UC16 | Estrazione del testo da fotografia ricevuta come messaggio autonomo | Mittente, Motore di estrazione (OCR / Speech-to-Text) | — | R23-F | Desiderabile | `UC16.png` |
| UC17 | Estrazione del testo da allegato PDF | Mittente, Motore di estrazione (OCR / Speech-to-Text) | — | R25-F | Obbligatorio | `UC17.png` |
| UC17.1 | &nbsp;&nbsp;Estrazione del testo tramite OCR da PDF scansionato | (come UC17) | estende UC17 | R25-F | Obbligatorio | `UC17_1.png` |
| UC17.2 | &nbsp;&nbsp;Errore di lettura del PDF | (come UC17) | estende UC17; include UC34 | R26-F | Obbligatorio | `UC17_2.png` |
| UC18 | Raffinamento dell'estrazione tramite LLM | Mittente, LLM | — | R27-F | Obbligatorio | `UC18.png` |
| UC18.1 | &nbsp;&nbsp;Errore del servizio LLM nel raffinamento | (come UC18) | estende UC18; include UC37 | R28-F | Obbligatorio | `UC18_1.png` |
| UC19 | Valutazione dell'affidabilità rispetto alla soglia di confidenza | Mittente | — | R29-F | Obbligatorio | `UC19.png` |
| UC19.1 | &nbsp;&nbsp;Dati sotto soglia di confidenza o insufficienti | (come UC19) | estende UC19; include UC34 | R30-F | Obbligatorio | `UC19_1.png` |

## Macroarea 4 — Elaborazione semantica e strutturazione

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC20 | Identificazione dell'intenzione principale | Mittente, LLM | include UC20.1 | R31-F | Obbligatorio | `UC20.png` |
| UC20.1 | &nbsp;&nbsp;Tracciamento delle informazioni secondarie o escluse | (come UC20) | — | R34-F | Obbligatorio | `UC20_1.png` |
| UC20.2 | &nbsp;&nbsp;Errore del servizio LLM nella classificazione | (come UC20) | estende UC20; include UC37 | R32-F | Obbligatorio | `UC20_2.png` |
| UC20.3 | &nbsp;&nbsp;Intenzione non determinabile o non supportata | (come UC20) | estende UC20; include UC34 | R33-F | Obbligatorio | `UC20_3.png` |
| UC21 | Estrazione delle entità dell'ordine d'acquisto | Mittente, LLM | — | R35-F | Obbligatorio | `UC21.png` |
| UC21.1 | &nbsp;&nbsp;Errore del servizio LLM nell'estrazione delle entità | (come UC21) | estende UC21; include UC37 | R36-F | Obbligatorio | `UC21_1.png` |
| UC21.2 | &nbsp;&nbsp;Rilevamento di informazioni mancanti imputabili al mittente | (come UC21) | estende UC21; include UC34 | R40-F | Obbligatorio | `UC21_2.png` |
| UC21.2.1 | &nbsp;&nbsp;&nbsp;&nbsp;Contatto diretto del mittente per le informazioni mancanti | Mittente, Servizio di posta in uscita | estende UC21.2 | R106-F | Opzionale | `UC21_2_1.png` |
| UC21.3 | &nbsp;&nbsp;Mappatura delle descrizioni informali sui codici articolo | LLM | estende UC21 | R44-F | Desiderabile | `UC21_3.png` |
| UC22 | Strutturazione dei dati dell'ordine in template JSON | Mittente | — | R37-F | Obbligatorio | `UC22.png` |
| UC22.1 | &nbsp;&nbsp;Errore di validazione dello schema JSON | (come UC22) | estende UC22, UC23; include UC34 | R39-F | Obbligatorio | `UC22_1.png` |
| UC23 | Strutturazione in template JSON per altre tipologie di richiesta | Mittente | — | R38-F | Desiderabile | `UC23.png` |
| UC24 | Applicazione della priorità al testo del messaggio | Mittente | include UC24.1 | R41-F | Obbligatorio | `UC24.png` |
| UC24.1 | &nbsp;&nbsp;Registrazione delle discrepanze tra testo e allegato | (come UC24) | include UC37 | R42-F | Obbligatorio | `UC24_1.png` |
| UC25 | Scomposizione di un messaggio in richieste indipendenti | Mittente, LLM | — | R43-F | Opzionale | `UC25.png` |

## Macroarea 5 — Azioni, integrazione e gestione delle anomalie

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC26 | Avvio automatico di azioni secondo le regole configurate | Mittente | — | R45-F | Obbligatorio | `UC26.png` |
| UC26.1 | &nbsp;&nbsp;Nessuna regola applicabile alla richiesta | (come UC26) | estende UC26; include UC34 | R46-F | Obbligatorio | `UC26_1.png` |
| UC27 | Inoltro dei dati strutturati agli applicativi tramite API REST | Mittente, Applicativo aziendale di destinazione | — | R47-F | Obbligatorio | `UC27.png` |
| UC27.1 | &nbsp;&nbsp;Errore di invocazione delle API REST | (come UC27) | estende UC27; include UC37 | R48-F | Obbligatorio | `UC27_1.png` |
| UC28 | Creazione automatica dell'ordine d'acquisto sul portale B2B | Mittente, Applicativo aziendale di destinazione | specializza UC27 | R49-F | Obbligatorio | `UC28.png` |
| UC29 | Apertura automatica di un ticket di assistenza | Mittente, Applicativo aziendale di destinazione | specializza UC27 | R50-F | Desiderabile | `UC29.png` |
| UC30 | Registrazione automatica di un appuntamento | Mittente, Applicativo aziendale di destinazione | specializza UC27 | R51-F | Desiderabile | `UC30.png` |
| UC31 | Registrazione automatica di un'opportunità commerciale nel CRM | Mittente, Applicativo aziendale di destinazione | specializza UC27 | R52-F | Desiderabile | `UC31.png` |
| UC32 | Inoltro all'ERP di una richiesta di documento contabile | Mittente, Applicativo aziendale di destinazione | specializza UC27 | R53-F | Desiderabile | `UC32.png` |
| UC33 | Invio automatico di e-mail di notifica | Mittente, Servizio di posta in uscita | — | R54-F | Obbligatorio | `UC33.png` |
| UC33.1 | &nbsp;&nbsp;Errore di invio e-mail con ritentativo | (come UC33) | estende UC33; include UC37 | R55-F | Obbligatorio | `UC33_1.png` |
| UC34 | Marcatura della richiesta come non riuscita | Mittente | include UC37 | R56-F | Obbligatorio | `UC34.png` |
| UC35 | Persistenza di testo estratto, payload e stato della richiesta | Mittente | — | R57-F | Obbligatorio | `UC35.png` |
| UC35.1 | &nbsp;&nbsp;Errore di persistenza con ritentativo | (come UC35) | estende UC35; include UC37 | R58-F | Obbligatorio | `UC35_1.png` |
| UC36 | Cifratura e salvataggio dei file originali allegati | Mittente | — | R59-F | Obbligatorio | `UC36.png` |
| UC37 | Registrazione degli eventi della pipeline nei log | Mittente | — | R60-F | Obbligatorio | `UC37.png` |

## Macroarea 6 — Interfaccia amministrativa e profili di accesso

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC38 | Autenticazione utente | Utente in sola lettura | — | R61-F | Obbligatorio | `UC38.png` |
| UC38.1 | &nbsp;&nbsp;Errore di autenticazione | (come UC38) | estende UC38 | R62-F | Obbligatorio | `UC38_1.png` |
| UC39 | Logout utente | Utente in sola lettura | — | R63-F | Obbligatorio | `UC39.png` |
| UC40 | Creazione di un utente con profilo di accesso | Amministratore | — | R66-F | Obbligatorio | `UC40.png` |
| UC40.1 | &nbsp;&nbsp;Errore identificativo utente già esistente | (come UC40) | estende UC40 | R69-F | Obbligatorio | `UC40_1.png` |
| UC40.2 | &nbsp;&nbsp;Errore profilo di accesso non valido | (come UC40) | estende UC40, UC41 | R69-F | Obbligatorio | `UC40_2.png` |
| UC41 | Modifica del profilo di accesso di un utente | Amministratore | — | R67-F | Obbligatorio | `UC41.png` |
| UC42 | Rimozione di un utente | Amministratore | — | R68-F | Obbligatorio | `UC42.png` |
| UC43 | Visualizzazione dei canali di ingresso e del loro stato | Utente in sola lettura | — | R70-F | Obbligatorio | `UC43.png` |
| UC44 | Configurazione di un nuovo canale di ingresso | Amministratore | — | R71-F | Obbligatorio | `UC44.png` |
| UC44.1 | &nbsp;&nbsp;Errore di validazione dei parametri di configurazione | (come UC44) | estende UC44, UC45, UC53, UC54, UC55, UC56 | R75-F | Obbligatorio | `UC44_1.png` |
| UC45 | Modifica dei parametri di un canale di ingresso | Amministratore | — | R72-F | Obbligatorio | `UC45.png` |
| UC46 | Rimozione di un canale di ingresso | Amministratore | — | R73-F | Obbligatorio | `UC46.png` |
| UC47 | Attivazione di un canale di ingresso | Amministratore | — | R74-F | Obbligatorio | `UC47.png` |
| UC48 | Disattivazione di un canale di ingresso | Amministratore | — | R74-F | Obbligatorio | `UC48.png` |
| UC49 | Visualizzazione delle regole di azione e notifica | Utente in sola lettura | — | R76-F | Obbligatorio | `UC49.png` |
| UC50 | Creazione di una regola di azione o notifica | Gestore | — | R77-F | Obbligatorio | `UC50.png` |
| UC51 | Modifica di una regola di azione o notifica | Gestore | — | R78-F | Obbligatorio | `UC51.png` |
| UC52 | Eliminazione di una regola di azione o notifica | Gestore | — | R79-F | Obbligatorio | `UC52.png` |
| UC53 | Configurazione degli applicativi aziendali di destinazione | Amministratore | — | R80-F | Obbligatorio | `UC53.png` |
| UC54 | Configurazione e sostituzione del modello LLM | Amministratore | — | R81-F | Obbligatorio | `UC54.png` |
| UC55 | Configurazione della posta in uscita | Amministratore | — | R82-F | Obbligatorio | `UC55.png` |
| UC56 | Impostazione della soglia di confidenza | Amministratore | — | R83-F | Obbligatorio | `UC56.png` |
| UC57 | Consultazione dello storico dei log | Utente in sola lettura | — | R84-F | Obbligatorio | `UC57.png` |
| UC57.1 | &nbsp;&nbsp;Errore nel recupero dello storico dei log | (come UC57) | estende UC57 | R85-F | Obbligatorio | `UC57_1.png` |
| UC57.2 | &nbsp;&nbsp;Filtraggio dello storico dei log | (come UC57) | estende UC57 | R86-F | Desiderabile | `UC57_2.png` |
| UC57.2.1 | &nbsp;&nbsp;&nbsp;&nbsp;Filtraggio dei log per periodo | (come UC57.2) | estende UC57.2 | R86-F | Desiderabile | `UC57_2_1.png` |
| UC57.2.2 | &nbsp;&nbsp;&nbsp;&nbsp;Filtraggio dei log per canale | (come UC57.2) | estende UC57.2 | R86-F | Desiderabile | `UC57_2_2.png` |
| UC57.2.3 | &nbsp;&nbsp;&nbsp;&nbsp;Filtraggio dei log per tenant | (come UC57.2) | estende UC57.2 | R86-F | Desiderabile | `UC57_2_3.png` |
| UC57.2.4 | &nbsp;&nbsp;&nbsp;&nbsp;Filtraggio dei log per tipologia | (come UC57.2) | estende UC57.2 | R86-F | Desiderabile | `UC57_2_4.png` |
| UC57.2.5 | &nbsp;&nbsp;&nbsp;&nbsp;Filtraggio dei log per esito | (come UC57.2) | estende UC57.2 | R86-F | Desiderabile | `UC57_2_5.png` |
| UC58 | Consultazione delle richieste persistite e del loro stato | Utente in sola lettura | — | R87-F | Obbligatorio | `UC58.png` |
| UC58.1 | &nbsp;&nbsp;Visualizzazione del dettaglio di una richiesta | (come UC58) | estende UC58; include UC58.1.1, UC58.1.2, UC58.1.3, UC58.1.4, UC58.1.5 | R88-F | Obbligatorio | `UC58_1.png` |
| UC58.1.1 | &nbsp;&nbsp;&nbsp;&nbsp;Visualizzazione del testo estratto della richiesta | (come UC58.1) | — | R88-F | Obbligatorio | `UC58_1_1.png` |
| UC58.1.2 | &nbsp;&nbsp;&nbsp;&nbsp;Visualizzazione del payload della richiesta | (come UC58.1) | — | R88-F | Obbligatorio | `UC58_1_2.png` |
| UC58.1.3 | &nbsp;&nbsp;&nbsp;&nbsp;Visualizzazione dello stato della richiesta | (come UC58.1) | — | R88-F | Obbligatorio | `UC58_1_3.png` |
| UC58.1.4 | &nbsp;&nbsp;&nbsp;&nbsp;Visualizzazione delle azioni eseguite sulla richiesta | (come UC58.1) | — | R88-F | Obbligatorio | `UC58_1_4.png` |
| UC58.1.5 | &nbsp;&nbsp;&nbsp;&nbsp;Visualizzazione delle anomalie registrate per la richiesta | (come UC58.1) | — | R88-F | Obbligatorio | `UC58_1_5.png` |
| UC58.1.6 | &nbsp;&nbsp;&nbsp;&nbsp;Consultazione degli allegati originali conservati | (come UC58.1) | estende UC58.1 | R89-F | Desiderabile | `UC58_1_6.png` |
| UC59 | Ritentativo dell'inoltro di una richiesta | Gestore, Applicativo aziendale di destinazione | include UC27 | R90-F | Desiderabile | `UC59.png` |
| UC60 | Eliminazione delle richieste persistite | Amministratore | — | R91-F | Obbligatorio | `UC60.png` |
| UC60.1 | &nbsp;&nbsp;Errore nell'eliminazione dei dati persistiti | (come UC60) | estende UC60 | R92-F | Obbligatorio | `UC60_1.png` |

## Macroarea 7 — Funzionalità opzionali ed estensioni

| Codice | Titolo | Attori | Relazioni UML | Requisiti | Imp. | File immagine |
|---|---|---|---|---|---|---|
| UC61 | Instradamento di una richiesta non riuscita nella coda di revisione umana | Mittente | estende UC34 | R93-F | Opzionale | `UC61.png` |
| UC62 | Visualizzazione della coda di revisione umana | Gestore | include UC62.1 | R94-F | Opzionale | `UC62.png` |
| UC62.1 | &nbsp;&nbsp;Visualizzazione di motivo ed elemento problematico di una richiesta in revisione | (come UC62) | — | R95-F | Opzionale | `UC62_1.png` |
| UC63 | Correzione o completamento dei dati di una richiesta in revisione | Gestore | — | R96-F | Opzionale | `UC63.png` |
| UC64 | Approvazione di una richiesta revisionata | Gestore, Applicativo aziendale di destinazione | include UC27 | R97-F | Opzionale | `UC64.png` |
| UC65 | Scarto di una richiesta in revisione | Gestore | — | R98-F | Opzionale | `UC65.png` |
| UC66 | Visualizzazione della dashboard analitica | Utente in sola lettura | include UC66.1, UC66.2 | R99-F | Opzionale | `UC66.png` |
| UC66.1 | &nbsp;&nbsp;Visualizzazione dello stato delle notifiche | (come UC66) | — | R100-F | Opzionale | `UC66_1.png` |
| UC66.2 | &nbsp;&nbsp;Visualizzazione delle azioni eseguite verso gli applicativi | (come UC66) | — | R101-F | Opzionale | `UC66_2.png` |
| UC66.3 | &nbsp;&nbsp;Errore di caricamento della dashboard analitica | (come UC66) | estende UC66 | R102-F | Opzionale | `UC66_3.png` |
| UC67 | Invio al mittente della conferma di ricezione | Mittente, Canale di ingresso, Servizio di posta in uscita | — | R103-F | Opzionale | `UC67.png` |
| UC67.1 | &nbsp;&nbsp;Errore di invio della risposta al mittente | (come UC67) | estende UC67, UC68; include UC37 | R105-F | Opzionale | `UC67_1.png` |
| UC68 | Invio al mittente di un messaggio di errore di ricezione | Mittente, Canale di ingresso, Servizio di posta in uscita | — | R104-F | Opzionale | `UC68.png` |
| UC69 | Acquisizione di registrazioni e trascrizioni di meeting | Mittente, Canale di ingresso | — | R107-F | Opzionale | `UC69.png` |
| UC69.1 | &nbsp;&nbsp;Errore di acquisizione o elaborazione dei meeting | (come UC69) | estende UC69, UC70; include UC37 | R109-F | Opzionale | `UC69_1.png` |
| UC70 | Estrazione di richieste dai meeting | Mittente, LLM | — | R108-F | Opzionale | `UC70.png` |

## Requisiti funzionali senza UC

Non producono casi d'uso perché non descrivono un'interazione ma una proprietà o una regola del sistema:

- **R12-F-O** — separazione rigorosa dei dati dei tenant: è un vincolo trasversale a tutto il sistema, non un flusso.
- **R64-F-O** — esistenza dei tre profili di accesso: è modellata dalla gerarchia degli attori (`Attori.png`).
- **R65-F-O** — limitazione delle funzionalità in base al profilo: è espressa dall'attore associato a ciascun UC e dalla stessa gerarchia.

## Scelte di modellazione da condividere

- **Attore del filtro e della pipeline**: come da sezione Attori, le fasi della pipeline hanno il *Mittente* come attore primario che innesca il flusso; il sistema agisce in autonomia.
- **Gerarchia dei profili**: Amministratore → Gestore → Utente in sola lettura. Ho associato ogni UC al profilo *minimo* che può eseguirlo (es. consultazioni → Utente in sola lettura; regole → Gestore; configurazioni → Amministratore); i profili superiori lo ereditano e nei diagrammi non è ridisegnato.
- **UC condivisi**: UC 34 (marcatura come non riuscita) e UC 37 (log) sono inclusi dagli UC di errore invece di ripetere gli stessi passi in ognuno.
- **Inoltro API REST**: UC 27 è l'UC generale; ordine, ticket, appuntamento, opportunità e documento contabile (UC 28–32) lo specializzano; ritentativo (UC 59) e approvazione da revisione (UC 64) lo includono.
- **Errore di validazione parametri** (UC 44.1): un solo UC che estende tutte le configurazioni (nuovo canale, modifica canale, applicativi, LLM, posta, soglia), perché R75 lo descrive in modo generico.
- **Errore di accesso al canale** (UC 6): un solo UC che estende tutte le acquisizioni (R7 vale per ogni canale).
- **Sotto-UC dei filtri log e del dettaglio richiesta** (R86, R88): scomposti nelle singole voci elencate dal requisito. Se li ritenete eccessivi si possono accorpare nell'UC padre senza toccare il resto.
- **R5 (WhatsApp testo e immagini)** e **R74 (attiva/disattiva canale)** sono ciascuno spezzati in due UC distinti.

## Possibili lacune nei requisiti (da valutare)

- Non c'è un requisito per **visualizzare l'elenco degli utenti**, ma modificare o rimuovere un utente (R67, R68) lo presuppone.
- Non c'è un requisito per l'**accesso negato** quando un utente tenta una funzione non consentita dal suo profilo (R65).
- Per rimozione di canali, regole e utenti non è prevista una **conferma**: l'esempio di riferimento ne ha una (UC 144.1/144.2).
