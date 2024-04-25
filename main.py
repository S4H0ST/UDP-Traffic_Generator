from udpTraffic import udpGenerator, send_package, get_mac_origen, get_mac_destino, get_mac_gateway, get_interfaces_and_Ips
import netifaces as ni

def main(ip_origen:str, ip_destino:str):
    # Especificaciones del paquete

      # ejemplo
    puerto_origen = 5076
    puerto_destino = 1024
    a = 0
    vlan_id = 0
    prioridad = 5


    # Obtener mac del origen
    mac_origen = get_mac_origen(ip_origen)  # cambiar interfaz
    # Obtener mac del destino
    mac_destino = get_mac_destino(ip_destino) or get_mac_gateway()

    while (a!=2): #envia 9 paquetes
     mensaje = f"paquetito numero{a} llegó"
     # Crear el paquete Ethernet
     paquete_ether = udpGenerator(ip_origen, ip_destino, mac_origen, mac_destino, puerto_origen, puerto_destino, mensaje,vlan_id, prioridad)
     # Mostrar la representación del paquete
     print(paquete_ether.show())
     # Enviar el paquete
     send_package(paquete_ether)
     a+=1

def menu():
    print("Mostrando todas las interfaces disponibles ...")
    resultado = get_interfaces_and_Ips()
    if resultado:
        for interfaz, ips in resultado.items():
            print(f"Interfaz: {interfaz}, IPs asignadas: {ips}")
    else:
        print("No se pudo obtener la información de las interfaces y direcciones IP.")

    origen = input("Elige la IP desde donde se va a mandar el paquete : ")
    destino = input("Elige la IP a donde se va a llegar el paquete : ")
    main(origen,destino)


# Ejecuta la función main
if __name__ == "__main__":
    menu()
