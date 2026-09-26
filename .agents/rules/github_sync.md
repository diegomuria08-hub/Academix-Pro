# Sincronización Automática con GitHub y Respaldo Continuo

1. **Guardado en Repositorio Remoto**:
   - Todo cambio aprobado o completado en el código debe ser inmediatamente commiteado y enviado al repositorio remoto de GitHub (`origin/main`).
   - Esto garantiza que los servicios conectados (Render, Vercel, CI/CD) se actualicen automáticamente con la versión más reciente.
   - Sirve como respaldo total ante cualquier pérdida accidental de archivos locales.

2. **Compilación de Artefactos**:
   - Tras cambios funcionales importantes en la aplicación móvil/frontend, compilar el APK con Flet y actualizar el binario `Academix-Pro.apk` tanto en la raíz del proyecto como en el Escritorio del usuario (`C:\Users\Diego Muria\OneDrive\Desktop\Academix-Pro.apk`).

