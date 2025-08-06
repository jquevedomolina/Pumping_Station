# Configuración de Despliegue para ceb.dev

Esta guía explica cómo configurar el despliegue de la aplicación en el dominio `ceb.dev`.

## Requisitos Previos

1. Servidor con Docker y Docker Compose instalados
2. Acceso al panel de control de tu proveedor de DNS
3. Puerto 80 y 443 abiertos en tu firewall

## Configuración de DNS

1. Configura un registro A en tu DNS que apunte a la IP de tu servidor:
   ```
   ceb.dev.    A     TU_IP_DEL_SERVIDOR
   www.ceb.dev. CNAME ceb.dev.
   ```

2. (Opcional) Para desarrollo local, puedes editar tu archivo `/etc/hosts`:
   ```
   127.0.0.1    ceb.dev
   ```

## Configuración del Servidor

1. Asegúrate de que los puertos 80 y 443 estén abiertos en tu firewall:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

2. Crea los directorios necesarios para los certificados:
   ```bash
   mkdir -p certs vhost.d acme
   chmod 600 certs
   ```

## Despliegue con Docker Compose

1. Edita el archivo `docker-compose.yml` y actualiza las siguientes variables:
   - `LETSENCRYPT_EMAIL`: Tu correo electrónico para notificaciones de Let's Encrypt
   - `VIRTUAL_HOST` y `LETSENCRYPT_HOST`: Asegúrate de que coincidan con tu dominio

2. Inicia los servicios:
   ```bash
   docker-compose up -d
   ```

3. Verifica los logs para asegurarte de que todo funcione correctamente:
   ```bash
   docker-compose logs -f
   ```

## Renovación Automática de Certificados

Los certificados SSL se renovarán automáticamente gracias al contenedor `letsencrypt-nginx-proxy`. No es necesaria ninguna acción adicional.

## Monitoreo

Puedes verificar el estado de tus certificados con:
```bash
docker exec nginx-proxy-acme acme.sh --list
```

## Solución de Problemas

### Error de "Demasiados registros"
Si ves un error de "too many registrations", espera 1 hora o usa un correo diferente.

### Certificado no generado
Verifica que:
1. El dominio apunte correctamente a la IP del servidor
2. Los puertos 80 y 443 estén abiertos
3. No haya otros servicios usando estos puertos

### Renovar manualmente
Para forzar la renovación de un certificado:
```bash
docker exec nginx-proxy-acme acme.sh --issue -d ceb.dev --force
```

## Seguridad Adicional

1. **Actualizaciones de Seguridad**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

2. **Copias de Seguridad**:
   - Haz backup regular de los directorios `certs/` y `acme/`
   - Considera usar volúmenes nombrados para producción

3. **Monitoreo**:
   Configura un servicio de monitoreo para verificar que los certificados se renueven correctamente.
