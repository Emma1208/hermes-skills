#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name('.env'))
key = os.getenv('BINANCE_API_KEY','')
secret = os.getenv('BINANCE_API_SECRET','')
print('KEY len', len(key), 'prefix', key[:4], 'suffix', key[-4:])
print('SECRET len', len(secret), 'prefix', secret[:4], 'suffix', secret[-4:])
