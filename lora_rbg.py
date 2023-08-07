import serial
import time
import codecs
from PIL import Image

serial_port = "/dev/ttyUSB0"
baud_rate = 115200

#Radio set up
freq = 915
mod = "SF9"
band_width = 125
tx_pr = 8
rx_pr = 8
power = 22

#RF configuration string
rf_conf_str = "AT+TEST=RFCFG,{},{},{},{},{},{},OFF,OFF,OFF\n".format(freq, mod, band_width, tx_pr, rx_pr, power)

#Serial Objet
ser = serial.Serial(serial_port,baud_rate)


def initialize_radio(): #Test PASSED
    ser.write("AT+MODE=TEST\n".encode())
    time.sleep(0.5)
    print(ser.readline().decode())
    time.sleep(0.5)
    ser.write(rf_conf_str.encode())
    print(ser.readline().decode())

def send_msg(message):
    ser.write("AT+TEST=TXLRPKT,\"{}\"\n".format(message).encode())
    print(ser.readline().decode())
    
def chr_to_hex(string):
    return codecs.encode(string.encode(),'hex').decode()

def hex_to_chr(string):
    return codecs.decode(string, 'hex').decode()

def itp_rbg(image_path, packet_size):
    # Leer la imagen
    image = Image.open(image_path)

    # Redimensionar la imagen
    new_width = 64
    new_height = 64
    image = image.resize((new_width, new_height))

    # Obtener los canales de color de la imagen
    red, green, blue = image.split()

    # Obtener los bytes de cada canal de color
    red_bytes = red.tobytes()
    green_bytes = green.tobytes()
    blue_bytes = blue.tobytes()

    # Dividir cada canal de color en paquetes
    red_packets = split_bytes_into_packets(red_bytes, packet_size)
    green_packets = split_bytes_into_packets(green_bytes, packet_size)
    blue_packets = split_bytes_into_packets(blue_bytes, packet_size)

    # Retornar los paquetes de cada canal de color
    return red_packets, green_packets, blue_packets


def split_bytes_into_packets(data_bytes, packet_size):
    packets = []
    total_bytes = len(data_bytes)
    num_packets = total_bytes // packet_size + 1

    for packet_num in range(num_packets):
        start_index = packet_num * packet_size
        end_index = start_index + packet_size
        packet_data = data_bytes[start_index:end_index]
        packets.append(packet_data)

    return packets

#paquetes, puerto, bits por segundo, time [s]
def send_image_packets_to_lora(red_packets, green_packets, blue_packets):
    # Reiniciar el módulo LoRa?
    # Enviar los datos de los paquetes 
    #TODO: pasar mejor un objteto que tenga los packetes que tengan que ser y implementar una interfaz de send packetsi
    for red in red_packets:
        data=str(red)
        print("enviando el dato:",data)
        send_msg(chr_to_hex(data))
        time.sleep(0.5)
    send_msg(chr_to_hex("|||||"))
    time.sleep(0.5)
    
    for green in green_packets:
        data=str(green)
        print("enviando el dato", data)
        send_msg(chr_to_hex(data))
        time.sleep(0.5)
    send_msg(chr_to_hex("|||||"))
    time.sleep(0.5)
    
    for blue in blue_packets:
        data=str(blue)
        print("Enviando el dato", data)
        send_msg(chr_to_hex(data))
        time.sleep(0.5)

initialize_radio()
time.sleep(1)

red_packets, green_packets, blue_packets = itp_rbg('test_camera.jpg',20)
send_image_packets_to_lora(red_packets, green_packets, blue_packets)
