import pandas as pd # type: ignore
from icalendar import Calendar, Event # type: ignore
from datetime import datetime, timedelta
import pytz # type: ignore
from datetime import datetime, timedelta, time
import re

def procesar_calendario(file_path):
    # Cargar el archivo de Excel
    df = pd.read_excel(file_path, sheet_name='Calendario Apertura 2024-25', header=None)
    

    # Lista para almacenar los partidos
    partidos = []

    current_division = None
    current_jornada = None
    current_campo = None
    jornada_fechas = None
    current_dia = None  # Añadimos esta variable para rastrear el día actual

    def extract_dates(text):
        match = re.search(r'\((\d{1,2})-(\d{1,2})\s+(\w+)\)', text)
        if match:
            day1, day2, month = match.groups()
            return f"{day1} {month}", f"{day2} {month}"
        return None, None

    #print("\nComenzando a procesar las filas...")

    # Iterar sobre las filas para extraer la información de los partidos
    for index, row in df.iterrows():
        #print(f"\nProcesando fila {index}:")
        #print(f"Contenido de la fila: {row.tolist()}")
        
        # Detectar cambio de división y jornada
        if pd.notna(row[1]) and "DIVISIÓN" in str(row[1]):
            current_division = row[1]
            #print(f"Nueva división detectada: {current_division}")
            
            # Extraer información de la jornada y fechas
            if pd.notna(row[3]) and "JORNADA" in str(row[3]):
                current_jornada = row[3]
                fecha1, fecha2 = extract_dates(row[3])
                if fecha1 and fecha2:
                    jornada_fechas = {
                        'SÁBADO': fecha1,
                        'DOMINGO': fecha2
                    }
                    #print(f"Nueva jornada detectada: {current_jornada}, Fechas: {jornada_fechas}")
                else:
                    #rint(f"No se pudieron extraer las fechas de: {row[3]}")
                    pass
            continue
        
        # Detectar cambio de campo
        if pd.notna(row[3]) and "CAMPO" in str(row[3]):
            current_campo = row[3]
            #print(f"Nuevo campo detectado: {current_campo}")
            continue
        
        # Actualizar el día si se encuentra uno nuevo
        if pd.notna(row[1]) and row[1] in ['SÁBADO', 'DOMINGO']:
            current_dia = row[1]
            #print(f"Nuevo día detectado: {current_dia}")
        
        # Procesar partidos
        if pd.notna(row[2]):
            #print(f"Posible partido detectado. Hora: {row[2]}, Tipo: {type(row[2])}")
            
            if isinstance(row[2], time):
                hora = row[2].strftime('%H:%M')
            else:
                #print(f"Tipo de hora no reconocido: {type(row[2])}")
                continue
            
            if hora and current_dia and jornada_fechas:
                partido = {
                    'División': current_division,
                    'Jornada': current_jornada,
                    'Campo': current_campo,
                    'Fecha': jornada_fechas[current_dia],
                    'Día': current_dia,
                    'Hora': hora,
                    'Equipo Local': row[3],
                    'Equipo Visitante': row[4]
                }
                partidos.append(partido)
                print(f"Partido agregado: {partido['Equipo Local']} vs {partido['Equipo Visitante']} - {partido['Fecha']} {partido['Hora']}")
            else:
                print(f"No se pudo procesar el partido. Día: {current_dia}, Fechas: {jornada_fechas}, Hora: {hora}")
        else:
            #print("No se detectó un partido en esta fila")
            pass

    print(f"\nTotal de partidos encontrados: {len(partidos)}")

    if len(partidos) > 0:
        # Convertir la lista de partidos a un DataFrame
        partidos_df = pd.DataFrame(partidos)
        # Crear máscaras para los diferentes casos
        mask_20_21 = partidos_df['Hora'].isin(['20:00', '21:00'])
        mask_other = ~mask_20_21
        
        # Función para ajustar la fecha
        def adjust_date(date_str, adjustment):
            parts = date_str.split()
            day = int(parts[0]) + adjustment
            return f"{day} {' '.join(parts[1:])}"
        
        # Aplicar ajustes
        partidos_df.loc[mask_20_21, 'Día'] = 'LUNES'
        partidos_df.loc[mask_other, 'Fecha'] = partidos_df.loc[mask_other, 'Fecha'].apply(lambda x: adjust_date(x, -1))


        # Limpiar el campo 'Jornada' eliminando los paréntesis y su contenido
        partidos_df['Jornada'] = partidos_df['Jornada'].str.replace(r'\s*\(.*\)', '', regex=True)

        
        return partidos_df
    else:
        print("No se encontraron partidos. Revisa el formato del archivo Excel.")
        return None


def pasar_a_ical(partidos_df, nombre_archivo):
    if partidos_df is not None:
        # Crear un calendario
        cal = Calendar()

        # Configurar la zona horaria de Madrid
        madrid_tz = pytz.timezone('Europe/Madrid')

        # Diccionario para traducir nombres de meses (incluyendo versiones en minúsculas)
        meses_es_en = {
            'Enero': 'January', 'enero': 'January',
            'Febrero': 'February', 'febrero': 'February',
            'Marzo': 'March', 'marzo': 'March',
            'Abril': 'April', 'abril': 'April',
            'Mayo': 'May', 'mayo': 'May',
            'Junio': 'June', 'junio': 'June',
            'Julio': 'July', 'julio': 'July',
            'Agosto': 'August', 'agosto': 'August',
            'Septiembre': 'September', 'septiembre': 'September',
            'Octubre': 'October', 'octubre': 'October',
            'Noviembre': 'November', 'noviembre': 'November',
            'Diciembre': 'December', 'diciembre': 'December'
        }

        for _, partido in partidos_df.iterrows():
            event = Event()
            #print(f"\nProcesando partido para Calendario\n{partido}")
            
            event.add('summary', f"{partido['Equipo Local']} - {partido['Equipo Visitante']}")
            #print(f"Evento creado con summary: {event['summary']}")
            
            fecha_str = partido['Fecha']
            hora_str = partido['Hora']
            #print(f"Fecha original: {fecha_str}, Hora: {hora_str}")
            
            # Separar el día y el mes
            dia, mes = fecha_str.split()
            # Traducir el mes al inglés
            mes_en = meses_es_en[mes]
            # Formatear la fecha y hora
            fecha_hora_str = f"{dia} {mes_en} {datetime.now().year} {hora_str}"
            #print(f"Fecha y hora formateada: {fecha_hora_str}")
            
            fecha_hora = datetime.strptime(fecha_hora_str, "%d %B %Y %H:%M")
            #print(f"Fecha y hora parseada: {fecha_hora}")
            fecha_hora = madrid_tz.localize(fecha_hora)
            #print(f"Fecha y hora localizada: {fecha_hora}")
            
            event.add('dtstart', fecha_hora)
            event.add('dtend', fecha_hora + timedelta(hours=1))
            
            event.add('location', partido['Campo'])
            event.add('description', f"{partido['Jornada']}")
        
            
            cal.add_component(event)

        with open(nombre_archivo, 'wb') as f:
            f.write(cal.to_ical())
        
        print(f"Archivo de calendario '{nombre_archivo}' creado exitosamente.")
    else:
        print("No se pudo crear el archivo de calendario debido a un error en el procesamiento de los datos.")

def main():
    file_path = './Calendario Apertura LAA_2024_25.xlsx'
    partidos_df = procesar_calendario(file_path)
    pasar_a_ical(partidos_df, 'LigaRetamarAA.ics')
    if partidos_df is not None:
        # Get unique team names from both 'Equipo Local' and 'Equipo Visitante' columns
        equipos = set(partidos_df['Equipo Local'].unique()) | set(partidos_df['Equipo Visitante'].unique())
        equipos = ['DESCANSA' if pd.isna(equipo) or equipo == 'nan' else equipo for equipo in equipos]
        
        for equipo in equipos:
            #print(f"\nProcesando calendario para: {equipo}")
            # Filter matches for the current team
            partidos_equipo = partidos_df[
                (partidos_df['Equipo Local'] == equipo) | (partidos_df['Equipo Visitante'] == equipo)
            ]
            
            # Create a sanitized filename
            nombre_archivo = f"Equipos/calendario_{equipo.lower().replace(' ', '_')}.ics"
            
            # Pass the filtered DataFrame to pasar_a_ical with the team name
            pasar_a_ical(partidos_equipo, nombre_archivo)
            
        print("\nCalendarios individuales creados para todos los equipos.")
    else:
        print("No se pudieron crear los calendarios debido a un error en el procesamiento de los datos.")
    # Obtener las divisiones únicas del DataFrame
    divisiones = partidos_df['División'].unique()
    
    for division in divisiones:
        #print(f"\nProcesando calendario para la división: {division}")
        # Filtrar los partidos para la división actual
        partidos_division = partidos_df[partidos_df['División'] == division]
        
        # Crear un nombre de archivo sanitizado
        nombre_archivo = f"Divisiones/calendario_{division.replace(' ', '_')}.ics"
        
        # Pasar el DataFrame filtrado a pasar_a_ical con el nombre de la división
        pasar_a_ical(partidos_division, nombre_archivo)
        
    print("\nCalendarios por división creados para todas las divisiones.")
    #print(partidos_df.to_string(index=False))
    #pasar_a_ical(partidos_df)

    
    
    
    

if __name__ == "__main__":
    main()
