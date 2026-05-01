// frontend/src/i18n/copy.it.ts
// Source: FND-09, UI-SPEC §7.2 — Phase 1 copy lock (must ship verbatim, ~80 strings)
// Italian-only Sprint 1. Type-safe via `as const` + literal types.
// Refactor to react-i18next deferred to v2 (per RESEARCH Pattern 12).
//
// Tone rules (UI-SPEC §7.1):
//   - No `!` in error or status copy (reserved for celebratory only — Phase 3)
//   - No infantilizing ("Ops!", "Yay!", caps lock — forbidden)
//   - Specific over generic
//   - Verb-first CTAs
//   - Italian conventions: "Lunedì" capital, "kg"/"kcal" lowercase no period

export const copy = {
  // ───── Top app bar (UI-SPEC §7.2) ─────
  appBar: {
    today: 'Oggi',
    history: 'Storico',
    plan: 'Piano',
    settings: 'Impostazioni',
  },

  // ───── Auth (login + logout) ─────
  auth: {
    loginHeading: 'Accedi a Wellness Buddy',
    emailLabel: 'Email',
    emailPlaceholder: 'nome@esempio.it',
    passwordLabel: 'Password',
    submitCta: 'Accedi',
    forgotLink: 'Password dimenticata?',
    invalidCreds: 'Email o password non corretti. Riprova.',
    locked: 'Account momentaneamente non disponibile. Riprova tra qualche minuto.',
    offlineLogin: 'Nessuna connessione. Controlla la rete e riprova.',
    sessionExpired: 'Sessione scaduta dopo 7 giorni di inattività. Accedi di nuovo.',
    logoutConfirm: 'Vuoi davvero uscire?',
    logoutCta: 'Esci',
    logoutCancel: 'Annulla',
    logoutToast: 'Sei uscito.',
  },

  // ───── Invite signup ─────
  invite: {
    heading: 'Crea il tuo account',
    subheading: 'Sei stato invitato a Wellness Buddy.',
    nameLabel: 'Come ti chiami',
    submitCta: 'Crea account',
    tokenExpired: "Questo invito è scaduto. Chiedi all'amministratore un nuovo link.",
    tokenInvalid: "Questo invito non è valido. Chiedi all'amministratore un nuovo link.",
  },

  // ───── /today (greeting + empty states + meal card labels) ─────
  today: {
    greeting: {
      morning: 'Buongiorno, {nome}',
      afternoon: 'Buon pomeriggio, {nome}',
      evening: 'Buonasera, {nome}',
      night: 'Ciao, {nome}',
    },
    emptyNoPlan: {
      heading: 'Nessun piano attivo',
      body: 'Carica il tuo piano nutrizionale per iniziare.',
      cta: 'Carica piano',
    },
    emptyDayBlank: {
      heading: 'Niente registrato oggi',
      body: 'Quando segni i pasti, qui vedi i progressi.',
    },
    mealMarkCta: 'Segna pasto',
    mealCompletedLabel: 'Pasto registrato',
    macroKcal: 'kcal',
    macroProtChip: 'prot',
    macroProtFull: 'proteine',
    macroCarbChip: 'carbo',
    macroCarbFull: 'carboidrati',
    macroFat: 'grassi',
  },

  // ───── Weight quick-log ─────
  weight: {
    heading: 'Pesata di oggi',
    inputLabel: 'Peso (kg)',
    submitCta: 'Salva peso',
    successToast: 'Peso registrato.',
    editToast: 'Peso aggiornato.',
    deleteConfirm: 'Cancellare la pesata di {data}?',
    deleteCta: 'Elimina',
    deleteSuccess: 'Pesata eliminata.',
  },

  // ───── Workout form ─────
  workout: {
    heading: 'Allenamento di oggi',
    toggleLabel: 'Hai allenato oggi?',
    durationLabel: 'Durata (minuti)',
    typeLabel: 'Tipo',
    typePlaceholder: 'es. corsa, yoga, palestra',
    caloriesLabel: 'Calorie bruciate',
    caloriesHelper: 'Opzionale',
    notesLabel: 'Note',
    submitCta: 'Salva allenamento',
    successToast: 'Allenamento registrato.',
    deleteConfirm: "Cancellare l'allenamento del {data}?",
    deleteCta: 'Elimina',
  },

  // ───── Plan upload (FND-09 + Plan 04) ─────
  plans: {
    heading: 'Carica piano nutrizionale',
    dropzoneIdle: 'Trascina qui il file .md o tocca per scegliere',
    dropzoneDragging: 'Rilascia per caricare',
    parsingState: 'Sto leggendo il piano...',
    parseWarningsHeading: 'Sezioni non riconosciute',
    parseWarningsBody:
      'Il piano è stato letto, ma queste sezioni non sono state riconosciute: {list}. Puoi attivarlo comunque o annullare.',
    diffHeading: 'Differenze rispetto al piano attivo',
    diffAddedHeading: 'Aggiunte',
    diffRemovedHeading: 'Rimosse',
    diffChangedHeading: 'Modificate',
    diffEmpty: 'Nessuna differenza rilevata.',
    activateCta: 'Attiva piano',
    cancelCta: 'Annulla',
    activateConfirm:
      'Sostituire il piano attivo con quello caricato? Il piano precedente verrà archiviato.',
    activateSuccess: 'Piano attivato.',
    activateFailed: 'Attivazione non riuscita. Riprova.',
    errorBadFileType: 'Solo file .md sono supportati.',
    errorTooLarge: 'Il file supera il limite di 1 MB.',
    errorParseFailed: 'Non sono riuscito a leggere il piano. Verifica che il formato sia corretto.',
    errorGenericUpload: 'Caricamento non riuscito. Riprova.',
    listHeading: 'Piani caricati',
    listEmpty: 'Non hai ancora caricato nessun piano.',
    listActiveBadge: 'attivo',
    nameLabel: 'Nome del piano',
    namePlaceholder: 'es. Piano gennaio 2026',
    previewHeading: 'Anteprima del piano',
  },

  // ───── Settings ─────
  settings: {
    themeHeading: 'Tema',
    themeLight: 'Chiaro',
    themeDark: 'Scuro',
    themeSystem: 'Sistema',
    profileHeading: 'Profilo',
    languageHeading: 'Lingua',
    languageValue: 'Italiano',
    languageNote: 'Solo italiano in questa versione.',
    logoutCta: 'Esci',
  },

  // ───── PWA install (iOS) + update toast ─────
  pwa: {
    installHeading: 'Installa Wellness Buddy',
    installBody: 'Aggiungilo alla schermata Home per usarlo come app.',
    installCta: 'Mostra come fare',
    installStep1: 'Tocca il pulsante Condividi nella barra di Safari.',
    installStep2: 'Scorri e tocca "Aggiungi a Home".',
    installStep3: 'Conferma toccando "Aggiungi".',
    installDismiss: 'Più tardi',
    updateHeading: 'Nuova versione disponibile',
    updateBody: 'Ricarica per aggiornare.',
    updateAction: 'Ricarica',
    updateDismiss: 'Più tardi',
    persistDeniedHeading: 'Storage offline non abilitato',
    persistDeniedBody:
      "I tuoi dati potrebbero essere cancellati dopo 7 giorni di inattività. Apri l'app regolarmente.",
  },

  // ───── AI placeholder (Phase 1 widget on /today) ─────
  ai: {
    placeholderHeading: 'AI in arrivo',
    placeholderBody:
      "L'assistente AI sarà disponibile presto. Puoi usare l'app senza problemi anche ora.",
  },

  // ───── Sync status indicator (UI-SPEC §10.5) ─────
  sync: {
    synced: 'Sincronizzato',
    pending: 'In sincronizzazione',
    error: 'Sincronizzazione non riuscita',
    offline: 'Offline',
    tooltip: 'Ultima sincronizzazione: {time}',
    offlineToast: 'Nessuna connessione. Le modifiche verranno inviate quando torni online.',
  },

  // ───── Generic errors (D-20: API errors → italian via copy.it.ts code lookup) ─────
  errors: {
    forbidden: 'Non hai accesso a questa sezione.',
    notFound: 'Pagina non trovata.',
    generic500: 'Qualcosa non ha funzionato. Riprova tra poco.',
    networkOffline: 'Nessuna connessione. Le modifiche verranno inviate quando torni online.',
    boundaryHeading: 'Qualcosa non ha funzionato',
    boundaryBody: 'Ricarica la pagina o torna a Oggi.',
    boundaryReloadCta: 'Ricarica',
    boundaryHomeCta: 'Torna a Oggi',
    conflict: 'Modificato da un altro utente',
    conflictHint: "Ricarica per vedere l'ultima versione.",
    syncFailed: 'Sincronizzazione non riuscita. Riprova più tardi.',
  },

  // ───── App boot (loading splash + Dexie wipe resync) ─────
  appBoot: {
    loadingSplash: 'Wellness Buddy',
    resyncMessage: 'Sto ricaricando i tuoi dati...',
  },
} as const;

export type Copy = typeof copy;
