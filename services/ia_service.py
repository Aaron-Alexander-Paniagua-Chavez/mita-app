"""Asistente Gemini de MITA, con contexto por sesión y protección de datos."""
from __future__ import annotations

import logging
import re
import threading

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


LOG = logging.getLogger(__name__)

_INSTRUCCION_SISTEMA = """
Eres el asistente general de MITA, una aplicación de acompañamiento para personas mayores,
familiares y cuidadores. Responde en el idioma de la persona, con frases claras, amables y
breves. Puedes explicar cómo usar MITA, proponer actividades generales de bienestar y dar
orientación general no clínica. No diagnostiques, no ajustes medicamentos, no interpretes
síntomas, no pidas datos personales o clínicos y recuerda llamar a emergencias o consultar
un profesional ante una urgencia. No inventes funciones que MITA no tenga.
""".strip()

# Antes de una llamada remota se bloquean categorías que MITA prometió no enviar
# a integraciones externas. Es una defensa adicional al aviso de la interfaz.
_PATRON_SENSIBLE = re.compile(
    r"\b(contrase(?:ña|nas)|password|diagn[oó]stico|medicamento|dosis|alergia|"
    r"imc|historia cl[ií]nica|expediente|c[eé]dula|documento de identidad)\b",
    re.IGNORECASE,
)


class AsistenteIA:
    """Cliente de Gemini usando el SDK oficial y el modelo configurado en ``.env``."""

    def __init__(self) -> None:
        self.client = None
        self.chat_session = None
        self.conectado = False
        self.modelo_activo = ""
        self.ultimo_error = ""
        self._lock = threading.Lock()
        self._inicializar_cliente()

    def _inicializar_cliente(self) -> None:
        if not GEMINI_API_KEY:
            self.ultimo_error = "Falta configurar GEMINI_API_KEY en .env."
            LOG.info("IA no configurada: GEMINI_API_KEY vacía")
            return
        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self._crear_conversacion()
            self.conectado = self.chat_session is not None
        except Exception as exc:  # noqa: BLE001 - el SDK puede exponer errores de red variados.
            self.ultimo_error = self._mensaje_error(exc)
            self.client = None
            self.chat_session = None
            LOG.warning("No fue posible inicializar Gemini: %s", self.ultimo_error)

    def _modelos_a_probar(self) -> tuple[str, ...]:
        # Respeta el modelo del usuario y ofrece la opción actual documentada
        # para cuentas que no tengan acceso al modelo heredado configurado.
        candidatos = [GEMINI_MODEL.strip(), "gemini-3.6-flash"]
        return tuple(modelo for indice, modelo in enumerate(candidatos) if modelo and modelo not in candidatos[:indice])

    def _crear_conversacion(self, excluir: set[str] | None = None) -> None:
        if not self.client:
            return
        excluir = excluir or set()
        ultimo_error = None
        configuracion = types.GenerateContentConfig(system_instruction=_INSTRUCCION_SISTEMA)
        for modelo in self._modelos_a_probar():
            if modelo in excluir:
                continue
            try:
                self.chat_session = self.client.chats.create(model=modelo, config=configuracion)
                self.modelo_activo = modelo
                self.ultimo_error = ""
                return
            except Exception as exc:  # noqa: BLE001
                ultimo_error = exc
        self.chat_session = None
        self.ultimo_error = self._mensaje_error(ultimo_error)

    def enviar_mensaje(self, texto_usuario: str) -> str:
        """Envía una consulta general y mantiene el contexto sólo de la sesión actual."""
        texto = (texto_usuario or "").strip()
        if not self.conectado or not self.chat_session:
            return f"IA no disponible. {self.ultimo_error or 'Revise la configuración de Gemini.'}"
        if not texto:
            return "Escribe una pregunta para el asistente."
        if len(texto) > 700:
            return "Por seguridad, escribe una pregunta de hasta 700 caracteres."
        if _PATRON_SENSIBLE.search(texto):
            return "Por privacidad, no envíes datos clínicos, credenciales ni identificaciones al asistente. Formula una pregunta general."
        try:
            with self._lock:
                response = self.chat_session.send_message(message=texto)
            respuesta = (getattr(response, "text", "") or "").strip()
            if respuesta:
                return respuesta
            return "No recibí una respuesta de Gemini. Intenta nuevamente en unos segundos."
        except Exception as exc:  # noqa: BLE001
            # ``chats.create`` no siempre valida el modelo hasta el primer
            # mensaje. Si el modelo indicado en .env ya no está habilitado,
            # se prueba una vez la alternativa oficial sin perder la consulta.
            if self._es_error_modelo(exc):
                try:
                    with self._lock:
                        self._crear_conversacion(excluir={self.modelo_activo})
                        if self.chat_session:
                            response = self.chat_session.send_message(message=texto)
                            respuesta = (getattr(response, "text", "") or "").strip()
                            if respuesta:
                                return respuesta
                except Exception as reintento_error:  # noqa: BLE001
                    exc = reintento_error
            self.ultimo_error = self._mensaje_error(exc)
            LOG.warning("Error al consultar Gemini: %s", self.ultimo_error)
            return f"No fue posible consultar la IA. {self.ultimo_error}"

    def reiniciar_conversacion(self) -> None:
        """Descarta el contexto anterior al cerrar sesión o limpiar el chat."""
        if not self.client:
            self._inicializar_cliente()
            return
        with self._lock:
            self._crear_conversacion()
            self.conectado = self.chat_session is not None

    @staticmethod
    def _es_error_modelo(error: Exception) -> bool:
        texto = str(error).lower()
        return "model" in texto or "not found" in texto or "404" in texto

    @staticmethod
    def _mensaje_error(error: Exception | None) -> str:
        texto = str(error or "Error desconocido").replace("\n", " ")
        # No se devuelven detalles internos del SDK ni posibles datos del entorno.
        if "API key" in texto or "api_key" in texto.lower() or "401" in texto:
            return "La clave de Gemini no es válida o fue revocada."
        if "429" in texto or "quota" in texto.lower() or "rate" in texto.lower():
            return "Gemini alcanzó temporalmente su límite de solicitudes."
        if "404" in texto or "not found" in texto.lower() or "model" in texto.lower():
            return "El modelo configurado no está disponible para esta clave."
        return "Comprueba la conexión a Internet y la configuración de Gemini."

    @property
    def estado(self) -> str:
        if self.conectado:
            return f"IA lista ({self.modelo_activo})"
        return f"IA no disponible: {self.ultimo_error or 'sin configurar'}"
