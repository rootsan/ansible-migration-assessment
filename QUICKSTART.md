# Quick Start Guide

## Guía Rápida de Uso

### 1. Configuración Inicial (5 minutos)

```bash
# Clonar repositorio
git clone https://github.com/rootsan/ansible-migration-assessment.git
cd ansible-migration-assessment

# Configurar inventory con tus servidores
vi inventory/hosts.ini
```

Añade tus servidores al inventory:
```ini
[legacy_servers]
server1 ansible_host=192.168.1.10 ansible_user=admin

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### 2. Ejecutar Evaluación (10-30 minutos)

```bash
# Recopilar información (toma unos minutos por servidor)
cd playbooks
ansible-playbook gather_system_info.yml

# Generar evaluación y reportes (instantáneo)
cd ../scripts
python3 run_assessment.py ../output
```

### 3. Revisar Resultados

Los reportes CSV se encuentran en `output/`:

```bash
cd ../output
ls -la *.csv

# Ver resumen ejecutivo
cat executive_summary_*.csv

# Abrir con Excel/LibreOffice para análisis detallado
```

## Interpretación Rápida

### Archivo: `migration_priority_*.csv`
**Este es el archivo más importante para tomar decisiones**

- Ordena sistemas por prioridad de migración
- Muestra timeline recomendado
- Indica acciones inmediatas

### Niveles de Riesgo

| Color | Nivel | Acción |
|-------|-------|--------|
| 🔴 | HIGH (70-100) | Migrar en 0-3 meses |
| 🟠 | MEDIUM-HIGH (50-69) | Planificar en 3-6 meses |
| 🟡 | MEDIUM (30-49) | Programar en 6-12 meses |
| 🟢 | LOW (0-29) | Sin urgencia (12+ meses) |

## Casos de Uso Comunes

### Escenario 1: Primera Evaluación
```bash
# Evaluar todos los servidores legacy
ansible-playbook -i inventory/hosts.ini playbooks/gather_system_info.yml
python3 scripts/run_assessment.py output/
```

### Escenario 2: Re-evaluación Después de Cambios
```bash
# Re-ejecutar evaluación
python3 scripts/run_assessment.py output/
```

### Escenario 3: Evaluación de Servidores Específicos
```bash
# Limitar a un grupo
ansible-playbook -i inventory/hosts.ini playbooks/gather_system_info.yml --limit legacy_servers
```

## Troubleshooting Rápido

**Error: "No hosts matched"**
- Verificar inventory/hosts.ini está configurado
- Probar conectividad: `ansible all -m ping`

**Error: "Permission denied"**
- Verificar usuario tiene acceso SSH
- Verificar usuario tiene privilegios sudo

**Error: "No system data found"**
- Ejecutar primero: `ansible-playbook playbooks/gather_system_info.yml`
- Verificar archivos JSON en output/

## Próximos Pasos

1. Revisar `migration_priority_*.csv` para identificar servidores críticos
2. Planificar migración basándose en timeline recomendado
3. Revisar `detailed_assessment_*.csv` para problemas específicos
4. Usar `statistics_summary_*.csv` para presentaciones ejecutivas

## Contacto y Soporte

- Issues: https://github.com/rootsan/ansible-migration-assessment/issues
- Documentación completa: README.md
