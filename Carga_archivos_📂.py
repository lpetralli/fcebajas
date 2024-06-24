import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st

# Configuración de la página para usar el modo ancho
st.set_page_config(layout="wide")

st.image("logo_empresariales_color.png")


st.header("Control Bajas🚨")
st.divider()

col1, col2 = st.columns(2)

with col1:
   st.subheader("Subir asistencia")
   asistencia1y2 = st.file_uploader("ASISTENCIAS 1Q24 1ER Y 2DO AÑO", type=['csv', 'xlsx'])

   asistencia3y4 = st.file_uploader("ASISTENCIAS 1Q24 3ER Y 4TO AÑO", type=['csv', 'xlsx'])

with col2:
   st.subheader("Subir notas")
   #st.session_state['periodo'] = st.selectbox("Notas de", ["1P", "2P", "Finales"])
   notas1y2 = st.file_uploader("NOTAS 1Q24 1ER Y 2DO AÑO", type=['csv', 'xlsx'])
   notas3y4 = st.file_uploader("NOTAS 1Q24 3ER Y 4TO AÑO   ", type=['csv', 'xlsx'])



if asistencia1y2 is not None and asistencia3y4 is not None and notas1y2 is not None and notas3y4 is not None:

    #Asistencia-------------------------------------------------

    asistencia1y2 = pd.read_excel(asistencia1y2, skiprows = 1)
    asistencia1y2.drop(asistencia1y2.columns[1:4], axis=1, inplace=True)
    for column in asistencia1y2.columns[1:]:
        asistencia1y2[column] = pd.to_numeric(asistencia1y2[column], errors='coerce').fillna(0).round(2)

    # Sumar el total de inasistencias, asumiendo que las materias comienzan de la segunda columna en adelante
    asistencia1y2['Total de Inasistencias'] = asistencia1y2.iloc[:, 1:].sum(axis=1)

    # Función para clasificar las materias en los rangos de inasistencias
    def clasificar_materias(row):
        materias_menor_a_15 = []
        materias_entre_15_y_25 = []
        materias_mas_de_25 = []
        for materia in row.index[1:-1]:  # Excluye la primera y la ltima columna añadida
            inasistencias = row[materia]
            if pd.notna(inasistencias):
                materia_con_inasistencias = f"{materia} ({inasistencias})"
                if inasistencias > 0 and inasistencias < 15:
                    materias_menor_a_15.append(materia_con_inasistencias)
                elif 15 <= inasistencias < 25:
                    materias_entre_15_y_25.append(materia_con_inasistencias)
                elif inasistencias >= 25:
                    materias_mas_de_25.append(materia_con_inasistencias)
        row['Materias <15'] = ', '.join(materias_menor_a_15)
        row['Materias 15-25'] = ', '.join(materias_entre_15_y_25)
        row['Materias >25'] = ', '.join(materias_mas_de_25)
        return row


    asistencia3y4 = pd.read_excel(asistencia3y4, skiprows = 1)
    asistencia3y4.drop(asistencia3y4.columns[1:4], axis=1, inplace=True)
    for column in asistencia3y4.columns[1:]:
        asistencia3y4[column] = pd.to_numeric(asistencia3y4[column], errors='coerce').fillna(0).round(2)

    # Sumar el total de inasistencias, asumiendo que las materias comienzan de la segunda columna en adelante
    asistencia3y4['Total de Inasistencias'] = asistencia3y4.iloc[:, 1:].sum(axis=1)


    asistencia1y2 = asistencia1y2.apply(clasificar_materias, axis=1)
    asistencia3y4 = asistencia3y4.apply(clasificar_materias, axis=1)


    # if 'asistencia_data1y2' not in st.session_state:
    #     st.session_state['asistencia_data1y2'] = asistencia1y2

    # if 'asistencia_data3y4' not in st.session_state:
    #     st.session_state['asistencia_data3y4'] = asistencia3y4

    # with st.expander("Asistencia 1Q24 1ER Y 2DO AÑO"):
    #     st.dataframe(st.session_state['asistencia_data1y2'], hide_index=True)

    # with st.expander("Asistencia 1Q24 3ER Y 4TO AÑO"):
    #     st.dataframe(st.session_state['asistencia_data3y4'], hide_index=True)


    # Combine the dataframes asistencia_data1y2 and asistencia_data3y4
    combined_asistencia = pd.concat([asistencia1y2, asistencia3y4])

    # Select only the specified columns
    selected_columns = ['Apellido y Nombres', 'Total de Inasistencias', 'Materias <15', 'Materias 15-25', 'Materias >25']
    combined_asistencia = combined_asistencia[selected_columns]

    # Store the combined dataframe in the session state
    st.session_state['combined_asistencia'] = combined_asistencia

    # Display the combined dataframe in an expander
    with st.expander("Asistencia"):
        st.dataframe(st.session_state['combined_asistencia'], hide_index=True)

    #Notas----------------------



    # Aquí puedes añadir el código para manejar el archivo de notas
    # st.success("Archivo de notas cargado con éxito.")
    notas1y2 = pd.read_excel(notas1y2, header=1)
    notas3y4 = pd.read_excel(notas3y4, header=1)

    def identificar_desaprobados(df):
        df.replace(['-'], 0, inplace=True)
        df.replace(['Ausente'], -1, inplace=True)
        df.replace(r'\s+\(\D+\)', '', regex=True, inplace=True)
        df.iloc[:, 4:] = df.iloc[:, 4:].apply(pd.to_numeric, errors='coerce')
        df['Exámenes Desaprobados'] = df.iloc[:, 4:].apply(lambda row: [col for col, val in row.items() if pd.notna(val) and val != 0 and val < 4], axis=1)
        return df
    
    notas1y2 = identificar_desaprobados(notas1y2)
    notas3y4 = identificar_desaprobados(notas3y4)

    notas = pd.concat([notas1y2.iloc[:, :4], notas3y4.iloc[:, :4]], axis=0)
    notas['Exámenes Desaprobados'] = pd.concat([notas1y2['Exámenes Desaprobados'], notas3y4['Exámenes Desaprobados']], axis=0).values
    notas = notas[['Apellido y Nombres', 'Exámenes Desaprobados']]
    # Remove rows where 'Apellido y Nombres' is empty or null
    notas = notas[notas['Apellido y Nombres'].notna() & (notas['Apellido y Nombres'] != '')]

    # Store the combined dataframe in the session state
    st.session_state['notas'] = notas

    # Display the combined dataframe in an expander
    with st.expander("Notas"):
        st.dataframe(st.session_state['notas'], hide_index=True)


    with st.expander("Revisión de coincidencia de alumnos"):
        # Check for students present in 'notas' but not in 'combined_asistencia'
        if len(notas) != len(combined_asistencia):
            st.write("alumnos en notas: ", len(notas))
            st.write("alumnos en asistencia: ", len(combined_asistencia))
            st.warning("La cantidad de alumnos no coincide entre las tablas")
            missing_in_notas = combined_asistencia[~combined_asistencia['Apellido y Nombres'].isin(notas['Apellido y Nombres'])]
            missing_in_asistencia = notas[~notas['Apellido y Nombres'].isin(combined_asistencia['Apellido y Nombres'])]
            if not missing_in_notas.empty:
                st.error("Alumnos faltantes en notas:")
                st.dataframe(missing_in_notas[['Apellido y Nombres']], hide_index=True)
            if not missing_in_asistencia.empty:
                st.error("Alumnos faltantes en asistencia:")
                st.dataframe(missing_in_asistencia[['Apellido y Nombres']], hide_index=True)
        else:
            st.info("Cantidad de alumnos coinciden en ambas tablas")

    # Merge 'combined_asistencia' with 'notas' on 'Apellido y Nombres', ensuring no duplicates and keeping all columns from 'combined_asistencia' plus 'Exámenes Desaprobados' from 'notas'
    full_data = pd.merge(combined_asistencia, notas[['Apellido y Nombres', 'Exámenes Desaprobados']], on='Apellido y Nombres', how='left')
    #full_data['Exámenes Desaprobados'].fillna('no hay información de notas', inplace=True)
    
    # Display the merged dataframe in an expander
    with st.expander("Vista completa de alumnos"):
        st.dataframe(full_data, hide_index=True)
        st.write("Total alumnos: ", len(full_data))

        # Función para convertir el DataFrame a un archivo Excel
    def to_excel(df):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data
    from datetime import datetime

    # Botón de descarga
    st.download_button(
        label="Descargar Datos",
        data=to_excel(full_data),
        file_name=f'datos_alumnos_fce_{datetime.today().strftime("%Y-%m-%d")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)