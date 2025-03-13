import socket
import struct
import time

# NTP parameters
NTP_PORT = 123
NTP_VERSION = 4
TIME1970 = 2208988800  # Offset for Unix time -> NTP time


def get_ip_address():
    """Get the local IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "Unknown"
    

def ntp_server():
    """Start the NTP server and listen for incoming requests."""
    
    # Get local IP addresses
    wifi_ip = get_ip_address()

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", NTP_PORT))  # Listen on all network interfaces

    print("NTP Server Started")
    print(f"Listening on UDP port {NTP_PORT}")
    print(f"Wi-Fi IP Address: {wifi_ip}")
    print("\nTo test from another device, run:")
    print(f"   ➜ `ntpdate -d {wifi_ip}`  (Linux/macOS)")

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Receive NTP request
            print(f"Received NTP request from {addr}")

            if len(data) < 48:  # Ignore invalid requests
                print("❌ Invalid request (too short). Ignoring.")
                continue

            # Unpack the incoming request
            unpacked_data = struct.unpack("!12I", data)

            # Set response flags (LI=0, VN=4, Mode=4)
            LI_VN_MODE = (0 << 6) | (NTP_VERSION << 3) | 4

            # The client’s Transmit Timestamp is at words 11 & 12:
            client_tx_s = unpacked_data[10]
            client_tx_f = unpacked_data[11]

            curr_time = int(time.time() + TIME1970)
            frac_time = int((time.time() % 1) * 2**32)

            response = struct.pack(
                "!BBBbIII8I",
                LI_VN_MODE,
                1,    # Stratum
                0,    # Poll
                -20,  # Precision
                0,    # Root Delay
                0,    # Root Dispersion
                0,    # Reference ID
                curr_time, frac_time,         # Reference
                client_tx_s, client_tx_f,     # Originate Timestamp
                curr_time, frac_time,         # Receive Timestamp
                curr_time, frac_time          # Transmit Timestamp
            )

            sock.sendto(response, addr)  # Send response
            print(f"✅ Sent NTP response to {addr}")

        except KeyboardInterrupt:
            print("\n🛑 NTP Server Stopped.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")


ntp_server()