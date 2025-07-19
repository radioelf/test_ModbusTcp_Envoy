# Enphase activa la función Modbus TCP/IP de solo lectura en el rango 700 ??
# https://enphase.com/en-gb/download/ac-coupling-victron-battery-inverters-using-modbus-tcpip-tech-brief
# Test de lectura de registros Modbus TCP del Envoy de Enphase
# Hay registros que se desconocen y puede haber errores, ya que no he encontrado ninguna información.....

from pymodbus.client import ModbusTcpClient
import time
import datetime
import os

# --- Configuración del Modbus ---
ip = "192.168.x.xxx" # dirección del Envoy
port = 502
unit_id = 126  # Modbus Unit ID del Envoy

# --- Configuración de Logging ---
log_filename = "enphase_modbus.log"
log_directory = "logs"
log_filepath = os.path.join(log_directory, log_filename)
os.makedirs(log_directory, exist_ok=True)

def log_message(message, print_to_console=True):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    with open(log_filepath, "a") as log_file:
        log_file.write(log_entry + "\n")
    if print_to_console:
        print(log_entry)

# --- Función para leer y decodificar el bloque SunSpec ---
def read_sunspec_block():
    client = ModbusTcpClient(host=ip, port=port)
    if client.connect():
        log_message("✅ Conectado para lectura SunSpec")
        try:
            start = 40000
            count = 49  # Cubre hasta 40048
            log_message(f"📋 Leyendo bloque SunSpec: {count} registros desde {start}...")
            
            response = client.read_holding_registers(address=start, count=count, slave=unit_id)
            
            if not response.isError():
                registers = response.registers
                log_message(f"✅ Leídos {len(registers)} registros SunSpec")
                log_message("-" * 70, print_to_console=False)
                
                # Decodificación SunSpec ID (40000-40001)
                if len(registers) >= 2:
                    combined = (registers[0] << 16) | registers[1]
                    bytes_id = [(combined >> 24) & 0xFF, 
                               (combined >> 16) & 0xFF,
                               (combined >> 8) & 0xFF, 
                               combined & 0xFF]
                    sunspec_id = ''.join(chr(b) for b in bytes_id)
                    log_message(f"🔹 SunSpec ID: {sunspec_id} (40000-40001)")
                
                # Modelo ID (40002)
                if len(registers) >= 3:
                    log_message(f"🔹 Modelo ID: {registers[2]} (40002)")
                
                # Longitud del modelo (40003)
                if len(registers) >= 4:
                    log_message(f"🔹 Longitud del modelo: {registers[3]} (40003)")
                
                # Fabricante (40004-40010)
                if len(registers) >= 11:
                    manufacturer_bytes = []
                    for i in range(7):
                        word = registers[4 + i]
                        manufacturer_bytes.append((word >> 8) & 0xFF)
                        manufacturer_bytes.append(word & 0xFF)
                    manufacturer = bytes(manufacturer_bytes).decode('ascii').split('\x00')[0]
                    log_message(f"🔹 Fabricante: {manufacturer} (40004-40010)")
                
                # Modelo (40020-40022)
                if len(registers) >= 23:
                    model_bytes = []
                    for i in range(3):
                        word = registers[20 + i]
                        model_bytes.append((word >> 8) & 0xFF)
                        model_bytes.append(word & 0xFF)
                    model = bytes(model_bytes).decode('ascii').split('\x00')[0]
                    log_message(f"🔹 Modelo: {model} (40020-40022)")
                
                # Número de Serie (40044-40048)
                if len(registers) >= 49:
                    serial_bytes = []
                    for i in range(5):
                        word = registers[44 + i]
                        serial_bytes.append((word >> 8) & 0xFF)
                        serial_bytes.append(word & 0xFF)
                    serial = bytes(serial_bytes).decode('ascii').split('\x00')[0]
                    log_message(f"🔹 Versión Envoy: {serial} (40044-40048)")
                
                log_message("-" * 70, print_to_console=False)
                return True
            else:
                log_message(f"⛔ Error SunSpec: {response}")
                return False
        except Exception as e:
            log_message(f"⛔ Excepción SunSpec: {str(e)}")
            return False
        finally:
            client.close()
            log_message("\n🔌 Conexión SunSpec cerrada")
    else:
        log_message("⛔ Fallo conexión SunSpec")
        return False

# --- Función para leer registros de medición ---
def read_measurements():
    client = ModbusTcpClient(host=ip, port=port)
    if client.connect():
        log_message("✅ Conectado para mediciones")
        try:
            start = 40070
            count = 21  # 40070-40090
            log_message(f"📋 Leyendo {count} registros de medición desde {start}...")
            
            response = client.read_holding_registers(address=start, count=count, slave=unit_id)
            
            if not response.isError():
                registers = response.registers
                log_message(f"✅ Leídos {len(registers)} registros de medición")
                log_message("-" * 70, print_to_console=False)
                log_message("--- Valores de Medición ---")
                
                energy_total = None
                voltage = None
                frequency = None
                
                for i, val in enumerate(registers):
                    current_address = start + i
                    
                    # Producción solar
                    if current_address == 40080:
                        log_message(f"🔹 Producción solar: {val} W")
                    
                    # Tensión de red (40086)
                    elif current_address == 40086:
                        voltage = val / 100.0
                        log_message(f"🔹 Tensión de Red: {voltage:.2f} V (40086)")
                    
                    # Frecuencia (40088)
                    elif current_address == 40088:
                        frequency = val / 100.0
                        log_message(f"🔹 Frecuencia: {frequency:.2f} Hz (40088)")
                    
                    # Otros registros relevantes
                    elif current_address in [40070, 40071, 40081, 40082, 40084, 40091, 40092, 40096]:
                        log_message(f"🔹 Registro {current_address}: {val}")
                
                log_message("-" * 70, print_to_console=False)
                return True
            else:
                log_message(f"⛔ Error mediciones: {response}")
                return False
        except Exception as e:
            log_message(f"⛔ Excepción mediciones: {str(e)}")
            return False
        finally:
            client.close()
            log_message("\n🔌 Conexión mediciones cerrada")
    else:
        log_message("⛔ Fallo conexión mediciones")
        return False

# --- Inicialización: Leer SunSpec una sola vez ---
log_message("🚀 Inicialización - Leyendo bloque SunSpec...")
if not read_sunspec_block():
    log_message("⚠️ Advertencia: Fallo en lectura SunSpec. Continuando...")

# --- Bucle principal de monitoreo ---
log_message("🔄 Iniciando monitoreo de mediciones...")
while True:
    read_measurements()
    log_message("😴 Esperando 5 segundos...")
    time.sleep(5)
