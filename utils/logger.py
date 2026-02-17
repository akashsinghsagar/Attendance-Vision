"""
logger.py
Simple error logging utility.
"""
import logging
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.log')

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def log_error(msg):
    logging.error(msg)

def log_info(msg):
    logging.info(msg)
