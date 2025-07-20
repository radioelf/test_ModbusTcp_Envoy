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
            log_message("🔌 Conexión SunSpec cerrada\n")
    else:
        log_message("⛔ Fallo conexión SunSpec")
        return False

# --- Función para leer registros de medición ---
def read_measurements():
    high_word_id = None
    low_word_id = None
    valor_32 = None
    client = ModbusTcpClient(host=ip, port=port)
    if client.connect():
        log_message("✅ Conectado para mediciones")
        try:
            start = 40070
            count = 27  # 40070-40096
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
                    
                    # Bloque de lectura de registros
                    if current_address == 40070:
                        high_word_id = val
                    elif current_address == 40071:
                        low_word_id = val
                    # Combinar las dos partes para obtener el ID completo
                    if high_word_id is not None and low_word_id is not None:
                    # Desplazar la parte alta 16 bits a la izquierda y combinar con la parte baja
                       valor_32 = (high_word_id << 16) | low_word_id
                       log_message(f"✨ ID del Modelo SunSpec Combinado: {valor_32}")
                       high_word_id = None
                       low_word_id = None
                       
                    # Potencia solar (40080)
                    elif current_address == 40080:
                        log_message(f"🔹 Potencia solar: {val} W (40080)")
                    
                    # Potencia aparente solar (40081)
                    elif current_address == 40081:
                        log_message(f"🔹 Potencia aparente solar: {val} VA (40081)")  
                    
                    # Potencia reactiva solar (40082)
                    elif current_address == 40082:
                        log_message(f"🔹 Potencia reactiva solar: {val} VA (40082)")   
                        
                    # Factor de potencia (40083)
                    elif current_address == 40083:
                        current = val / 100.0
                        log_message(f"🔹 Factor potencia: {current} Fp (40083)")
                        
                    # Intensidad solar (40084
                    elif current_address == 40084:
                        current = val / 100.0
                        log_message(f"🔹 Corriente solar: {current} A (40084)")
                    
                    # Tensión fotovoltaica (40086)
                    elif current_address == 40086:
                        voltage = val / 100.0
                        log_message(f"🔹 Tensión de Red: {voltage:.2f} V (40086)")

                    # Frecuencia (40088)
                    elif current_address == 40088:
                        frequency = val / 100.0
                        log_message(f"🔹 Frecuencia: {frequency:.2f} Hz (40088)")

                    # Total producción solar
                    if current_address == 40091:
                        high_word_id = val
                    elif current_address == 40092:
                        low_word_id = val
                    # Combinar las dos partes para obtener el ID completo
                    if high_word_id is not None and low_word_id is not None:
                    # Desplazar la parte alta 16 bits a la izquierda y combinar con la parte baja y dividir por 1000000
                       valor_32 = ((high_word_id << 16) | low_word_id) / 1000000
                       log_message(f"🔹 Total producción : {valor_32} Mwh (40091, 40092)")
                       high_word_id = None
                       low_word_id = None
                    
                    # Tipo de conexión eléctrica(40096)
                    elif current_address == 40096:
                        if val == 111:
                           log_message(f"🔹 Una fase activa + neutro (40096)")
                        elif val == 112:
                           log_message(f"🔹Dos fases opuestas de 120°(40096)")
                        elif val == 113:
                            log_message(f"🔹 Trifásico (40096)")
                    
                    # Otros registros desconocidos
                    elif current_address in [40072, 40073, 40074, 40075, 40076, 40077, 40078, 40079, 40085, 40087, 40089, 40090, 40093, 40094, 40095]:
                        if val not in [0, 32768, 65534, 65535]:
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
            log_message("🔌 Conexión mediciones cerrada\n")
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
