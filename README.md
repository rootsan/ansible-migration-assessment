## 🚀 Infrastructure Migration Risk Assessment Tool

Este proyecto de automatización con Ansible está diseñado para realizar una evaluación exhaustiva y no destructiva de infraestructuras de servidores heterogéneas (CentOS, RHEL, Ubuntu, Debian, SUSE).

Su objetivo principal es calcular un Risk Score (Puntuación de Riesgo) para determinar la viabilidad de migrar sistemas operativos Legacy (ej. CentOS 7) a versiones modernas y soportadas (RHEL 8/9), basándose en las mejores prácticas de Red Hat.

## 📋 Características Principales
* Multi-OS Support: Lógica diferenciada para familias Red Hat (yum/dnf) y Debian (apt).
* Risk Scoring Algorithm: Calcula un puntaje numérico basado en hallazgos críticos.
* Auditoría de "Caja Negra": No requiere conocer la aplicación; infiere el riesgo basado en puertos, servicios y logs.
* Pre-Flight Checks: Valida CPU, RAM, Disco y estabilidad del Kernel.
* Reporte Ejecutivo: Consolida los datos de cientos de servidores en un único archivo CSV (Excel-ready).

## 📂 Estructura del Proyecto
```text
migration-project/
├── ansible.cfg
├── inventory
├── group_vars/
│   └── all.yml            # Variables globales (pesos del score)
├── roles/
│   └── migration_assessment/
│       ├── defaults/
│       │   └── main.yml   # Valores por defecto
│       ├── tasks/
│       │   ├── main.yml          # Orquestador
│       │   ├── init.yml          # Inicialización de variables
│       │   ├── resources.yml     # CPU, RAM, Disco
│       │   ├── services.yml      # Puertos y Servicios
│       │   ├── logs.yml          # Análisis de Logs
│       │   ├── os_checks.yml     # Leapp, Apt, Zypper
│       │   └── report_local.yml  # Generación del JSON
│       └── templates/
│           └── assessment.json.j2 # Plantilla (opcional, aunque usaremos to_nice_json)
└── playbooks/
    ├── assess_infrastructure.yml  # Playbook principal que llama al rol
    └── generate_consolidated_csv.yml # Playbook de reporte (Control Node)
```

## ⚙️ Requisitos Previos
* Ansible Core 2.12+ instalado en el nodo de control.
* Acceso SSH a los nodos destino (preferiblemente con llaves SSH).
* Privilegios de sudo (root) sin contraseña para el usuario de automatización.
  - Nota: Requerido para leer logs del sistema (/var/log/messages) y ejecutar leapp.
* Python 2.7 o 3.6+ en los nodos destino (Ansible lo detecta automáticamente).

## 🚀 Guía de Uso Rápida
1. Configurar el Inventario
Edita el archivo inventory/hosts.yml para reflejar tu infraestructura. Asegúrate de agrupar los servidores correctamente.

```bash
vim inventory/hosts.yml
```
2. Validar Conectividad
Antes de lanzar la evaluación, asegura que Ansible "ve" a todos los servidores.

```bash
ansible -i inventory/hosts.yml all -m ping
```
3. Ejecutar la Evaluación de Riesgo (Risk Assessment)
Este playbook ejecutará el rol migration_assessment en todos los nodos. Generará un archivo JSON individual en /tmp de cada servidor.

```bash
ansible-playbook -i inventory/hosts.yml playbooks/assess_infrastructure.yml
```
> Nota: Este proceso es de lectura/análisis. No modifica archivos de configuración ni instala paquetes (salvo herramientas de diagnóstico si se configuran). Utiliza leapp en modo --analyze (simulación).

4. Generar el Reporte Consolidado
Una vez finalizada la evaluación, ejecuta este playbook para recolectar los JSONs y crear el CSV maestro en tu máquina local.

```bash
ansible-playbook -i inventory/hosts.yml playbooks/generate_consolidated_csv.yml
```
El reporte se guardará en la raíz del proyecto como: Master_Migration_Risk_Report.csv.

## 📊 Interpretación del Risk Score
El sistema asigna puntos acumulativos. A mayor puntaje, mayor riesgo y complejidad de migración.

| Puntos | Factor de Riesgo Detectado | Acción Sugerida |
| ----------- | ------- | ------- |
| +100 | Inhibidor crítico de Leapp / Error grave | Bloqueante. Requiere remediación manual obligatoria. |
|  +50 | Kernel Custom / No Estándar | Reinstalar kernel oficial antes de migrar. |
|  +40 | RAM < 2GB / Errores en Logs / Servicios Failed | Estabilizar el servidor o aumentar recursos. |
|  +30 | Espacio en / < 5GB / Paquetes retenidos (apt) | Limpieza de disco y actualizaciones previas. |
|  +20 | Repositorios de Terceros / Carga CPU Alta	| Deshabilitar repositorios externos. |
|  +15 | Stack Complejo (Bases de Datos, Web Servers) | Requiere ventana de mantenimiento y backup validado.|

Niveles de Clasificación
* 🟢 BAJO (0 - 19): Candidato ideal para migración automatizada masiva.
* 🟡 MODERADO (20 - 49): Requiere revisión menor (limpieza, recursos).
* 🟠 ALTO (50 - 99): Requiere intervención técnica antes de intentar migrar.
* 🔴 CRÍTICO (100+): NO MIGRAR. Considerar reinstalación (Replatforming).

Puedes ajustar los umbrales de sensibilidad en 
roles/migration_assessment/defaults/main.yml:

```yml

min_ram_mb: 2048          # Mínimo de RAM para considerar seguro
min_boot_space_mb: 500    # Espacio requerido en /boot
cpu_load_threshold: 0.8   # Umbral de carga de CPU (80%)
log_lines_to_check: 2000  # Profundidad de análisis de logs
```
🛡️ Solución de Problemas (Troubleshooting)
* Error: "Leapp preupgrade failed": Asegúrate de que el servidor CentOS 7 esté actualizado a la última versión menor (7.9) y tenga repositorios base accesibles.
* Error de conexión SSH: Verifica que tu usuario tenga permisos y que host_key_checking = False esté activo en ansible.cfg si estás rotando entornos.
* Tiempos de ejecución lentos: Ajusta el parámetro forks = 20 en ansible.cfg según la capacidad de tu nodo de control.


