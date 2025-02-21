import socket
import struct
import os

if os.name=='nt':
	# публичный сетевой интерфейс
	HOST = socket.gethostbyname(socket.gethostname())

	# создайте необработанный сокет и свяжите его с публичным интерфейсом
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
	s.bind((HOST, 0))

	# Включить заголовки IP
	s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

	# получать все пакеты
	s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

	while True:
		# получить пакет
		print(s.recvfrom(65565))

	# отключение неразборчивого режима
	s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

else:

	# Функция для разбора Ethernet-фрейма
	def parse_ethernet_frame(frame):
	    dest_mac, src_mac, eth_proto = struct.unpack('!6s6sH', frame[:14])
	    return {
	        'dest_mac': ':'.join(f'{b:02x}' for b in dest_mac),
	        'src_mac': ':'.join(f'{b:02x}' for b in src_mac),
	        'eth_proto': socket.htons(eth_proto),
	        'payload': frame[14:]
	    }

	# Функция для разбора IP-пакета
	def parse_ip_packet(packet):
	    version_and_header_length = packet[0]
	    version = version_and_header_length >> 4
	    header_length = (version_and_header_length & 0xF) * 4
	    ttl, proto, src_ip, dest_ip = struct.unpack('!8xBB2x4s4s', packet[:20])
	    return {
	        'version': version,
	        'header_length': header_length,
	        'ttl': ttl,
	        'proto': proto,
	        'src_ip': socket.inet_ntoa(src_ip),
	        'dest_ip': socket.inet_ntoa(dest_ip),
	        'payload': packet[header_length:]
	    }

	# Функция для разбора TCP-сегмента
	def parse_tcp_segment(segment):
	    src_port, dest_port, seq, ack, offset_flags = struct.unpack('!HHLLH', segment[:14])
	    offset = (offset_flags >> 12) * 4
	    flags = offset_flags & 0x1FF
	    return {
	        'src_port': src_port,
	        'dest_port': dest_port,
	        'seq': seq,
	        'ack': ack,
	        'flags': flags,
	        'payload': segment[offset:]
	    }

	# Основная функция для захвата пакетов
	def sniff_packets(interface):
	    # Создаем raw-сокет
	    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
	    sock.bind((interface, 0))

	    print(f"Starting packet capture on interface {interface}...")

	    try:
	        while True:
	            raw_data, _ = sock.recvfrom(65535)
	            eth_frame = parse_ethernet_frame(raw_data)

	            print(f"\nEthernet Frame:")
	            print(f"  Destination MAC: {eth_frame['dest_mac']}")
	            print(f"  Source MAC: {eth_frame['src_mac']}")
	            print(f"  Protocol: {eth_frame['eth_proto']}")

	            if eth_frame['eth_proto'] == 8:  # IPv4
	                ip_packet = parse_ip_packet(eth_frame['payload'])
	                print(f"  IP Packet:")
	                print(f"    Version: {ip_packet['version']}")
	                print(f"    Header Length: {ip_packet['header_length']}")
	                print(f"    TTL: {ip_packet['ttl']}")
	                print(f"    Protocol: {ip_packet['proto']}")
	                print(f"    Source IP: {ip_packet['src_ip']}")
	                print(f"    Destination IP: {ip_packet['dest_ip']}")

	                if ip_packet['proto'] == 6:  # TCP
	                    tcp_segment = parse_tcp_segment(ip_packet['payload'])
	                    print(f"    TCP Segment:")
	                    print(f"      Source Port: {tcp_segment['src_port']}")
	                    print(f"      Destination Port: {tcp_segment['dest_port']}")
	                    print(f"      Sequence Number: {tcp_segment['seq']}")
	                    print(f"      Acknowledgment Number: {tcp_segment['ack']}")
	                    print(f"      Flags: {tcp_segment['flags']}")
	                    print(f"      Payload: {tcp_segment['payload']}")

	    except KeyboardInterrupt:
	        print("\nPacket capture stopped.")

	if __name__ == "__main__":
	    # Указываем сетевой интерфейс (например, "eth0" или "wlan0")
	    interface = "eth0"
	    sniff_packets(interface)