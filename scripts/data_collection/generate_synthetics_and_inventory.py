# -*- coding: utf-8 -*-
import os, csv, hashlib, random
import pandas as pd, numpy as np
from datetime import datetime, timedelta
PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW_BRAZIL = os.path.join(PROJECT_ROOT, "data", "raw", "brazilian_ecommerce"
