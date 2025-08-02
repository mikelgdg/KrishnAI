# Memoria del Proyecto KrishnAI - Desarrollo y Migración

## Resumen Ejecutivo

Este documento detalla el proceso de desarrollo y migración de KrishnAI, una aplicación que permite dialogar con una IA que simula ser Krishna del Bhagavad Gita. El proyecto ha evolucionado desde una aplicación Python con Streamlit hasta una aplicación móvil React Native con Expo, manteniendo la misma funcionalidad central pero adaptada a dispositivos móviles.

## Objetivos Completados

1. **Limpieza de Archivos Innecesarios**
   - Eliminación de archivos backend innecesarios
   - Optimización de la estructura de carpetas

2. **Migración de SDK de Expo**
   - Actualización del proyecto de SDK 51 a SDK 53
   - Creación de un nuevo proyecto con la versión correcta del SDK
   - Configuración adecuada de metro.config.js para reducir problemas de recursos

3. **Implementación del Núcleo Funcional**
   - Creación del componente principal App.tsx con interfaz de chat
   - Implementación del servicio de API de Gemini en src/api/gemini.ts
   - Sistema de rotación de claves API
   - Manejo de historial de conversación para contexto

4. **Diseño de Interfaz de Usuario**
   - Interfaz tipo ChatGPT con diseño minimalista
   - Sidebar colapsable para configuración
   - Sistema de burbujas de mensajes con iconos distintivos
   - Paleta de colores en tonos grises

5. **Características Avanzadas**
   - Detección de género para adaptar respuestas
   - Manejo de historial para proveer contexto a la IA
   - Sistema de prohibición de repetición de versos
   - Estructura optimizada del prompt para respuestas consistentes

## Detalles Técnicos

### Estructura del Proyecto

```
KrishnAI_Mobile_New/
├── App.tsx               # Componente principal de la aplicación
├── app.json              # Configuración de Expo
├── assets/               # Recursos estáticos (imágenes)
├── babel.config.js       # Configuración de Babel
├── metro.config.js       # Configuración del bundler Metro
├── package.json          # Dependencias y scripts
├── src/
│   └── api/
│       └── gemini.ts     # Servicios para interactuar con Gemini API
└── tsconfig.json         # Configuración de TypeScript
```

### Tecnologías Utilizadas

- **Frontend**: React Native, Expo SDK 53
- **IA**: Google Generative AI (Gemini 1.5 Flash)
- **Lenguaje**: TypeScript
- **Estilo**: StyleSheet de React Native
- **Bundler**: Metro

### Funcionamiento Principal

1. El usuario escribe un mensaje en la interfaz
2. La aplicación envía el mensaje a la API de Gemini junto con:
   - Nombre del usuario (y género detectado)
   - Historial reciente de la conversación (últimos 6 mensajes)
3. El prompt construido instruye a Gemini para responder como Krishna
4. La respuesta se muestra en la interfaz con formato apropiado
5. El historial se actualiza para futuras consultas

## Análisis de Estructura Actual

### Aplicación Streamlit (Python)

La versión original en Python tiene una estructura bien definida:

1. **Componentes principales**:
   - `app.py`: Punto de entrada, interfaz Streamlit
   - `rotacion_claves.py`: Sistema de rotación de claves API
   - `procesado.py`: Procesamiento del texto del Bhagavad Gita
   - `base_textos.json`: Almacenamiento de textos procesados

2. **Funcionalidades clave**:
   - Carga y procesamiento del Bhagavad Gita
   - Construcción avanzada del prompt con versos contextuales
   - Sistema anti-repetición de versos
   - Detección de género del usuario
   - Interfaz con sidebar configurable

### Aplicación React Native (Actual)

La versión móvil ha implementado:

1. **Componentes principales**:
   - `App.tsx`: Interfaz principal y lógica de la aplicación
   - `src/api/gemini.ts`: Cliente para la API de Gemini

2. **Funcionalidades implementadas**:
   - Interfaz de chat estilo ChatGPT
   - Sistema de rotación de claves API
   - Manejo básico del historial de conversación
   - Detección de género del usuario

3. **Funcionalidades pendientes**:
   - Carga y procesamiento del Bhagavad Gita completo
   - Sistema avanzado anti-repetición de versos
   - Optimización de prompts con versos contextuales

## Próximos Pasos Potenciales

### Prioridad Alta

1. **Integración Completa del Bhagavad Gita**
   - Crear una estructura de datos optimizada para móvil
   - Implementar un sistema de carga eficiente de los versos
   - Convertir el formato JSON del Bhagavad Gita a un formato más liviano

2. **Sistema Anti-repetición de Versos**
   - Adaptar la funcionalidad `extraer_versos_citados_del_historial` a TypeScript
   - Implementar el sistema de prohibición de versos ya mencionados
   - Mejorar la estructura del prompt para evitar repeticiones

3. **Optimización de Rendimiento**
   - Reducir el tamaño del prompt manteniendo la calidad de respuestas
   - Implementar caché local para versos frecuentemente utilizados
   - Optimizar el manejo de memoria para dispositivos de baja gama

### Prioridad Media

1. **Mejoras de UX/UI**
   - Añadir animaciones para transiciones más fluidas
   - Implementar modo oscuro/claro
   - Mejorar accesibilidad para usuarios con discapacidades

2. **Características Adicionales**
   - Búsqueda de versos específicos
   - Guardado de conversaciones favoritas
   - Compartir fragmentos de la conversación
   - Ajustes de personalidad (tono más formal/informal)

3. **Internacionalización**
   - Soporte para múltiples idiomas
   - Adaptación de prompts según contexto cultural

### Prioridad Baja

1. **Características Avanzadas**
   - Modo sin conexión con modelo local más pequeño
   - Integración con asistentes de voz
   - Notificaciones diarias con versos recomendados

2. **Expansión de Contenido**
   - Integrar otros textos sagrados relacionados
   - Añadir referencias cruzadas y explicaciones

## Conclusión

El proyecto KrishnAI ha evolucionado exitosamente de una aplicación web Python a una aplicación móvil React Native, manteniendo su esencia y funcionalidad principal. La migración ha permitido que la experiencia del usuario sea más accesible en dispositivos móviles, con una interfaz moderna y responsiva.

Los próximos pasos se centran en completar la integración del sistema de procesamiento avanzado del Bhagavad Gita y mejorar la experiencia del usuario con características adicionales. La arquitectura actual proporciona una base sólida para estas mejoras futuras.
