import os
import glob
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar logging
log_path = os.path.expanduser("~/Downloads/screenshot_cleanup.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def enviar_correo(contenido, total_kb):
    # Configura estos valores con tus datos de correo
    remitente = "diego.vinalslage@gmail.com"
    destinatario = "diego.vinalslage@gmail.com"
    password = "estt bjqu mlqy njbn"  # Para Gmail, usa una contraseña de aplicación
    
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = f"Reporte de limpieza de screenshots - {datetime.now().strftime('%Y-%m-%d')}"
    
    cuerpo = f"""
📸 Reporte de Limpieza de Screenshots
════════════════════════════════════════════════════════════

🗑️ Espacio Total Liberado: {total_kb:.2f} KB

📋 Detalle de Operaciones:
────────────────────────────────────────────────────────────
{contenido}

✨ Reporte generado el {datetime.now().strftime('%d/%m/%Y')} a las {datetime.now().strftime('%H:%M:%S')}"""
    
    mensaje.attach(MIMEText(cuerpo, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.send_message(mensaje)
        logging.info("Correo enviado exitosamente")
    except Exception as e:
        logging.error(f"Error al enviar correo: {e}")

def limpiar_screenshots():
    downloads_path = os.path.expanduser("~/Downloads")
    files_to_delete = glob.glob(os.path.join(downloads_path, "Captura de pantalla*"))
    
    total_archivos = len(files_to_delete)
    archivos_borrados = 0
    total_kb = 0
    log_contenido = []

    logging.info(f"Iniciando limpieza. Encontrados {total_archivos} screenshots")
    
    for file in files_to_delete:
        try:
            tamano = os.path.getsize(file) / 1024
            total_kb += tamano
            os.remove(file)
            archivos_borrados += 1
            mensaje = f"    • {os.path.basename(file)} ({tamano:.2f} KB)"
            logging.info(mensaje)
            log_contenido.append(mensaje)
        except Exception as e:
            mensaje = f"    ❌ Error al borrar {file}: {e}"
            logging.error(mensaje)
            log_contenido.append(mensaje)
    
    resumen = f"\n✅ Proceso completado: {archivos_borrados} de {total_archivos} archivos borrados"
    logging.info(resumen)
    log_contenido.append(resumen)
    
    # Enviar el log por correo
    enviar_correo("\n".join(log_contenido), total_kb)

if __name__ == "__main__":
    limpiar_screenshots()
