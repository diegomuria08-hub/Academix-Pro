import flet as ft

# ─── Paleta vibrant para adolescentes ──────────────────────────
class AcademixColors:
    # ─── Neón y Acentos Principales ───
    CYAN_NEON      = "#00E5FF"   # Cyan neón birrete y bordes brillantes
    CYAN_GLOW      = "#00F2FE"   # Cyan resplandor
    YELLOW_NEON    = "#FFE500"   # Amarillo neón "Pro" y enlaces
    YELLOW_GOLD    = "#FACC15"   # Amarillo dorado
    
    PRIMARY        = "#6366F1"   # Indigo vibrante
    PRIMARY_PURPLE = "#8B5CF6"   # Púrpura brillante para degradados
    ACCENT         = "#00E5FF"   # Cyan de acento principal
    ACCENT_SOFT    = "#38BDF8"   # Cyan suave
    
    SUCCESS        = "#00E676"   # Verde neón aprobadas
    SUCCESS_DARK   = "#10B981"
    WARNING        = "#F59E0B"   # Ámbar
    ERROR          = "#FF5252"   # Rojo neón reprobadas
    
    # ─── Gradiente de fondo profundo (Deep Midnight Navy) ───
    BG_START       = "#060D1A"   # Azul marino casi negro profundo
    BG_END         = "#0B162C"   # Azul marino noche
    
    # ─── Superficies Glassmorphism (Vidrio translúcido) ───
    GLASS_BG       = "#0D1B2A"   # Base para vidrios
    GLASS_BORDER   = "#2A3B53"   # Borde sutil de cristal
    SURFACE_1      = "#0F1E36"   # Card base
    SURFACE_2      = "#142644"   # Card elevada
    SURFACE_3      = "#1B3156"   # Card alta
    
    # ─── Texto ───
    TEXT_PRIMARY   = "#FFFFFF"
    TEXT_MUTED     = "#94A3B8"
    TEXT_CYAN      = "#00E5FF"

def get_theme(is_dark=True):
    return ft.Theme(
        color_scheme_seed=AcademixColors.CYAN_NEON,
        visual_density=ft.VisualDensity.COMFORTABLE,
        font_family="Roboto",
    )
