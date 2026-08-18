"""Servicio de Inteligencia Artificial para MITA usando Google Gemini.

Reglas:
- Nunca transmite información clínica (diagnósticos, medicamentos, IMC, etc.).
- Funciona como servicio opcional - si no hay API key, se desactiva silenciosamente.
- Mantiene contexto de conversación para chats coherentes.
"""
from __future__ import annotations

import os
import logging
from typing import Optional

from google import genai

LOG = logging.getLogger(__name__)


class AsistenteIA:
    """Wrapper para el servicio de Google Gemini con manejo de errores y contexto."""

    def __init__(self) -> None:
        """Inicializa el cliente de IA si hay API key disponible."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.strip() == "":
            LOG.info("IA no configurada: GEMINI_API_KEY no encontrada o vacía")
            self.conectado = False
            self.client = None
            self.chat_session = None
            return

        try:
            # El cliente detecta automáticamente la variable de entorno 'GEMINI_API_KEY'
            self.client = genai.Client(api_key=api_key)
            # Usamos el modelo rápido y optimizado para texto y chat
            self.chat_session = self.client.chats.create(model="gemini-3.6-flash")
            self.conectado = True
            LOG.info("IA inicializada correctamente con modelo gemini-3.6-flash")
        except Exception as e:
            LOG.error(f"Error al inicializar la IA: {e}")
            self.conectado = False
            self.client = None
            self.chat_session = None

    def enviar_mensaje(self, texto_usuario: str) -> str:
        """Envía un mensaje a la IA manteniendo el hilo de conversación.

        Args:
            texto_usuario: Mensaje del usuario

        Returns:
            Respuesta de la IA o mensaje de error
        """
        if not self.conectado:
            return (
                "Error: La IA no está conectada o falta configurar la API Key. "
                "Configure GEMINI_API_KEY en su archivo .env para usar esta función."
            )

        if not texto_usuario or not texto_usuario.strip():
            return "Por favor, ingrese un mensaje para enviar a la IA."

        try:
            # Envía el mensaje manteniendo el hilo de la conversación anterior
            response = self.chat_session.send_message(message=texto_usuario.strip())
            return response.text
        except Exception as e:
            LOG.error(f"Error al comunicarse con la IA: {e}")
            return f"Ocurrió un error al comunicarse con la IA: {str(e)}"

    def reiniciar_conversacion(self) -> None:
        """Reinicia la sesión de chat, perdiendo el contexto anterior."""
        if self.conectado and self.client:
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                self.chat_session = self.client.chats.create(model="gemini-3.6-flash")
                LOG.info("Conversación de IA reiniciada")
            except Exception as e:
                LOG.error(f"Error al reiniciar conversación de IA: {e}")
                self.conectado = False

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la IA para mostrar en la UI."""
        if self.conectado:
            return "IA conectada y lista"
        return "IA no disponible - configure GEMINI_API_KEY en .env"


# --- Ejemplo de prueba rápida en consola ---
if __name__ == "__main__":
    ia = AsistenteIA()

    print("--- Chat con IA iniciado (Escribe 'salir' para terminar) ---")
    while True:
        pregunta = input("\nTú: ")
        if pregunta.lower() == "salir":
            break

        respuesta = ia.enviar_mensaje(pregunta)
        print(f"IA: {respuesta}")