"""Reportes nivel 10 para administradores, médicos y cuidadores (Sin diagnósticos clínicos)."""
from typing import Optional, Dict, Any
from repositories.usuario_repository import UsuarioRepository
from repositories.progreso_repository import ProgresoRepository
from repositories.medicamento_repository import MedicamentoRepository
from repositories.dieta_sueno_repository import DietaSuenoRepository
from repositories.actividad_repository import ActividadRepository


class AnalisisService:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        progreso_repo: ProgresoRepository,
        med_repo: MedicamentoRepository,
        dieta_sueno_repo: Optional[DietaSuenoRepository] = None,
        actividad_repo: Optional[ActividadRepository] = None,
    ):
        self._usuario_repo = usuario_repo
        self._progreso_repo = progreso_repo
        self._med_repo = med_repo
        self._dieta_sueno_repo = dieta_sueno_repo
        self._actividad_repo = actividad_repo

    def generar_reporte_paciente(self, id_usuario_adulto: int) -> Dict[str, Any]:
        """Genera reporte integral Nivel 10 de hábitos, adherencia y actividad de un paciente."""
        usuario = self._usuario_repo.obtener_por_id(id_usuario_adulto)
        if not usuario or usuario["rol"] != "Adulto Mayor":
            return {"error": "Paciente no encontrado."}

        # Progreso acumulado
        progreso = self._progreso_repo.obtener_progreso_vista(id_usuario_adulto)

        # Adherencia a medicamentos
        rows_adherencia = self._usuario_repo._db.ejecutar_mysql(
            "SELECT id FROM adulto_mayor WHERE id_usuario = %s", (id_usuario_adulto,)
        )
        id_adulto = rows_adherencia[0]["id"] if rows_adherencia else None
        adherencia_list = self._med_repo.obtener_adherencia_vista(id_adulto) if id_adulto else []

        # Registro de sueño
        sueno_list = self._dieta_sueno_repo.obtener_registros_sueno(id_adulto, limite=7) if (id_adulto and self._dieta_sueno_repo) else []
        promedio_sueno = 0
        if sueno_list:
            duraciones = [s.get("duracion_minutos") or 0 for s in sueno_list if s.get("duracion_minutos")]
            promedio_sueno = round(sum(duraciones) / len(duraciones) / 60, 1) if duraciones else 0

        # Historial de actividades recientes
        actividades_recientes = self._actividad_repo.listar_actividades_usuario(id_usuario_adulto, limite=10) if self._actividad_repo else []

        return {
            "paciente": usuario["nombre"],
            "correo": usuario["correo"],
            "puntos": progreso.get("puntos", 0),
            "actividades_completadas": progreso.get("actividades_completadas", 0),
            "cognitivas_completadas": progreso.get("cognitivas_completadas", 0),
            "fisicas_completadas": progreso.get("fisicas_completadas", 0),
            "adherencia_medicacion": adherencia_list,
            "promedio_sueno_horas_diarias": promedio_sueno,
            "actividades_recientes": actividades_recientes,
        }

    def generar_reporte_global() -> Dict[str, Any]:
        usuarios = self._usuario_repo.listar_todos()
        adultos = [u for u in usuarios if u["rol"] == "Adulto Mayor"]
        cuidadores = [u for u in usuarios if u["rol"] in ("Cuidador", "Médico")]
        familiares = [u for u in usuarios if u["rol"] == "Familiar"]

        return {
            "total_usuarios": len(usuarios),
            "total_adultos": len(adultos),
            "total_cuidadores": len(cuidadores),
            "total_familiares": len(familiares),
        }
