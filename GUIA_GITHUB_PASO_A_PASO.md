# Subir HidroPredict a GitHub con VS Code

## 1. Preparación

Instalar Git para Windows y abrir VS Code. Confirmar que el compañero haya dado acceso de escritura a `FabriPaniagua/IA` y que se haya aceptado la invitación.

## 2. Clonar (solo una vez)

Abrir una terminal PowerShell en una carpeta de trabajo:

```powershell
git clone https://github.com/FabriPaniagua/IA.git
cd IA
```

Si solicita autenticación, usar la ventana de inicio de sesión de GitHub; nunca compartir contraseñas ni tokens.

## 3. Copiar el proyecto

Copiar **el contenido interior** de la carpeta `HIDROPREDICT_ENTREGA_GITHUB` a la carpeta `IA` clonada. No reemplazar la carpeta oculta `.git` ni eliminar los ZIP anteriores sin acordarlo con el compañero.

## 4. Revisar y registrar cambios

```powershell
git status
git add .
git status
git commit -m "Integrar HidroPredict con API React Docker y auditoria"
git push origin main
```

Si Git solicita nombre y correo:

```powershell
git config --global user.name "TU_USUARIO_GITHUB"
git config --global user.email "TU_CORREO_GITHUB"
```

Si `git push` es rechazado por cambios nuevos, **no usar `--force`**. Ejecutar `git pull --rebase origin main`, resolver conflictos si aparecen y volver a hacer `git push origin main`.

## 5. Commits futuros

Tras cada cambio real:

```powershell
git add .
git commit -m "Describir brevemente el cambio realizado"
git push origin main
```

Ejemplos: `Documentar fuentes y calidad de datos`, `Agregar pruebas de pronostico`, `Corregir informe de cobertura`. No inventar fechas ni cambios.

## 6. Verificación final

En GitHub, confirmar que se ven las carpetas `backend`, `src`, `web`, `models`, `data`, `investigacion` y el archivo `docker-compose.yml`. Revisar el botón `Commits` para comprobar el historial. En otra carpeta, clonar el repositorio y ejecutar `docker compose up -d --build`.
