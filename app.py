import streamlit as st
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import os

# Configuración de la página
st.set_page_config(page_title="PDF a Audio", page_icon="🎧", layout="centered")

st.title("🎧 Convierte tu PDF a Audio (MP3)")
st.write("Sube tu PDF, elige el idioma y descarga la lectura completa con voz natural.")

# Subida del archivo
archivo_pdf = st.file_uploader("Sube un archivo PDF aquí", type=["pdf"])

# Opciones de usuario
col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma del PDF:", ["Español", "Inglés"])
with col2:
    traducir = st.checkbox("¿Traducir de Inglés a Español antes de leer?")

# Función para generar el audio con la voz de Microsoft
async def generar_audio(texto, voz, archivo_salida):
    comunicador = edge_tts.Communicate(texto, voz)
    await comunicador.save(archivo_salida)

if archivo_pdf is not None:
    if st.button("Generar Audio MP3", type="primary"):
        
        with st.spinner('Extrayendo texto del PDF...'):
            lector = PdfReader(archivo_pdf)
            texto_completo = ""
            for pagina in lector.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_completo += texto_extraido + " "
            
            texto_completo = texto_completo.replace('\n', ' ')

        if not texto_completo.strip():
            st.error("No se pudo extraer texto de este PDF.")
        else:
            # Traducción
            if traducir and idioma_origen == "Inglés":
                with st.spinner('Traduciendo el texto al español...'):
                    fragmentos = [texto_completo[i:i+4999] for i in range(0, len(texto_completo), 4999)]
                    texto_traducido = ""
                    for fragmento in fragmentos:
                        traduccion = GoogleTranslator(source='en', target='es').translate(fragmento)
                        texto_traducido += traduccion + " "
                    
                    texto_final = texto_traducido
                    voz_elegida = 'es-ES-AlvaroNeural' # Voz masculina de España
            else:
                texto_final = texto_completo
                # Si es español usa Álvaro, si es inglés usa Aria (voz femenina USA)
                voz_elegida = 'es-ES-AlvaroNeural' if idioma_origen == "Español" else 'en-US-AriaNeural'

            # Generación de Audio
            with st.spinner('Grabando el MP3 con voz neuronal...'):
                try:
                    archivo_mp3 = "lectura.mp3"
                    
                    # Ejecutar la creación del audio
                    asyncio.run(generar_audio(texto_final, voz_elegida, archivo_mp3))

                    st.success("¡Audio generado con éxito! 🎉")
                    
                    # Botón de descarga
                    with open(archivo_mp3, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar MP3",
                            data=file,
                            file_name="lectura_pdf.mp3",
                            mime="audio/mpeg",
                        )
                except Exception as e:
                    st.error(f"Hubo un error al generar el audio: {e}")
