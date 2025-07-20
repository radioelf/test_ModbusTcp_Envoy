El script realiza dos tipos de lecturas:
1. Lectura inicial del bloque SunSpec

    Se ejecuta solo una vez al iniciar
    Lee los registros 40000-40048
    Decodifica información del dispositivo como:
        ID de SunSpec (confirma que es un dispositivo SunSpec)
        Modelo ID (1 = SunSpec Common Model)
        Longitud del modelo (66 registros)
        Información del fabricante ("ENPHASE ENERGY")
        Modelo del dispositivo ("Envoy")
        versión de firmware

2. Monitoreo continuo de mediciones

    Se ejecuta en bucle cada 5 segundos
    Lee los registros 40070-40096
    Extrae valores como (NO verificado):
        Potencia de prodicción fotovoltaica (40080)
        Potencia aparente forovoltaica (40081)
        Potencia reactiva fotovoltaica (40082)
        Factor de potencia (40083)
        Corriente (40084)
        Tensión de red (40086)
        Frecuencia (40088)
        Producción total fotovoltaica (40091 y 40092)
        Tipo de instalación electrica (40096)
        Otros registros desconocidos (40072, 40073, etc.)

Limitaciones y notas

    El código está optimizado para mi Envoy --SOLO para TEST--
    Los registros no están documentados por Enphase y pueden requerir interpretación adicional
    Asegúrate de que el Modbus TCP esté habilitado en tu Envoy antes de usar este script
    https://enphase.com/en-gb/download/ac-coupling-victron-battery-inverters-using-modbus-tcpip-tech-brief

Licencia

Creative Commons License Disclaimer

UNLESS OTHERWISE MUTUALLY AGREED TO BY THE PARTIES IN WRITING, LICENSOR OFFERS THE WORK AS-IS AND MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE WORK, EXPRESS, IMPLIED, STATUTORY OR OTHERWISE, INCLUDING, WITHOUT LIMITATION, WARRANTIES OF TITLE, MERCHANTIBILITY, FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER DEFECTS, ACCURACY, OR THE PRESENCE OF ABSENCE OF ERRORS, WHETHER OR NOT DISCOVERABLE. SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF IMPLIED WARRANTIES, SO SUCH EXCLUSION MAY NOT APPLY TO YOU. EXCEPT TO THE EXTENT REQUIRED BY APPLICABLE LAW, IN NO EVENT WILL LICENSOR BE LIABLE TO YOU ON ANY LEGAL THEORY FOR ANY SPECIAL, INCIDENTAL, CONSEQUENTIAL, PUNITIVE OR EXEMPLARY DAMAGES ARISING OUT OF THIS LICENSE OR THE USE OF THE WORK, EVEN IF LICENSOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

http://creativecommons.org/licenses/by-sa/3.0/
