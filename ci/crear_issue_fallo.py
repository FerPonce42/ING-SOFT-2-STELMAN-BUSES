"""Crea un issue en GitHub cuando falla una etapa del pipeline de Jenkins (issue #63).

Variables de entorno:
  GITHUB_TOKEN       token con permiso de issues (credencial de Jenkins, nunca en el repo)
  GITHUB_REPO        por defecto FerPonce42/ING-SOFT-2-STELMAN-BUSES
  GITHUB_API         por defecto https://api.github.com
  STAGE_NAME         etapa que falló (opcional)
  BUILD_NUMBER, BUILD_URL, GIT_BRANCH, GIT_COMMIT   los define Jenkins
  ISSUE_ASSIGNEES    usuarios separados por coma (por defecto iairalejandro)
  SLACK_WEBHOOK_URL  si existe, avisa también por Slack
"""
import json
import os
import sys
import urllib.request

EQUIPO = ["FerPonce42", "Arleondo", "CieloKaren", "iairalejandro", "NicolFer", "ru0505"]
REPO = os.environ.get("GITHUB_REPO", "FerPonce42/ING-SOFT-2-STELMAN-BUSES")
API = os.environ.get("GITHUB_API", "https://api.github.com")


def _post(url, datos, cabeceras):
    peticion = urllib.request.Request(
        url, data=json.dumps(datos).encode("utf-8"), headers=cabeceras, method="POST")
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode("utf-8") or "{}")


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Falta GITHUB_TOKEN", file=sys.stderr)
        return 1

    etapa = os.environ.get("STAGE_NAME", "desconocida")
    numero = os.environ.get("BUILD_NUMBER", "?")
    url_build = os.environ.get("BUILD_URL", "")
    rama = os.environ.get("GIT_BRANCH", "")
    commit = os.environ.get("GIT_COMMIT", "")[:7]
    asignados = [u.strip() for u in os.environ.get("ISSUE_ASSIGNEES", "iairalejandro").split(",") if u.strip()]

    titulo = f"[CI] Falló la etapa '{etapa}' en el build #{numero}"
    cuerpo = (
        f"El pipeline de Jenkins falló.\n\n"
        f"- Etapa: {etapa}\n"
        f"- Build: #{numero}\n"
        f"- Rama: {rama}\n"
        f"- Commit: {commit}\n"
        f"- Log: {url_build}console\n\n"
        + "Aviso al equipo: " + " ".join(f"@{u}" for u in EQUIPO)
    )
    cabeceras = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    issue = _post(f"{API}/repos/{REPO}/issues",
                  {"title": titulo, "body": cuerpo, "assignees": asignados}, cabeceras)
    print(f"Issue creado: {issue.get('html_url')}")

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        _post(webhook, {"text": f"{titulo}\n{issue.get('html_url')}"}, {"Content-Type": "application/json"})
        print("Notificación enviada a Slack")
    return 0


if __name__ == "__main__":
    sys.exit(main())
