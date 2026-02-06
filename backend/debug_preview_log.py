from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import re

db_path = os.path.join(os.getcwd(), "sql_app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_revisions(drawing_id):
    rows = db.execute(text(f"SELECT revision_no, drawing_date, status FROM drawing_revisions WHERE drawing_id = {drawing_id}")).fetchall()
    return rows

try:
    # Find project ID 
    pid = 8
    
    print("\n| Sl. No | Sheet No | Drawing Title | Sent for Rev A | Sent for Rev 0 | Remarks |")
    print("|---|---|---|---|---|---|")
    
    # Get drawings
    dwgs = db.execute(text(f"SELECT id, drawing_no, description, status FROM drawings WHERE project_id = {pid} LIMIT 20")).fetchall()
    
    for i, d in enumerate(dwgs, 1):
        did, dno, desc, status = d
        revs = get_revisions(did)
        
        rev_a_date = ""
        rev_0_date = ""
        
        # Check revisions
        for r in revs:
            r_no = str(r[0]).upper()
            r_date = str(r[1])
            
            if r_no == "A":
                rev_a_date = r_date
            elif r_no == "0":
                rev_0_date = r_date
                
        print(f"| {i} | {dno} | {desc} | {rev_a_date} | {rev_0_date} | {status} |")

except Exception as e:
    print(f"Error: {e}")
