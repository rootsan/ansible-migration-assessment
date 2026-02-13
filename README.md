# Ansible Migration Assessment Tool

**Herramienta de Evaluación de Migración de Infraestructura Legacy**

Este proyecto evalúa la viabilidad de migración de infraestructuras Legacy (CentOS 7) a RHEL 8/9, implementando:
- ✅ **Risk Scoring (Puntuación de Riesgo)**: Sistema de evaluación de riesgo basado en múltiples factores
- ✅ **Normalización de Datos**: Compatibilidad entre familias de SO Debian/RedHat
- ✅ **Reportes Ejecutivos CSV**: Generación automática para toma de decisiones basada en datos

## 🎯 Características Principales

### Risk Scoring System
- Evaluación ponderada de 5 categorías:
  - **OS Version (30%)**: Antigüedad y soporte del sistema operativo
  - **Package Compatibility (25%)**: Compatibilidad de paquetes instalados
  - **Hardware (20%)**: Recursos de hardware disponibles
  - **Services (15%)**: Servicios críticos y su compatibilidad
  - **Kernel Modules (10%)**: Complejidad de módulos del kernel

### Normalización de Datos
- Soporte para múltiples familias de SO:
  - RedHat (CentOS, RHEL, Fedora)
  - Debian (Ubuntu, Debian)
- Unificación de formatos de paquetes (RPM/DEB)
- Estandarización de información del sistema

### Reportes CSV Ejecutivos
1. **Executive Summary**: Vista general de todos los sistemas
2. **Detailed Assessment**: Desglose por categorías de riesgo
3. **Migration Priority Matrix**: Priorización por nivel de riesgo
4. **Statistics Summary**: Análisis estadístico agregado

## 📋 Requisitos

- **Ansible** 2.9 o superior
- **Python** 3.6 o superior
- **SSH access** a los servidores a evaluar
- **Privilegios sudo** en los servidores objetivo

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/rootsan/ansible-migration-assessment.git
cd ansible-migration-assessment

# Instalar dependencias (opcional)
pip install -r requirements.txt

# Configurar inventory
cp inventory/hosts.ini.example inventory/hosts.ini
# Editar inventory/hosts.ini con tus servidores
```

## 📖 Uso

### Paso 1: Configurar Inventory

Edita `inventory/hosts.ini` o `inventory/hosts.yml` con tus servidores:

```ini
[legacy_servers]
centos7-server1 ansible_host=192.168.1.10 ansible_user=admin
centos7-server2 ansible_host=192.168.1.11 ansible_user=admin

[rhel_servers]
rhel7-server1 ansible_host=192.168.1.20 ansible_user=admin
```

### Paso 2: Recopilar Información del Sistema

```bash
cd playbooks
ansible-playbook gather_system_info.yml
```

Este playbook:
- Conecta a todos los servidores especificados
- Recopila información del sistema (OS, paquetes, servicios, hardware)
- Guarda los datos en formato JSON en el directorio `output/`

### Paso 3: Ejecutar Evaluación y Generar Reportes

```bash
cd scripts
python3 run_assessment.py ../output
```

Este script:
1. Analiza los datos recopilados
2. Calcula puntuaciones de riesgo
3. Genera reportes CSV ejecutivos

## 📊 Reportes Generados

Los reportes se generan en el directorio `output/`:

### 1. Executive Summary (`executive_summary_YYYYMMDD_HHMMSS.csv`)
Vista consolidada de todos los sistemas evaluados con:
- Hostname y FQDN
- Distribución y versión del SO
- Puntuación global de riesgo (0-100)
- Nivel de riesgo (LOW, MEDIUM, MEDIUM-HIGH, HIGH)
- Recomendaciones

### 2. Detailed Assessment (`detailed_assessment_YYYYMMDD_HHMMSS.csv`)
Desglose detallado por categoría:
- Puntuación por categoría
- Pesos aplicados
- Issues específicos encontrados

### 3. Migration Priority Matrix (`migration_priority_YYYYMMDD_HHMMSS.csv`)
Matriz de priorización ordenada por riesgo:
- Prioridad de migración (1, 2, 3...)
- Timeline recomendado
- Acciones recomendadas

### 4. Statistics Summary (`statistics_summary_YYYYMMDD_HHMMSS.csv`)
Análisis estadístico agregado:
- Distribución de niveles de riesgo
- Distribución por familia de SO
- Promedios y totales

## 🎨 Interpretación de Resultados

### Niveles de Riesgo

| Puntuación | Nivel | Acción Recomendada |
|------------|-------|-------------------|
| 70-100 | **HIGH** | Migración inmediata (0-3 meses) |
| 50-69 | **MEDIUM-HIGH** | Planificar migración (3-6 meses) |
| 30-49 | **MEDIUM** | Programar migración (6-12 meses) |
| 0-29 | **LOW** | Migración a conveniencia (12+ meses) |

### Factores de Riesgo Evaluados

1. **OS Version**: CentOS 7 y versiones EOL reciben puntuaciones altas
2. **Package Compatibility**: Paquetes obsoletos (Python2, PHP5, etc.)
3. **Hardware**: Memoria < 2GB, CPU < 2 cores
4. **Services**: Servicios deprecados (network.service, iptables)
5. **Kernel Modules**: Complejidad del sistema (número de módulos)

## 🔧 Configuración Avanzada

### Personalizar Pesos de Riesgo

Edita `scripts/assess_migration.py` para ajustar los pesos:

```python
WEIGHTS = {
    'os_version': 30,           # Ajustar según prioridades
    'package_compatibility': 25,
    'hardware': 20,
    'services': 15,
    'kernel_modules': 10
}
```

### Añadir Paquetes Problemáticos

```python
PROBLEMATIC_PACKAGES = [
    'python2', 'python-',
    'mysql-server-5.5',
    # Añadir más paquetes aquí
]
```

## 📁 Estructura del Proyecto

```
ansible-migration-assessment/
├── ansible.cfg                    # Configuración de Ansible
├── inventory/                     # Inventarios de servidores
│   ├── hosts.ini                 # Formato INI
│   └── hosts.yml                 # Formato YAML
├── playbooks/                     # Playbooks de Ansible
│   └── gather_system_info.yml    # Recopilación de información
├── scripts/                       # Scripts Python de análisis
│   ├── assess_migration.py       # Evaluación de riesgo
│   ├── generate_reports.py       # Generador de reportes CSV
│   └── run_assessment.py         # Orquestador principal
├── output/                        # Directorio de salida
│   ├── *_system_info.json        # Datos recopilados
│   ├── assessment_results.json   # Resultados de evaluación
│   └── *.csv                     # Reportes CSV generados
└── README.md                      # Esta documentación
```

## 🔍 Ejemplo de Flujo Completo

```bash
# 1. Preparar entorno
cd ansible-migration-assessment
vim inventory/hosts.ini  # Configurar servidores

# 2. Recopilar datos
cd playbooks
ansible-playbook gather_system_info.yml

# 3. Ejecutar evaluación
cd ../scripts
python3 run_assessment.py ../output

# 4. Revisar reportes
cd ../output
ls -la *.csv
```

## 🛠️ Troubleshooting

### Problema: "No system data found to assess"
**Solución**: Ejecutar primero el playbook `gather_system_info.yml`

### Problema: "Permission denied" al conectar a servidores
**Solución**: Verificar:
- Claves SSH configuradas correctamente
- Usuario tiene privilegios sudo
- `ansible_become_password` configurado si es necesario

### Problema: Falta información en los reportes
**Solución**: Verificar que los archivos JSON en `output/` contienen datos completos

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 👥 Autores

- **rootsan** - *Trabajo inicial* - [rootsan](https://github.com/rootsan)

## 🙏 Agradecimientos

- Comunidad de Ansible
- Documentación oficial de RHEL
- Herramientas de migración de Red Hat

## 📞 Soporte

Para reportar bugs o solicitar features, por favor abre un issue en:
https://github.com/rootsan/ansible-migration-assessment/issues