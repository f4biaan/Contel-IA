import streamlit as st
from openai import OpenAI
import urllib.parse
from mistralai import Mistral

st.set_page_config(
    page_title="ContelIA",
    page_icon="🧠",
    layout="wide"
)

def conectar_api(proveedor):
    try:
        if proveedor == "DeepSeek":
            cliente = OpenAI(
                api_key=st.session_state.get('deepseek_api_key', ''),
                base_url="https://api.deepseek.com"
            )
        elif proveedor == "Mistral":
            cliente = Mistral(
                api_key=st.session_state.get('mistral_api_key', ''),
                model="mistral-large-latest"
            )
        return cliente
    except Exception as e:
        st.error(f"Error al conectar con {proveedor}: {str(e)}")
        return None

def generar_texto(prompt, proveedor, tipo_contenido):
    cliente = conectar_api(proveedor)
    if not cliente:
        return "Error de conexión con la API"
    
    system_prompts = {
        "Post para Twitter/X": "Eres un experto en marketing digital especializado en crear tweets virales. Genera contenido conciso y atractivo en 280 caracteres o menos.",
        "Post para Facebook": "Eres un experto en marketing de redes sociales especializado en Facebook. Crea contenido atractivo con el tono y formato adecuados para esta plataforma.",
        "Post para Instagram": "Eres un experto en marketing visual para Instagram. Crea contenido atractivo con hashtags relevantes y llamadas a la acción.",
        "Guión para TikTok": "Eres un creador de contenido para TikTok. Genera un guión breve y entretenido que capture la atención en los primeros segundos.",
        "Artículo de blog": "Eres un redactor profesional de blogs. Genera un artículo bien estructurado con introducción, desarrollo y conclusión sobre el tema solicitado.",
        "Email marketing": "Eres un experto en email marketing. Genera un correo persuasivo con asunto atractivo, introducción, beneficios y llamada a la acción clara."
    }
    
    system_content = system_prompts.get(tipo_contenido, "Eres un asistente útil y creativo.")
    
    try:
        respuesta = cliente.chat.completions.create(
            model="deepseek-chat" if proveedor == "DeepSeek" else "mistral-large" if proveedor == "Mistral" else "claude-3-opus-20240229",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al generar texto: {str(e)}"

def generar_codigo(descripcion, proveedor, lenguaje):
    cliente = conectar_api(proveedor)
    if not cliente:
        return "Error de conexión con la API"
    
    prompt = f"""Genera código en {lenguaje} para la siguiente tarea: {descripcion} Proporciona código bien comentado y explicado, siguiendo las mejores prácticas de programación."""
    
    try:
        respuesta = cliente.chat.completions.create(
            model="deepseek-coder" if proveedor == "DeepSeek" else "mistral-large" if proveedor == "Mistral" else "claude-3-opus-20240229",
            messages=[
                {"role": "system", "content": f"Eres un experto programador de {lenguaje}. Proporciona soluciones de código eficientes, bien comentadas y siguiendo las mejores prácticas."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al generar código: {str(e)}"

def guardar_en_historial(tipo, prompt, resultado):
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    
    st.session_state.historial.append({
        "tipo": tipo,
        "prompt": prompt,
        "resultado": resultado,
    })

def mostrar_historial():
    if 'historial' not in st.session_state or not st.session_state.historial:
        st.info("No hay historial disponible")
        return
    
    for i, item in enumerate(st.session_state.historial):
        with st.expander(f"{item['tipo']}"):
            st.write("**Prompt:**")
            st.write(item['prompt'])
            st.write("**Resultado:**")
            st.write(item['resultado'])
            if st.button(f"Eliminar", key=f"del_{i}"):
                st.session_state.historial.pop(i)
                st.rerun()

def main():
    with st.sidebar:
        st.title("Configuración")
        
        st.subheader("Claves de API")
        
        if 'deepseek_api_key' not in st.session_state:
            st.session_state.deepseek_api_key = ""
        if 'mistral_api_key' not in st.session_state:
            st.session_state.mistral_api_key = ""
        
        deepseek_key = st.text_input("DeepSeek API Key", value=st.session_state.deepseek_api_key, type="password")
        mistral_key = st.text_input("Mistral API Key", value=st.session_state.mistral_api_key, type="password")
        
        if st.button("Guardar Claves"):
            st.session_state.deepseek_api_key = deepseek_key
            st.session_state.mistral_api_key = mistral_key
            st.success("Claves guardadas con éxito")
        
        st.subheader("Navegación")
        pagina = st.radio("Ir a:", ["Generador de Contenido", "Generador de Código", "Historial"])
        
        st.divider()
        st.info("ContelIA es un asistente para generar diferentes tipos de contenido utilizando LLMs mediante sus APIs.")
    
    st.title("ContelIA 🧠")
    
    if pagina == "Generador de Contenido":
        generar_contenido_ui()
    elif pagina == "Generador de Código":
        generar_codigo_ui()
    else:
        st.header("Historial de Generaciones")
        mostrar_historial()

def generar_contenido_ui():
    st.header("Generador de Contenido")
    
    tab1, tab2 = st.tabs(["Generación Directa", "Generación de Ideas"])
    
    with tab1:
        st.subheader("Generación Directa de Contenido")
        
        col1, col2 = st.columns(2)
        
        with col1:
            proveedor = st.selectbox(
                "Selecciona el proveedor de IA:",
                ["DeepSeek", "Mistral"],
                key="proveedor_forma1"
            )
        
        with col2:
            tipo_contenido = st.selectbox(
                "Tipo de contenido:",
                [
                    "Selecciona el tipo de contenido que deseas crear",
                    "Post para Twitter/X", 
                    "Post para Facebook", 
                    "Post para Instagram",
                    "Guión para TikTok",
                    "Guión para Reels",
                    "Artículo de blog", 
                    "Email marketing",
                    "Infografía",
                    "Newsletter",
                    "Podcast script"
                ],
                key="tipo_contenido_forma1"
            )
        
        tipo_respuesta = st.selectbox(
            "¿Qué tipo de respuesta necesitas?",
            [
                "Selecciona el tipo de respuesta que deseas",
                "Ejemplo concreto",
                "Recomendaciones",
                "Ideas creativas",
                "Estructura para video/post",
                "Análisis de tendencias",
                "Fórmulas probadas",
                "Call to Action (CTA)"
            ],
            key="tipo_respuesta"
        )
        
        st.subheader("Tu Prompt")
        prompt_ayuda = {
            "Post para Twitter/X": "Describe el tema y tono del tweet. Ej: 'Un tweet promocionando un nuevo curso de programación con tono entusiasta'",
            "Post para Facebook": "Describe el contenido y objetivo. Ej: 'Post anunciando una oferta especial de fin de semana para nuestra tienda de ropa'",
            "Post para Instagram": "Describe la imagen y el mensaje. Ej: 'Post sobre consejos de fitness con una imagen motivadora'",
            "Guión para TikTok": "Describe el tema y estilo. Ej: 'Un TikTok educativo de 30 segundos explicando cómo funciona la inteligencia artificial'",
            "Guión para Reels": "Describe el tema y enfoque. Ej: 'Un Reel mostrando 3 tips de productividad con un tono energético'",
            "Artículo de blog": "Describe el tema y enfoque. Ej: 'Artículo sobre los beneficios del yoga para la salud mental, enfocado a principiantes'",
            "Email marketing": "Describe la campaña y objetivo. Ej: 'Email promocionando un webinar gratuito sobre marketing digital'",
            "Infografía": "Describe el tema y datos clave a incluir. Ej: 'Infografía sobre estadísticas de uso de redes sociales en 2025'",
            "Newsletter": "Describe el tema y secciones. Ej: 'Newsletter mensual para una tienda de productos ecológicos'",
            "Podcast script": "Describe el tema y formato. Ej: 'Guión para un episodio de podcast sobre finanzas personales para millennials'"
        }
        
        prompt_base = st.text_area(
            "Ingresa tu prompt base:", 
            height=100, 
            help=prompt_ayuda.get(tipo_contenido, ""),
            key="prompt_forma1"
        )
        
        if prompt_base:
            prompt_completo = f"""
            Crea {tipo_contenido} sobre: {prompt_base}
            Tipo de respuesta requerida: {tipo_respuesta}
            El contenido debe ser original, atractivo y optimizado para la plataforma indicada.
            """
        else:
            prompt_completo = ""
            
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Generar Contenido", use_container_width=True, key="generar_forma1"):
                if tipo_contenido == "Selecciona el tipo de contenido que deseas crear":
                    st.error("Por favor, selecciona un tipo de contenido")
                elif tipo_respuesta == "Selecciona el tipo de respuesta que deseas":
                    st.error("Por favor, selecciona un tipo de respuesta")
                elif not prompt_base:
                    st.error("Por favor, ingresa un prompt")
                elif not st.session_state.get(f"{proveedor.lower()}_api_key"):
                    st.error(f"Por favor, configura tu API key de {proveedor} en la barra lateral")
                else:
                    with st.spinner(f"Generando contenido con {proveedor}..."):
                        resultado = generar_texto(prompt_completo, proveedor, tipo_contenido)
                        st.session_state.ultimo_resultado = resultado
                        guardar_en_historial(tipo_contenido, prompt_completo, resultado)
                        
    with tab2:
        st.subheader("Generación de Ideas")
        proveedor_ideas = st.selectbox(
            "Selecciona el proveedor de IA:",
            ["DeepSeek", "Mistral"],
            key="proveedor_forma2"
        )
        
        tema_ideas = st.text_area(
            "¿Sobre qué tema quieres generar ideas de contenido?", 
            height=100,
            help="Describe tu nicho, producto, servicio o tema sobre el que necesitas ideas",
            key="tema_ideas"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            audiencia = st.text_input(
                "¿Cuál es tu audiencia objetivo?",
                help="Ej: Emprendedores, estudiantes, profesionales de marketing, etc.",
                key="audiencia"
            )
        
        with col2:
            objetivo = st.selectbox(
                "¿Cuál es tu objetivo principal?",
                [
                    "Selecciona el objetivo que esperas",
                    "Aumentar engagement", 
                    "Educar a la audiencia", 
                    "Vender un producto/servicio",
                    "Generar leads",
                    "Crear autoridad",
                    "Entretener"
                ],
                key="objetivo"
            )
        
        if st.button("Generar Ideas de Contenido", key="generar_forma2"):
            if not tema_ideas:
                st.error("Por favor, ingresa un tema para generar ideas")
            elif objetivo == "Selecciona el objetivo que esperas":
                st.error("Por favor selecciona un objetivo")
            elif not st.session_state.get(f"{proveedor_ideas.lower()}_api_key"):
                st.error(f"Por favor, configura tu API key de {proveedor_ideas} en la barra lateral")
            else:
                prompt_ideas = f"""
                Eres el experto en estrategia de contenido digital. Para la generación de ideas de contenido sobre: {tema_ideas}
                La audiencia objetivo es: {audiencia}
                El objetivo principal que se espera es: {objetivo}
                
                Proporciona lo siguiente:
                1. Definición del tipo de formato que se adapte a las necesidades del tema y la audiencia como: (videos, reels, blogs, infografías, etc.)
                1. Ideas de contenido para plasmar en los formatos sugeridos.
                2. Para cada idea, sugiere:
                   - El formato más adecuado
                   - Un título atractivo
                   - Breve descripción del contenido
                   - Por qué funcionaría bien con la audiencia objetivo
                
                Prioriza formatos y temas que se adecuen al tipo de contenido y sugerencias de contenido y frecuencia de publicación del contenido.
                """
                
                with st.spinner(f"Generando ideas con {proveedor_ideas}..."):
                    resultado_ideas = generar_texto(prompt_ideas, proveedor_ideas, "Ideas de Contenido")
                    st.session_state.ultimo_resultado = resultado_ideas
                    guardar_en_historial("Ideas de Contenido", prompt_ideas, resultado_ideas)

    
    if 'ultimo_resultado' in st.session_state:
        st.subheader("Contenido Generado")
        if 'historial_versiones' not in st.session_state:
            st.session_state.historial_versiones = []
            
        if not st.session_state.historial_versiones or st.session_state.ultimo_resultado != st.session_state.historial_versiones[-1]['contenido']:
            st.session_state.historial_versiones.append({
                'contenido': st.session_state.ultimo_resultado,
                'timestamp': "Versión actual"
            })
        
        
        st.write("### Versión actual:")
        st.write(st.session_state.ultimo_resultado)
        
        # Acciones
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Copiar al Portapapeles", key="copiar"):
                st.info("Texto copiado al portapapeles!")
        
        with col2:
            compartir_opcion = st.selectbox(
                "Compartir en:",
                ["Seleccionar...", "Twitter/X", "Facebook", "LinkedIn", "Instagram", "WhatsApp"],
                key="compartir_opcion"
            )
            
            if compartir_opcion != "Seleccionar..." and st.button("Compartir", key="compartir"):
                compartir_en_redes(compartir_opcion, st.session_state.ultimo_resultado)
        
        # st.divider()
        # st.subheader("Generar nueva versión")
        
        # preferencias = st.text_area(
        #     "Especifica preferencias o enfoque para la nueva versión:",
        #     placeholder="Ejemplos: 'Hazlo más informal', 'Incluye más datos', 'Enfócate en los beneficios', 'Usa más emojis'...",
        #     key="preferencias_nueva_version"
        # )
        
        # if st.button("Generar Nueva Versión", key="nueva_version"):
        #     if "prompt_forma1" in st.session_state and st.session_state.prompt_forma1:
        #         prompt_base = prompt_completo
        #         proveedor_actual = proveedor
        #         tipo_actual = tipo_contenido
        #     else:
        #         prompt_base = prompt_ideas
        #         proveedor_actual = proveedor_ideas
        #         tipo_actual = "Ideas de Contenido"
            
        #     # Agregar las preferencias al prompt
        #     if preferencias:
        #         prompt_actual = f"{prompt_base}\n\nConsideraciones adicionales para esta versión: {preferencias}"
        #     else:
        #         prompt_actual = prompt_base
            
        #     with st.spinner(f"Generando nueva versión con {proveedor_actual}..."):
        #         resultado = generar_texto(prompt_actual, proveedor_actual, tipo_actual)
                
        #         if st.session_state.ultimo_resultado != resultado:
        #             if st.session_state.historial_versiones[-1]['timestamp'] == "Versión actual":
        #                 st.session_state.historial_versiones[-1]['timestamp'] = "Versión anterior"
                    
        #             guardar_en_historial(tipo_actual, prompt_actual, resultado)
                    
                    
        
        # if len(st.session_state.historial_versiones) > 1:
        #     st.divider()
        #     st.subheader("Comparación de Versiones")
            
        #     for i, version in enumerate(reversed(st.session_state.historial_versiones[:-1]), 1):
        #         with st.expander(f"Versión anterior {i}"):
        #             st.write(version['contenido'])
        #             st.caption(version['timestamp'])
                    
        #             if st.button(f"Restaurar esta versión", key=f"restaurar_{i}"):
        #                 st.session_state.ultimo_resultado = version['contenido']
        #                 st.rerun()

def compartir_en_redes(red_social, contenido):
    contenido_codificado = urllib.parse.quote_plus(contenido)
    
    enlaces = {
        "Twitter/X": f"https://x.com/intent/post?text={contenido_codificado}",
        "Facebook": f"https://www.facebook.com/share_channel?u={contenido_codificado}",
        "LinkedIn": f"https://www.linkedin.com/shareArticle?mini=true&url=&title=&summary={contenido_codificado}",
        "WhatsApp": f"https://wa.me/?text={contenido_codificado}",
        "Instagram": "https://www.instagram.com/" # Instagram no permite compartir directamente texto vía URL
    }
    
    if red_social in enlaces:
        enlace = enlaces[red_social]
        
        if red_social != "Twitter/X":
            st.info(f"{red_social} no permite compartir contenido directamente. Copia el texto y pégalo en tu aplicación de Instagram.")
            st.code(contenido)
        else:
            st.markdown(f"[Haz clic aquí para compartir en {red_social}]({enlace})")
            html_script = f"""
            <script>
            window.open("{enlace}", "_blank");
            </script>
            """
            st.components.v1.html(html_script, height=0)

            st.success(f"¡Se ha abierto una nueva pestaña para compartir en {red_social}!")
    else:
        st.error("Red social no soportada para compartir.")

def generar_codigo_ui():
    st.header("Generador de Código")
    
    col1, col2 = st.columns(2)
    
    with col1:
        proveedor = st.selectbox(
            "Selecciona el proveedor de IA:",
            ["DeepSeek", "Mistral"],
            key="codigo_proveedor"
        )
    
    with col2:
        lenguaje = st.selectbox(
            "Lenguaje de programación:",
            ["Python", "JavaScript", "Java", "C++", "PHP", "Go", "Ruby", "C#", "SQL", "TypeScript", "Swift", "Rust"]
        )
    
    st.subheader("Describe tu necesidad de código")
    descripcion = st.text_area(
        "Describe qué código necesitas:", 
        height=150,
        help="Describe con detalle qué debe hacer el código, funcionalidades, bibliotecas a utilizar, etc."
    )
    
    st.subheader("Opciones de generación")
    
    solo_codigo = st.checkbox("Solo código (sin explicaciones ni comentarios)", value=False, key="solo_codigo")
    
    if not solo_codigo:
        opciones_col1, opciones_col2 = st.columns(2)
        
        with opciones_col1:
            incluir_comentarios = st.checkbox("Incluir comentarios en el código", value=False, key="incluir_comentarios")
            incluir_explicacion = st.checkbox("Incluir explicación detallada", value=False, key="incluir_explicacion")
            incluir_ejemplo = st.checkbox("Incluir ejemplo de uso", value=False, key="incluir_ejemplo")
        
        with opciones_col2:
            incluir_analisis_complejidad = st.checkbox("Incluir análisis de complejidad", value=False, key="incluir_complejidad")
            incluir_analisis_rendimiento = st.checkbox("Incluir análisis de rendimiento", value=False, key="incluir_rendimiento")
            incluir_alternativas = st.checkbox("Incluir enfoques alternativos", value=False, key="incluir_alternativas")
    else:
        incluir_comentarios = False
        incluir_explicacion = False
        incluir_ejemplo = False
        incluir_analisis_complejidad = False
        incluir_analisis_rendimiento = False
        incluir_alternativas = False
        
    if st.button("Generar Código", use_container_width=True):
        if not solo_codigo and not (incluir_comentarios or incluir_explicacion or incluir_ejemplo or incluir_analisis_complejidad or incluir_analisis_rendimiento or incluir_alternativas):
            st.error("Por favor, selecciona al menos una opción de generación")
        elif not descripcion:
            st.error("Por favor, describe qué código necesitas")
        elif not st.session_state.get(f"{proveedor.lower()}_api_key"):
            st.error(f"Por favor, configura tu API key de {proveedor} en la barra lateral")
        else:
            prompt_completo = f"Genera código en {lenguaje} para la siguiente tarea:\n\n{descripcion}\n\n"
            
            if solo_codigo:
                prompt_completo += "IMPORTANTE: Proporciona SOLO el código, sin explicaciones, comentarios adicionales ni descripciones. El código debe ser completamente funcional y listo para usar."
            else:
                prompt_completo += "Incluye en tu respuesta:\n"
                
                if incluir_comentarios:
                    prompt_completo += "- Comentarios explicativos dentro del código\n"
                else:
                    prompt_completo += "- NO incluyas comentarios en el código\n"
                    
                if incluir_explicacion:
                    prompt_completo += "- Una explicación detallada de cómo funciona el código\n"
                    
                if incluir_ejemplo:
                    prompt_completo += "- Un ejemplo de uso con entrada y salida esperada\n"
                    
                if incluir_analisis_complejidad:
                    prompt_completo += "- Un análisis de la complejidad temporal y espacial del código\n"
                    
                if incluir_analisis_rendimiento:
                    prompt_completo += "- Un análisis del rendimiento y posibles optimizaciones\n"
                    
                if incluir_alternativas:
                    prompt_completo += "- Enfoques alternativos para resolver el mismo problema\n"
            
            with st.spinner(f"Generando código {lenguaje} con {proveedor}..."):
                resultado = generar_codigo(prompt_completo, proveedor, lenguaje)
                st.session_state.ultimo_codigo = resultado
                guardar_en_historial(f"Código {lenguaje}", prompt_completo, resultado)
                    
    if 'ultimo_codigo' in st.session_state:
        st.subheader("Código Generado")
        
        if 'historial_codigo' not in st.session_state:
            st.session_state.historial_codigo = []
        
        if not st.session_state.historial_codigo or st.session_state.ultimo_codigo != st.session_state.historial_codigo[-1]['codigo']:
            st.session_state.historial_codigo.append({
                'codigo': st.session_state.ultimo_codigo,
                'timestamp': "Versión actual"
            })
        
        st.code(st.session_state.ultimo_codigo, language=lenguaje.lower())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Copiar Código", key="copiar_codigo"):
                st.info("Código copiado al portapapeles!")
        
        st.divider()
        st.subheader("Mejorar o Refactorizar Código")
        
        mejora_descripcion = st.text_area(
            "Describe qué aspectos del código quieres mejorar:",
            placeholder="Ejemplos: 'Optimizar rendimiento', 'Hacerlo más legible', 'Simplificar la lógica', 'Usar características modernas de " + lenguaje + "', etc.",
            key="mejora_descripcion"
        )
        
        mejora_col1, mejora_col2, mejora_col3 = st.columns(3)
        
        with mejora_col1:
            if st.button("Optimizar Rendimiento", key="optimizar"):
                mejora_especifica = "Optimiza el rendimiento del código manteniendo la misma funcionalidad. Enfócate en mejorar la eficiencia y velocidad de ejecución."
                if mejora_descripcion:
                    mejora_especifica += f" Considera estas indicaciones adicionales: {mejora_descripcion}"
                
                nuevo_prompt = f"Revisa, mejora y optimiza el siguiente código {lenguaje} para mejorar su rendimiento:\n\n{st.session_state.ultimo_codigo}\n\n{mejora_especifica}"
                with st.spinner(f"Optimizando código con {proveedor}..."):
                    resultado = generar_codigo(nuevo_prompt, proveedor, lenguaje)
                    actualizar_historial_codigo(resultado)
        
        with mejora_col2:
            if st.button("Mejorar Legibilidad", key="legibilidad"):
                mejora_especifica = "Mejora la legibilidad y mantenibilidad del código. Enfócate en hacer el código más claro, mejor organizado y más fácil de mantener."
                if mejora_descripcion:
                    mejora_especifica += f" Considera estas indicaciones adicionales: {mejora_descripcion}"
                
                nuevo_prompt = f"Revisa y refactoriza el siguiente código {lenguaje} para mejorar su legibilidad y mantenibilidad:\n\n{st.session_state.ultimo_codigo}\n\n{mejora_especifica}"
                with st.spinner(f"Mejorando legibilidad con {proveedor}..."):
                    resultado = generar_codigo(nuevo_prompt, proveedor, lenguaje)
                    actualizar_historial_codigo(resultado)
        
        with mejora_col3:
            if st.button("Refactorizar", key="refactorizar"):
                mejora_especifica = "Refactoriza el código para mejorar su estructura, reducir duplicación y seguir mejores prácticas."
                if mejora_descripcion:
                    mejora_especifica += f" Considera estas indicaciones adicionales: {mejora_descripcion}"
                
                nuevo_prompt = f"Refactoriza el siguiente código {lenguaje}:\n\n{st.session_state.ultimo_codigo}\n\n{mejora_especifica}"
                with st.spinner(f"Refactorizando código con {proveedor}..."):
                    resultado = generar_codigo(nuevo_prompt, proveedor, lenguaje)
                    actualizar_historial_codigo(resultado)
        
        if st.button("Mejora Personalizada", use_container_width=True, key="mejora_personalizada"):
            if not mejora_descripcion:
                st.error("Por favor, describe qué aspectos del código quieres mejorar")
            else:
                nuevo_prompt = f"Revisa y mejora el siguiente código {lenguaje} según estas indicaciones específicas:\n\n{st.session_state.ultimo_codigo}\n\nMejoras solicitadas: {mejora_descripcion}"
                with st.spinner(f"Mejorando código con {proveedor}..."):
                    resultado = generar_codigo(nuevo_prompt, proveedor, lenguaje)
                    actualizar_historial_codigo(resultado)
        
        if len(st.session_state.historial_codigo) > 1:
            st.divider()
            st.subheader("Versiones Anteriores del Código")
            
            for i, version in enumerate(reversed(st.session_state.historial_codigo[:-1]), 1):
                with st.expander(f"Versión anterior {i}"):
                    st.code(version['codigo'], language=lenguaje.lower())
                    st.caption(version['timestamp'])
                    
                    if st.button(f"Restaurar esta versión", key=f"restaurar_codigo_{i}"):
                        st.session_state.ultimo_codigo = version['codigo']
                        st.rerun()

def actualizar_historial_codigo(nuevo_codigo):
    if st.session_state.ultimo_codigo != nuevo_codigo:
        if st.session_state.historial_codigo[-1]['timestamp'] == "Versión actual":
            st.session_state.historial_codigo[-1]['timestamp'] = "Versión anterior"
        
        st.session_state.ultimo_codigo = nuevo_codigo
        guardar_en_historial(f"Código {st.session_state.get('lenguaje', 'desconocido')}", "Mejora o refactorización", nuevo_codigo)

if __name__ == "__main__":
    main()