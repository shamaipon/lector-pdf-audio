import streamlit as st
from PyPDF2 import PdfReader
from gtts import gTTS
from deep_translator import GoogleTranslator
import io
import time

# Configuración de la página
st.set_page_config(page_title="PDF a Audio", page_icon="🎧", layout="centered")

st.title("🎧 Convierte tu PDF a Audio (MP3)")
st.write("Sube tu PDF, elige el idioma y descarga la lectura completa en audio.")

# 1. Subida del archivo
archivo_pdf = st.file_uploader("Sube un archivo PDF aquí", type=["pdf"])

# Opciones de usuario
col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma del PDF:", ["Español", "Inglés"])
with col2:
    traducir = st.checkbox("¿Traducir de Inglés a Español antes de leer?")

if archivo_pdf is not None:
    if st.button("Generar Audio MP3", type="primary"):
        
        # Usamos st.spinner para que el usuario sepa que la app está trabajando
        with st.spinner('Extrayendo texto del PDF... Esto puede tardar unos segundos.'):
            # Leer el PDF
            lector = PdfReader(archivo_pdf)
            texto_completo = ""
            for pagina in lector.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_completo += texto_extraido + " "
            
            # Limpiar un poco el texto (quitar saltos de línea excesivos)
            texto_completo = texto_completo.replace('\n', ' ')

        if not texto_completo.strip():
            st.error("No se pudo extraer texto de este PDF. Asegúrate de que no sea una imagen escaneada.")
        else:
            # Lógica de traducción
            if traducir and idioma_origen == "Inglés":
                with st.spinner('Traduciendo el texto al español... (Esto tomará un tiempo para 15-30 páginas)'):
                    # Dividimos en fragmentos porque el traductor tiene límites de caracteres por petición
                    fragmentos = [texto_completo[i:i+4999] for i in range(0, len(texto_completo), 4999)]
                    texto_traducido = ""
                    for fragmento in fragmentos:
                        traduccion = GoogleTranslator(source='en', target='es').translate(fragmento)
                        texto_traducido += traduccion + " "
                        time.sleep(2)
                    
                    texto_final = texto_traducido
                    idioma_voz = 'es'
            else:
                texto_final = texto_completo
                idioma_voz = 'es' if idioma_origen == "Español" else 'en'

            # Generación del Audio
            with st.spinner('Generando el archivo MP3...'):
                try:
                    # Crear el objeto gTTS
                    tts = gTTS(text=texto_final, lang=idioma_voz, slow=False)
                    
                    # Guardar el audio en memoria (buffer) para no tener que crear archivos locales
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)

                    st.success("¡Audio generado con éxito! 🎉")
                    
                    # 2. Botón de descarga brutalmente sencillo
                    st.download_button(
                        label="⬇️ Descargar MP3",
                        data=audio_buffer,
                        file_name="lectura_pdf.mp3",
                        mime="audio/mpeg",
                    )
                except Exception as e:
                    st.error(f"Hubo un error al generar el audio: {e}")
