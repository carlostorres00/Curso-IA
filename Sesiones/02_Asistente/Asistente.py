#Versión definitiva con separación de ficheros
from gemini_client import preguntar_a_gemini

historial = []

while True:
    pregunta = input('¿Que le quieres preguntar a Gemini?')

    if pregunta == '/salir':
        break

    if pregunta == "/ayuda":
        print("""
        Comandos disponibles:
        
        /ayuda     Muestra esta ayuda
        /historial Muestra la conversación
        /limpiar   Borra el historial
        /guardar   Guarda la conversación
        /salir     Cierra el programa
        """)
        continue

    if pregunta == "/historial":
        for mensaje in historial:
            print(mensaje)
        continue

    if pregunta == "/limpiar":
        historial = []
        print("Historial borrado.")
        continue

    if pregunta == "/guardar":
        with open("historial.txt", "w", encoding="utf-8") as archivo:
            for mensaje in historial:
                archivo.write(mensaje +"\n")
        print("Conversación guardada")
        continue

    if pregunta == "/cargar":
        try:
            with open("historial.txt", "r", encoding="utf-8") as archivo:
                historial = []

                for linea in archivo:
                    historial.append(linea.strip())

            print("Conversación cargada.")

        except FileNotFoundError:
            print("No existe ningún historial guardado.")

        continue




    historial.append(f"Usuario: {pregunta}")
    try:
        respuesta = preguntar_a_gemini(historial)
        print(respuesta)
        historial.append(f"Gemini: {respuesta}")

    except Exception as error:
        print(f"Error: {error}")



