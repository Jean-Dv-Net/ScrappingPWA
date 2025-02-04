# logging_config.py
import logging

def setup_logger(name: str = None, log_file="logs/logging.log", level=logging.INFO):
    """
    Configura un logger con los parámetros dados.

    :param name: Nombre del logger. Si es None, se usará el root logger.
    :param log_file: Archivo donde se guardarán los logs.
    :param level: Nivel de logging (INFO, DEBUG, etc.).
    :return: Instancia del logger configurado.
    """
    # Formato de los mensajes de log
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(name)s - %(message)s")
    
    # Configuración del handler de archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Configuración del handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Creación y configuración del logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger