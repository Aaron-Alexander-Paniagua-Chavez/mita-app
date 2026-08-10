"""Localización básica de MITA.

El Náhuatl se marca como piloto: la interfaz cubre las rutas principales, pero
una persona hablante debe validarla antes de una publicación para comunidad.
"""
from __future__ import annotations


IDIOMAS = {
    "es": "Español",
    "en": "English",
    "nah": "Náhuatl (piloto)",
}


_T = {
    "en": {
        "Accesibilidad": "Accessibility",
        "Texto": "Text",
        "Modo oscuro": "Dark mode",
        "Idioma": "Language",
        "¿Quién eres?": "Who are you?",
        "Soy adulto mayor": "I am an older adult",
        "Soy familiar o encargado": "I am a family member or caregiver",
        "Soy médico, enfermero o cuidador": "I am a doctor, nurse, or caregiver",
        "Volver": "Back",
        "Volver al Menú": "Back to menu",
        "Cerrar sesión": "Sign out",
        "Entrar": "Sign in",
        "Guardar": "Save",
        "Cancelar": "Cancel",
        "Sí, continuar": "Yes, continue",
        "Confirmar": "Confirm",
        "¿Está seguro?": "Are you sure?",
        "Iniciar sesión": "Sign in",
        "Correo o nombre completo": "Email or full name",
        "Contraseña": "Password",
        "Ejercicio físico": "Physical exercise",
        "Ejercicio cognitivo": "Cognitive exercise",
        "Ver catálogo": "View catalog",
        "Ver actividades": "View activities",
        "Inicio": "Home",
        "Progreso": "Progress",
        "Comunidad": "Community",
        "Logros": "Achievements",
        "Ejercicios físicos": "Physical exercises",
        "Actividades cognitivas": "Cognitive activities",
        "Instrucciones": "Instructions",
        "COMENZAR ACTIVIDAD": "START ACTIVITY",
        "Tu progreso": "Your progress",
        "Mis logros": "My achievements",
        "Comunidad MITA": "MITA Community",
        "Escribe un mensaje...": "Write a message...",
        "Enviar": "Send",
        "Panel Familiar": "Family panel",
        "Panel Médico": "Medical panel",
        "Panel Administrador MITA": "MITA Administrator panel",
        "Registrar nuevo adulto mayor": "Register a new older adult",
        "Registrar adulto mayor": "Register older adult",
        "Registrar familiar": "Register family member",
        "Editar rol": "Edit role",
        "Comprobar conexión MySQL": "Check MySQL connection",
        "Salir del panel admin": "Leave administrator panel",
        "Acceso Administrador": "Administrator access",
        "Usuario admin": "Administrator user",
        "Registro personal": "Personal registration",
        "Registro profesional": "Professional registration",
        "Registro": "Registration",
        "Tamaño de texto ajustado": "Text size adjusted",
        "Modo claro": "Light mode",
        "Modo oscuro activado": "Dark mode enabled",
    },
    "nah": {
        "Accesibilidad": "Tlanextiliztli",
        "Texto": "Tlàtōlli",
        "Modo oscuro": "Yohualli tlachiyalistli",
        "Idioma": "Tlahtōl",
        "¿Quién eres?": "¿Aquin tehuatl?",
        "Soy adulto mayor": "Nehua huehue tlacatl",
        "Soy familiar o encargado": "Nehua nechicoliztli",
        "Soy médico, enfermero o cuidador": "Nehua tepajtiani o tlapalehuiani",
        "Volver": "Ximocuepa",
        "Volver al Menú": "Ximocuepa tlanahuatilli",
        "Cerrar sesión": "Xicahua calaquilistli",
        "Entrar": "Xicalaqui",
        "Guardar": "Xicpiyā",
        "Cancelar": "Xicahua",
        "Iniciar sesión": "Xipehua calaquilistli",
        "Correo o nombre completo": "Correo noso motōcā",
        "Contraseña": "Tlanahuatil tlatzacuilli",
        "Ejercicio físico": "Tlacayotl tequitl",
        "Ejercicio cognitivo": "Tlamatilistli tequitl",
        "Ver catálogo": "Xictlachili amatlacuilolli",
        "Ver actividades": "Xictlachili tequitl",
        "Inicio": "Pehualli",
        "Progreso": "Mochihualli",
        "Comunidad": "Altepetl",
        "Logros": "Tlatlani",
        "Ejercicios físicos": "Tlacayotl tequitl",
        "Actividades cognitivas": "Tlamatilistli tequitl",
        "Instrucciones": "Tlanahuatilli",
        "COMENZAR ACTIVIDAD": "XIPEHUA TEQUITL",
        "Tu progreso": "Mochihualli",
        "Mis logros": "Notlatlani",
        "Comunidad MITA": "MITA Altepetl",
        "Escribe un mensaje...": "Xictlàtōlti se amatl...",
        "Enviar": "Xictitlāni",
        "Panel Familiar": "Nechicoliztli panel",
        "Panel Médico": "Tepajtiani panel",
        "Panel Administrador MITA": "MITA tlanahuatiani panel",
        "Registrar nuevo adulto mayor": "Xictlacuilo yancuic huehue tlacatl",
        "Registrar adulto mayor": "Xictlacuilo huehue tlacatl",
        "Registrar familiar": "Xictlacuilo nechicoliztli",
        "Editar rol": "Xicpatla tequitl",
        "Comprobar conexión MySQL": "Xictlachili MySQL tlatzintli",
        "Salir del panel admin": "Xicahua tlanahuatiani panel",
        "Acceso Administrador": "Tlanahuatiani calaquilistli",
        "Usuario admin": "Tlanahuatiani tlacatl",
        "Registro personal": "Motech tlacuilolli",
        "Registro profesional": "Tepajtiani tlacuilolli",
        "Registro": "Tlacuilolli",
        "Tamaño de texto ajustado": "Tlàtōlli ihueyi mopatla",
        "Modo claro": "Tlanextli tlachiyalistli",
        "Modo oscuro activado": "Yohualli tlachiyalistli pehua",
    },
}

_idioma_actual = "es"


def idioma_actual() -> str:
    return _idioma_actual


def establecer_idioma(codigo: str) -> None:
    global _idioma_actual
    if codigo in IDIOMAS:
        _idioma_actual = codigo


def traducir(texto: str) -> str:
    """Traduce texto de interfaz originalmente escrito en español.

    Los reemplazos de fragmentos permiten conservar nombres de personas y otros
    valores dinámicos, por ejemplo ``Panel Familiar — Ana``.
    """
    if not texto or _idioma_actual == "es":
        return texto
    tabla = _T.get(_idioma_actual, {})
    if texto in tabla:
        return tabla[texto]
    resultado = texto
    for origen, destino in sorted(tabla.items(), key=lambda item: len(item[0]), reverse=True):
        resultado = resultado.replace(origen, destino)
    return resultado
