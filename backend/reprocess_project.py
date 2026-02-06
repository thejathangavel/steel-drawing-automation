import os
import asyncio
from app.services.extraction_service import ExtractionService
from app import crud
from app.db import models
from app.db.database import SessionLocal

# Setup
db = SessionLocal()
extraction_service = ExtractionService()
PROJECT_ID = 8 # From logs

def get_project_files(folder_path):
    pdf_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def update_db(project_id, file_path, metadata):
    filename_only = os.path.basename(file_path)
    if not metadata: return

    # Simplified version of projects.py logic just for revisions
    existing_drawing = db.query(models.Drawing).filter(
        models.Drawing.project_id == project_id,
        models.Drawing.filename == filename_only
    ).first()

    if existing_drawing:
        # print(f"Updating {filename_only}...")
        
        # 2. Process All Revisions
        # First, clear existing revisions? No, "Overwrite" strategy
        # Actually user wants strict rules. If reprocess finds 2 revs (A and 0), but DB has 3, what to do?
        # Safe strategy: Upsert/Update.
        
        all_revs = metadata.get("all_revisions", [])
        if not all_revs:
             return

        # print(f"  > Revisions found: {[r['rev'] for r in all_revs]}")

        for rev_item in all_revs:
            r_no = str(rev_item.get('rev', '')).strip()
            r_date = rev_item.get('date', '')
            r_desc = rev_item.get('desc', '') or metadata.get("remarks", "Active")
            
            if not r_no: continue
            
            # Upsert Revision
            found_r = None
            for r in existing_drawing.revisions:
                if r.revision_no == r_no:
                    found_r = r
                    break
            
            if found_r:
                found_r.drawing_date = r_date
                found_r.status = r_desc
            else:
                # print(f"  + Adding new revision: {r_no}")
                new_rev = models.DrawingRevision(
                    drawing_id=existing_drawing.id,
                    revision_no=r_no,
                    drawing_date=r_date,
                    status=r_desc,
                    filename=filename_only
                )
                db.add(new_rev)
        
        db.commit()

def main():
    project = crud.get_project(db, PROJECT_ID)
    if not project:
        print("Project not found")
        return

    print(f"Reprocessing files for project: {project.title}")
    files = get_project_files(project.folder_path)
    print(f"Found {len(files)} PDFs.")

    for i, f in enumerate(files):
        try:
            meta = extraction_service.extract_metadata(f)
            update_db(PROJECT_ID, f, meta)
            if i % 50 == 0: print(f"Processed {i}/{len(files)}")
        except Exception as e:
            print(f"Error {f}: {e}")

if __name__ == "__main__":
    main()
