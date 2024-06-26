Traffic Generator
--
---
En esta documentación se encuentra un ejemplo y demo de como funciona la creación de trafico UDP.

- Ejemplo de creacion manual de un paquete con Scapy en la terminal.

1. Instalar scapy en la terminal``pip install scapy``

2. Instalar ``netifaces`` hay que:
   - Instalar [Microsoft Visual studio Build](https://visualstudio.microsoft.com/es/visual-cpp-build-tools/)
   - Una vez dentro buscar en el apartado de **componentes individuales** y seleccionar `` "C++ CMake tools for Windows" y "C++ ATL para v142 build tools (x86 y x64)"``.
   - Una vez completado la instalación, estalar netifaces: ``pip install netifaces`` o desde el IDE en el apartado de **python interpreter** y al añadir una libreria buscar ``netifaces``

Información de configuración
---
---
- Para ver todos los nombres de las interfaces
En ``Powershell`` como administrador
```
Get-NetAdapter | Format-Table -Property Name, InterfaceDescription, Status, InterfaceGuid
```
**NOTA:** el formato que debe de salir es:
``
{FEEDFACE-C0FF-EEED-BEEF-CAFEF00DF00D}
``

Ejemplo de uso:
``
mac_origen = get_mac_origen("{FEEDFACE-C0FF-EEED-BEEF-CAFEF00DF00D}")
``
- Atributos necesarios para crear el paquete UDP : 
```python
    1. ip_origen(str): dirección IP de origen
    2. ip_destino(str): dirección IP de destino
    3. mac_origen(str): dirección MAC origen
    4. puerto_origen(int): numero de puerto 
    5. puerto_destino(int): numero de puerto destino
    6. mensaje(str): información adicional
    7. vlan_id(int): etiqueta de vlan
    8. prioridad(int): grado de prioridad 802.1Q CoS
```
Ejemplo de uso
---
---
**En TERMINAL**


Ejecutar ``scapy``
```python
scapy
INFO: Can't import PyX. Won't be able to use psdump() or pdfdump().
WARNING: Wireshark is installed, but cannot read manuf !
WARNING: IPython not available. Using standard Python shell instead.
AutoCompletion, History are disabled.
WARNING: On Windows, colors are also disabled

                     aSPY//YASa
             apyyyyCY//////////YCa       |
            sY//////YSpcs  scpCY//Pp     | Welcome to Scapy
 ayp ayyyyyyySCP//Pp           syY//C    | Version 2.5.0
 AYAsAYYYYYYYY///Ps              cY//S   |
         pCCCCY//p          cSSps y//Y   | https://github.com/secdev/scapy
         SPPPP///a          pP///AC//Y   |
              A//A            cyP////C   | Have fun!
              p///Ac            sC///a   |
              P////YCpc           A//A   | We are in France, we say Skappee.
       scccccp///pSP///p          p//Y   | OK? Merci.
      sY/////////y  caa           S//P   |             -- Sebastien Chabal
       cayCyayP//Ya              pY/Ya   |
        sY/PsY////YCc          aC//Yp
         sc  sccaCY//PCypaapyCP//YSs
                  spCPY//////YPSps
                       ccaacs
>>>
```
Creación y envio de un paquete sencillo UDP 
````
>>> dest=IP(dst="172.21.23.27")
>>> protocol = UDP(dport=1024,sport=5076)
>>> payload="Hello World"
>>> paquete = dest/protocol/payload
>>> paquete
<IP  frag=0 proto=udp dst=172.21.23.27 |<UDP  sport=5076 dport=1024 |<Raw  load='Hello World' |>>>
>>> send(paquete)
WARNING: Mac address to reach destination not found. Using broadcast.
.
Sent 1 packets.
>>>
````
En este caso, se ha enviado un paquete UDP con un payload que contiene el mensaje de ```"Hello World"``` a la dirección ``IP : 172.21.23.27``

**NOTA:** con ``nc -vv -u -l -p 1024`` en nuestro servidor linux que tenemos de manera identificable se puede escuchar en el puerto 1024 y se verá el mensaje "Hello World" que se ha enviado a ese puerto.

También lo podremos observar en [Wireshark](https://www.wireshark.org/download.html), si capturamos el trafico dentro de la interfaz de red donde enviamos los paquetes.

**En IDE**

````python
from scapy.layers.inet import IP, UDP
from scapy.all import *

def udpGenerator(ip_origen, mac_origen, ip_destino, puerto_origen, puerto_destino, mensaje, vlan_id, prioridad) :
  
    paquete = Ether(src=mac_origen)

    paquete /= IP(src=ip_origen, dst=ip_destino)

    paquete /= UDP(sport=puerto_origen, dport=puerto_destino)

    paquete /= Dot1Q(vlan=vlan_id, prio=prioridad)

    paquete /= Raw(load=mensaje)
    return paquete

````
Para UDP existe ``0 a 65535`` puertos donde enviar y recibir, aunque hay que tener en cuanta que algunos ya conocidos pueden estar en uso.

Así también saber que para añadir nivel de prioridad según el protocolo 802.1Q solo existen los valores ``0 al 7``, siendo el 7 de mayor prioridad.


