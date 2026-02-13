🚀 Infrastructure Migration Risk Assessment Tool
Este proyecto de automatización con Ansible está diseñado para realizar una evaluación exhaustiva y no destructiva de infraestructuras de servidores heterogéneas (CentOS, RHEL, Ubuntu, Debian, SUSE).

Su objetivo principal es calcular un Risk Score (Puntuación de Riesgo) para determinar la viabilidad de migrar sistemas operativos Legacy (ej. CentOS 7) a versiones modernas y soportadas (RHEL 8/9), basándose en las mejores prácticas de Red Hat.

📋 Características Principales
* Multi-OS Support: Lógica diferenciada para familias Red Hat (yum/dnf) y Debian (apt).
* Risk Scoring Algorithm: Calcula un puntaje numérico basado en hallazgos críticos.
* Auditoría de "Caja Negra": No requiere conocer la aplicación; infiere el riesgo basado en puertos, servicios y logs.
* Pre-Flight Checks: Valida CPU, RAM, Disco y estabilidad del Kernel.
* Reporte Ejecutivo: Consolida los datos de cientos de servidores en un único archivo CSV (Excel-ready).

📂 Estructura del Proyecto
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
    
⚙️ Requisitos Previos
* Ansible Core 2.12+ instalado en el nodo de control.
* Acceso SSH a los nodos destino (preferiblemente con llaves SSH).
* Privilegios de sudo (root) sin contraseña para el usuario de automatización.
  - Nota: Requerido para leer logs del sistema (/var/log/messages) y ejecutar leapp.
* Python 2.7 o 3.6+ en los nodos destino (Ansible lo detecta automáticamente).

🚀 Guía de Uso Rápida
1. Configurar el Inventario
Edita el archivo inventory/hosts.yml para reflejar tu infraestructura. Asegúrate de agrupar los servidores correctamente.

{vim inventory/hosts.yml}

2. Validar Conectividad
Antes de lanzar la evaluación, asegura que Ansible "ve" a todos los servidores.

{ansible -i inventory/hosts.yml all -m ping}
