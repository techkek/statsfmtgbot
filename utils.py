def send_long_message(bot, chat_id, text, parse_mode=None):
    max_message_length = 4096
    start = 0
    
    while start < len(text):
        end = start + max_message_length

        if end < len(text):
            end = text.rfind('\n', start, end)
            if end == -1:
                end = start + max_message_length
        try:
            bot.send_message(chat_id, text[start:end], parse_mode=parse_mode)
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {e}")
            cleaned_text = text[start:end].replace('_', '').replace('*', '').replace('`', '').replace('[', '').replace(']', '')
            bot.send_message(chat_id, cleaned_text)

        start = end
        
        if start < len(text) and text[start] == '\n':
            start += 1
