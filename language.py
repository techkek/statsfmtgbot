languages = {
    "en": {
        "welcome": "Welcome! To get started, use /username command to set your stats.fm username.",
        "username_saved": "Username {} saved. You can now use various commands like /random, /top, etc.",
        "provide_username": "Please provide a username. Usage: /username <your_stats.fm_username>",
        "set_username_first": "Please set your stats.fm username first using the /username command.",
        "generating_song": "Generating a random song...",
        "generating_random_genre": "Generating a random genre...",
        "no_tracks_found": "No tracks found for this username.",
        "no_genres_found": "No genres found for this username.",
        "no_items_found": "No items found for this username.",
        "unable_to_download": "Unable to download the audio file.",
        "language_set": "Language set to English.",
        "invalid_language": "Invalid language code. Available languages are: en, it",
        "help_message": """
Available commands:
/start - Welcome message
/username <username> - Set your stats.fm username
/random - Get a random song from your library
/random_artist - Get a random artist from your library
/random_album - Get a random album from your library
/random_genre - Get a random genre from your library
/top<number><period> - Get your top songs (e.g., /top10m, /top50hy, /top100lt)
/albums<number><period> - Get your top albums (e.g., /albums10m, /albums50hy, /albums100lt)
/artists<number><period> - Get your top artists (e.g., /artists10m, /artists50hy, /artists100lt)
/genres<number><period> - Get your top genres (e.g., /genres10m, /genres50hy, /genres100lt)
  number: 1-250
  period: m (month), hy (6 months), lt (lifetime)
/recommend - Get personalized song and album recommendations
/language <code> - Set language (en, it)
/help - Show this help message

For random and top commands, you'll get additional information such as:
- First and last listen times
- Total listening time
- Number of streams

The recommend command uses a complex algorithm to suggest new songs and albums based on your listening history, focusing on less-known artists that match your taste.
        """,
        "invalid_top_command": "Invalid command. Use /<type><number><period> (e.g., /top10m, /albums50hy, /artists100lt)",
        "generating_top": "Generating top {}...",
        "m": "of the month",
        "hy": "of the last 6 months",
        "lt": "of all time",
        "tracks": "tracks",
        "albums": "albums",
        "artists": "artists",
        "genres": "genres",
        "streams": "streams",
        "generating_random_artist": "Generating a random artist...",
        "generating_random_album": "Generating a random album...",
        "no_artists_found": "No artists found for this username.",
        "no_albums_found": "No albums found for this username.",
        "generating_recommendations": "Generating complex recommendations based on your listening history...",
        "recommended_tracks": "Recommended tracks for you",
        "recommended_albums": "Recommended albums for you",
        "error_recommendations": "An error occurred while getting recommendations. Please try again later.",
    },
    "it": {
        "welcome": "Benvenuto! Per iniziare, usa il comando /username per impostare il tuo nome utente stats.fm.",
        "username_saved": "Nome utente {} salvato. Ora puoi usare vari comandi come /random, /top, ecc.",
        "provide_username": "Per favore fornisci un nome utente. Uso: /username <tuo_nome_utente_stats.fm>",
        "set_username_first": "Per favore imposta prima il tuo nome utente stats.fm usando il comando /username.",
        "generating_song": "Generando una canzone casuale...",
        "generating_random_genre": "Generando un genere casuale...",
        "no_tracks_found": "Nessuna traccia trovata per questo nome utente.",
        "no_genres_found": "Nessun genere trovato per questo nome utente.",
        "no_items_found": "Nessun elemento trovato per questo nome utente.",
        "unable_to_download": "Impossibile scaricare il file audio.",
        "language_set": "Lingua impostata su Italiano.",
        "invalid_language": "Codice lingua non valido. Le lingue disponibili sono: en, it",
        "help_message": """
Comandi disponibili:
/start - Messaggio di benvenuto
/username <nome_utente> - Imposta il tuo nome utente stats.fm
/random - Ottieni una canzone casuale dalla tua libreria
/random_artist - Ottieni un artista casuale dalla tua libreria
/random_album - Ottieni un album casuale dalla tua libreria
/random_genre - Ottieni un genere casuale dalla tua libreria
/top<numero><periodo> - Ottieni le tue canzoni più ascoltate (es. /top10m, /top50hy, /top100lt)
/albums<numero><periodo> - Ottieni i tuoi album più ascoltati (es. /albums10m, /albums50hy, /albums100lt)
/artists<numero><periodo> - Ottieni i tuoi artisti più ascoltati (es. /artists10m, /artists50hy, /artists100lt)
/genres<numero><periodo> - Ottieni i tuoi generi più ascoltati (es. /genres10m, /genres50hy, /genres100lt)
  numero: 1-250
  periodo: m (mese), hy (6 mesi), lt (sempre)
/recommend - Ottieni raccomandazioni personalizzate di canzoni e album
/language <codice> - Imposta la lingua (en, it)
/help - Mostra questo messaggio di aiuto

Per i comandi random e top, riceverai informazioni aggiuntive come:
- Primo e ultimo ascolto
- Tempo totale di ascolto
- Numero di riproduzioni

Il comando recommend utilizza un algoritmo complesso per suggerire nuove canzoni e album basati sulla tua cronologia di ascolto, concentrandosi su artisti meno noti che corrispondono ai tuoi gusti.
        """,
        "invalid_top_command": "Comando non valido. Usa /<tipo><numero><periodo> (es. /top10m, /albums50hy, /artists100lt)",
        "generating_top": "Generazione {} più ascoltati...",
        "m": "del mese",
        "hy": "degli ultimi 6 mesi",
        "lt": "di sempre",
        "tracks": "brani",
        "albums": "album",
        "artists": "artisti",
        "genres": "generi",
        "streams": "ascolti",
        "generating_random_artist": "Generando un artista casuale...",
        "generating_random_album": "Generando un album casuale...",
        "no_artists_found": "Nessun artista trovato per questo nome utente.",
        "no_albums_found": "Nessun album trovato per questo nome utente.",
        "generating_recommendations": "Generazione di raccomandazioni complesse basate sulla tua cronologia di ascolto...",
        "recommended_tracks": "Brani consigliati per te",
        "recommended_albums": "Album consigliati per te",
        "error_recommendations": "Si è verificato un errore durante l'ottenimento delle raccomandazioni. Riprova più tardi.",
    },
}


def get_text(lang, key, format=None):
    if format != None:
        return languages[lang][key].format(format)
    return languages[lang][key]
