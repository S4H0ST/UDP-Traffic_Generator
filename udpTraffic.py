from scapy.all import *
from scapy.layers.inet import IP, UDP  # para la creación de paquetes IP y UDP
from scapy.layers.l2 import Ether, Dot1Q, ARP  # para la creación de paquetes Ethernet y 802.1Q
import netifaces as ni
'''
     ############ ATRIBUTOS #############
   - ip_origen(str): información adicional
   - ip_destino(str): dirección IP de destino
   - mac_origen(str): dirección MAC origen
   - mac_destino(str): dirección MAC destino
   - puerto_origen(int): numero de puerto 
   - puerto_destino(int): numero de puerto destino
   - mensaje(str): información adicional
   - vlan_id(int): etiqueta de vlan
   - prioridad(int): grado de prioridad 802.1Q CoS
'''


def udpGenerator(ip_origen:str, ip_destino:str,mac_origen:str,mac_destino:str, puerto_origen:int, puerto_destino:int, mensaje:str, vlan_id:int, prioridad:int)->Ether:
    '''
    Genera un paquete UDP con la configuración especificada.
    :param ip_origen(str): información adicional
    :param ip_destino(str): dirección IP de destino
    :param mac_origen(str): dirección MAC origen
    :param mac_destino(str): dirección MAC destino
    :param puerto_origen(int): numero de puerto
    :param puerto_destino(int): numero de puerto destino
    :param mensaje(str): información adicional
    :param vlan_id(int): etiqueta de vlan
    :param prioridad(int): grado de prioridad 802.1Q CoS
    :return paquete(Ether): devuelve el paquete creado para enviar
    '''

    ### CABECERA NIVEL 2 ### (Ethernet)
    # Crear el paquete Ethernet con la dirección MAC de origen y destino
    paquete = Ether(src=mac_origen,dst=mac_destino)

    ### CABECERA NIVEL 3 ### (IP)
    # Crear el paquete IP con la dirección IP de origen y destino
    paquete /= IP(src=ip_origen, dst=ip_destino,ihl=5)

    ### ESTABLECER LOS BITS LG y IG ###
    # Convertir la dirección MAC de origen a una cadena de bytes pasandolo a hexadecimal
    mac_origen_bytes = bytes.fromhex(mac_origen.replace(":", ""))

    # Modificar los bits LG e IG
    # El bit LG está en el byte más significativo, el bit IG está en el segundo byte
    mac_origen_bytes = bytes([mac_origen_bytes[0] & 0xFE]) + mac_origen_bytes[1:]

    # Convertir la cadena de bytes de vuelta a la representación de cadena hexadecimal de la dirección MAC
    mac_origen = ":".join(["{:02x}".format(b) for b in mac_origen_bytes])

    # Agregar la dirección MAC de origen modificada al paquete Ethernet
    paquete.src = mac_origen

    ### CABECERA NIVEL 3 ### (UDP)
    # Crear el paquete UDP con los puertos de origen y destino
    paquete_udp  = UDP(sport=puerto_origen, dport=puerto_destino)

    # Calcular el checksum del paquete UDP (si es necesario)
    paquete_udp.chksum = None  # Para que Scapy recalcule automáticamente el checksum
    paquete_udp = paquete_udp.__class__(bytes(paquete_udp))  # Recalcula el checksum

    # Calcular la longitud total del paquete UDP (cabecera UDP + carga útil)
    longitud_udp = len(paquete_udp) + len(mensaje)

    # Establecer la longitud total del paquete UDP en el campo 'len' de la cabecera UDP
    paquete_udp.len = longitud_udp

    # Agregar la cabecera UDP al paquete
    paquete /= paquete_udp

    ### CABECERA NIVEL 2 ### (802.1Q)
    # Agregar la prioridad 802.1Q y la etiqueta VLAN
    paquete /= Dot1Q(vlan=vlan_id, prio=prioridad)

    ### Carga útil (Payload) ###
    # Agregar el payload al paquete
    paquete /= Raw(load=mensaje)

    return paquete
def get_mac_origen(ip_origen: str):
    try:
        # Obtener todas las interfaces de red disponibles
        interfaces = ni.interfaces()
        # Buscar en cada interfaz la dirección MAC asociada a la IP objetivo
        for interfaz in interfaces:
            direcciones = ni.ifaddresses(interfaz).get(ni.AF_INET)

            if direcciones:
                for direccion in direcciones:
                    if direccion['addr'] == ip_origen:
                        # Si la IP objetivo se encuentra en esta interfaz, devolver la dirección MAC asociada
                        return ni.ifaddresses(interfaz)[ni.AF_LINK][0]['addr']
        # Si no se encuentra la IP en ninguna interfaz, devolver None
        return None
    except Exception as e:
        print("Error al obtener la dirección MAC:", e)
        return None

def get_mac_destino(ip: str)-> str or None:
    """
    Obtiene la dirección MAC asociada a una dirección IP mediante la realización de una solicitud ARP.
    :param ip(str): La dirección IP de destino.
    :return mac(str) or None: La dirección MAC asociada a la dirección IP especificada, o None si no se pudo obtener.
    """
    resp, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, retry=10)
    for s, r in resp:
        return r[Ether].src
    return None

def get_mac_gateway()->str or None:
    """
    Obtiene la dirección MAC asociada al gateway predeterminado de la red.
    :return mac(str) or None: La dirección MAC asociada al gateway predeterminado, o None si no se pudo obtener.
        """
    try:
        gws = ni.gateways()
        gateway_ip = gws['default'][ni.AF_INET][0]
        return get_mac_destino(gateway_ip)  # Llama a la función get_mac_destino con la dirección IP del gateway
    except Exception as e:
        print("Error al obtener la dirección MAC del gateway:", e)
        return None

def send_package(paquete:Ether)->None:
    sendp(paquete)

def get_interfaces_and_Ips():
    """
    Obtiene las interfaces de red y las direcciones IP asignadas a cada interfaz.

   :return
        dict: Un diccionario donde las claves son los nombres de las interfaces de red
        y los valores son listas de las direcciones IP asignadas a cada interfaz.
        None si ocurre un error.
    """
    try:
        # Obtener información detallada de todas las interfaces de red
        interfaces_info = ni.interfaces()
        # Crear un diccionario para almacenar las interfaces y las IPs asociadas a cada una
        interfaces_ips = {}
        # Recorrer la información de cada interfaz y obtener las direcciones IP asociadas
        for interfaz in interfaces_info:
            info = ni.ifaddresses(interfaz).get(ni.AF_INET)
            if info:
                ips = [direccion['addr'] for direccion in info]
                interfaces_ips[interfaz] = ips
        return interfaces_ips
    except Exception as e:
        print("Error al obtener las interfaces y direcciones IP:", e)
        return None