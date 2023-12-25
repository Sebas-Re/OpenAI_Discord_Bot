# OpenAI_Discord_Bot
 Bot de Discord que conecta con OpenAI

 Caracteristicas actuales:
 - Funcion de lectura de chat (responder o no a todos los mensajes enviados en los canales especificados).
 - Responde a mensajes de texto enviados en el canal seleccionado utilizando chatGPT-3.5-turbo, si la lectura de chat está habilitada y el canal está añadido a la lista de canales en los que puede leer y responder
 - Transcribe los mensajes de voz enviados en los canales especificados, utilizando el modelo Whisper de OpenAI.

 Comandos:
 - ping     > Probar si el bot está en línea y responde con "Pong!" y la latencia del bot.
 - leerchat > Habilitar o deshabilitar la función de lectura de chat en todos los canales
 - consulta > Enviar una solicitud a la API de GPT-3 de OpenAI y generar una respuesta (útil si la lectura de chat está deshabilitada).
 - imagine  > Generar una imagen basada en una solicitud utilizando el modelo DALL-E de OpenAI.
 - canal #NombreCanal Añadir/Eliminar > Añade o remueve el canal especificado de la lista de canales en los que el bot puede leer y responder
