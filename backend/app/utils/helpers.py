"""General helper utilities"""
from datetime import datetime

def compute_age(birthdate):
    today = datetime.utcnow().date()
    return (today - birthdate).days // 365
