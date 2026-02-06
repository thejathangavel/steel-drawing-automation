from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from .. import crud, schemas
from ..db import models
from ..db.database import get_db
from ..db.mongodb import get_database
from ..services.extraction_parser import PDFParser
# ...
router = APIRouter()

PROJECTS_DIR = "d:/steel/storage" # Configure this in settings ideally

from pymongo import MongoClient
from ..db.mongodb import db as mongo_config

import logging
logger = logging.getLogger("uvicorn")

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating project: {project.title}")
        
        # Create folder on disk
        project_slug = project.title.replace(" ", "_").lower()
        folder_path = os.path.join(PROJECTS_DIR, project_slug)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.makedirs(os.path.join(folder_path, "drawings"))
        
        new_project = crud.create_project(db=db, project=project, folder_path=folder_path)
        logger.info(f"Project created in SQLite with ID: {new_project.id}")
        
        # Save to MongoDB (Synchronous)
        try:
            client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
            mongo_db = client[mongo_config.db_name]
            # Test connection
            client.admin.command('ping')
            
            mongo_db.projects.insert_one({
                "sql_id": new_project.id,
                "title": new_project.title,
                "client_name": new_project.client_name,
                "created_at": new_project.created_at,
                "folder_path": new_project.folder_path,
                "drawings": []
            })
            client.close()
            logger.info(f"Project '{new_project.title}' saved to MongoDB")
        except Exception as e:
            logger.error(f"Failed to save to MongoDB: {e}")
            # Continue - do not fail the request

        return new_project

    except Exception as e:
        logger.error(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@router.get("/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

from fastapi import File, UploadFile
from typing import List
import shutil
from ..services.extraction_service import ExtractionService
from ..services.excel_manager import ExcelManager

extraction_service = ExtractionService()
excel_manager = ExcelManager()

@router.post("/{project_id}/upload")
async def upload_files(
    project_id: int, 
    files: List[UploadFile] = File(...), 
    is_last_batch: bool = True,
    db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    drawings_dir = os.path.join(project.folder_path, "drawings")
    extracted_data = []

    try:
        if not os.path.exists(drawings_dir):
            os.makedirs(drawings_dir)

        logger.info(f"Received {len(files)} files for upload to project {project_id}")
        
        # --- Phase 1: Save Files (IO Bound) ---
        saved_files = []
        for file in files:
            # We can now handle PDF and eventually DXF if we allow the extension
            if file.filename.lower().endswith((".pdf", ".dxf")):
                # 1. Determine relative path and filename
                # If uploaded via webkitdirectory, filename contains path: "Parent/Sub/file.pdf"
                rel_path = file.filename.replace("\\", "/") # Normalize to forward slash
                filename_only = os.path.basename(rel_path)
                
                # 2. Determine Subfolder & Drawing Type from Path
                subfolder = "drawings" # Default flat structure
                manual_drawing_type = None
                
                parts = rel_path.split("/")
                if len(parts) > 1:
                    # Check parent folders for keywords
                    for part in parts[:-1]: # Exclude filename
                        upper_part = part.upper()
                        if "SHOP" in upper_part:
                            manual_drawing_type = models.DrawingType.SHOP
                            subfolder = "Shop Drawings"
                            break
                        elif "PART" in upper_part:
                            manual_drawing_type = models.DrawingType.PART
                            subfolder = "Part Drawings"
                            break
                        elif "ERECTION" in upper_part:
                            manual_drawing_type = models.DrawingType.ERECTION
                            subfolder = "Erection Drawings"
                            break
                
                # 3. Create Target Directory
                target_dir = os.path.join(project.folder_path, "drawings", subfolder) if subfolder != "drawings" else drawings_dir
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    
                file_location = os.path.join(target_dir, filename_only)
                
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(file.file, file_object)
                
                saved_files.append({
                    "path": file_location,
                    "filename": filename_only,
                    "manual_drawing_type": manual_drawing_type
                })

        # --- Phase 2: Parallel Extraction (CPU Bound) ---
        import concurrent.futures
        import asyncio

        loop = asyncio.get_running_loop()

        def process_one_file(f_info):
            try:
                # This is blocking and optionally uses OCR
                meta = extraction_service.extract_metadata(f_info["path"])
                return f_info, meta, None
            except Exception as e:
                return f_info, None, e

        # Wrapper for thread pool execution
        def parallel_extract(files_info):
            results = []
            # Max workers: Limit to avoid crushing CPU if OCR is used. 
            # 8 is a reasonable balance for modern CPUs.
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(process_one_file, f) for f in files_info]
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            return results

        # Run extraction in thread pool to avoid blocking the async event loop
        
        extraction_results = await loop.run_in_executor(None, parallel_extract, saved_files)

        # --- Phase 3: Update Database (Sequential/Safety) ---
        for f_info, metadata, error in extraction_results:
            filename_only = f_info["filename"]
            manual_drawing_type = f_info["manual_drawing_type"]
            
            if error:
                logger.error(f"Error processing file {filename_only}: {error}")
                continue
                
            if not metadata:
                continue

            try:
                # Check if this is a transmittal
                if isinstance(metadata, dict) and metadata.get("is_transmittal"):
                    logger.info(f"Detected transmittal PDF: {filename_only}")
                    drawings_list = metadata.get("drawings", [])
                    logger.info(f"Extracted {len(drawings_list)} drawings from transmittal")
                    
                    for drawing_meta in drawings_list:
                        drawing_meta["filename"] = filename_only
                        extracted_data.append(drawing_meta)
                        
                        # Validate Enum
                        dtype_enum = models.DrawingType.UNKNOWN
                        if manual_drawing_type:
                            dtype_enum = manual_drawing_type
                        else:
                            dtype_str = drawing_meta.get("drawing_type", "UNKNOWN")
                            try:
                                dtype_enum = models.DrawingType(dtype_str)
                            except ValueError:
                                dtype_enum = models.DrawingType.UNKNOWN
                        
                        drawing_no = drawing_meta.get("drawing_no")
                        existing_drawing = db.query(models.Drawing).filter(
                            models.Drawing.project_id == project.id,
                            models.Drawing.drawing_no == drawing_no
                        ).first()
                        
                        extracted_rev = drawing_meta.get("revision_no", "0")
                        
                        if existing_drawing:
                            logger.info(f"Existing drawing found: {drawing_no}. Updating metadata.")
                            existing_drawing.description = drawing_meta.get("description")
                            existing_drawing.drawing_type = dtype_enum
                            existing_drawing.drawing_date = drawing_meta.get("date")
                            existing_drawing.revision_no = extracted_rev
                            if drawing_meta.get("remarks"):
                                existing_drawing.status = drawing_meta.get("remarks")
                            
                            rev_exists = False
                            for r in existing_drawing.revisions:
                                if r.revision_no == extracted_rev:
                                    rev_exists = True
                                    r.status = existing_drawing.status
                                    r.drawing_date = drawing_meta.get("date")
                                    break
                            
                            if not rev_exists:
                                new_rev = models.DrawingRevision(
                                    drawing_id=existing_drawing.id,
                                    revision_no=extracted_rev,
                                    drawing_date=drawing_meta.get("date"),
                                    status=existing_drawing.status,
                                    filename=filename_only
                                )
                                db.add(new_rev)
                            else:
                                # Prioritize Drawing PDF data if it exists.
                                # If existing revision is from a Drawing PDF (filename ends with .pdf and not transmittal),
                                # we generally do NOT overwrite it with Transmittal data unless specifically desired.
                                # But if existing is from another transmittal, we might update it.
                                # Heuristic: If existing filename == current filename (both transmittals?), update.
                                # If existing filename looks like a drawing (e.g. 1B1.pdf), skip update from Transmittal.
                                for r in existing_drawing.revisions:
                                    if r.revision_no == extracted_rev:
                                        # If existing revision source is a specific drawing PDF and we are parsing a transmittal
                                        is_existing_from_drawing = r.filename and r.filename.endswith(".pdf") and "TRANSMITTAL" not in r.filename.upper()
                                        if is_existing_from_drawing:
                                             logger.info(f"Skipping update for Rev {extracted_rev} from Transmittal as it exists from Drawing PDF {r.filename}")
                                        else:
                                             # Update from Transmittal (e.g. was inferred or from older transmittal)
                                             r.status = existing_drawing.status
                                             r.drawing_date = drawing_meta.get("date")
                                        break
                        else:
                            logger.info(f"New drawing from transmittal: {drawing_no}")
                            new_drawing = models.Drawing(
                                project_id=project.id,
                                filename=filename_only,
                                drawing_no=drawing_no,
                                revision_no=extracted_rev,
                                description=drawing_meta.get("description"),
                                drawing_type=dtype_enum,
                                status=drawing_meta.get("remarks", "Active"),
                                drawing_date=drawing_meta.get("date")
                            )
                            db.add(new_drawing)
                            db.flush()
                            
                            first_revision = models.DrawingRevision(
                                drawing_id=new_drawing.id,
                                revision_no=extracted_rev,
                                drawing_date=drawing_meta.get("date"),
                                status=drawing_meta.get("remarks", "Active"),
                                filename=filename_only
                            )
                            db.add(first_revision)
                
                else:
                    # Single Drawing
                    logger.info(f"Extracted metadata {filename_only}: {metadata}")
                    metadata["filename"] = filename_only
                    extracted_data.append(metadata)
                    
                    dtype_enum = models.DrawingType.UNKNOWN
                    if manual_drawing_type:
                        dtype_enum = manual_drawing_type
                    else:
                        dtype_str = metadata.get("drawing_type", "UNKNOWN")
                        try:
                            dtype_enum = models.DrawingType(dtype_str)
                        except ValueError:
                            dtype_enum = models.DrawingType.UNKNOWN

                    existing_drawing = db.query(models.Drawing).filter(
                        models.Drawing.project_id == project.id,
                        models.Drawing.filename == filename_only
                    ).first()

                    extracted_rev = metadata.get("revision_no", "0")
                    
                    if existing_drawing:
                        logger.info(f"Existing file found: {filename_only}. Overwriting metadata.")
                        existing_drawing.drawing_no = metadata.get("drawing_no")
                        existing_drawing.description = metadata.get("description")
                        existing_drawing.drawing_type = dtype_enum
                        existing_drawing.drawing_date = metadata.get("date")
                        existing_drawing.revision_no = extracted_rev
                        if metadata.get("remarks"):
                            existing_drawing.status = metadata.get("remarks")
                        
                        rev_exists = False
                        for r in existing_drawing.revisions:
                            if r.revision_no == extracted_rev:
                                rev_exists = True
                                r.status = existing_drawing.status
                                r.drawing_date = metadata.get("date")
                                break
                        
                        if not rev_exists:
                            new_rev = models.DrawingRevision(
                                drawing_id=existing_drawing.id,
                                revision_no=extracted_rev,
                                drawing_date=metadata.get("date"),
                                status=existing_drawing.status,
                                filename=filename_only
                            )
                            db.add(new_rev)
                        
                        # Process ALL detected revisions from this PDF (Rule 1: Extract BOTH Rev A and Rev 0 if present)
                        all_revs = metadata.get("all_revisions", [])
                        if all_revs:
                            for rev_item in all_revs:
                                r_no = str(rev_item.get('rev', '')).strip()
                                r_date = rev_item.get('date', '')
                                r_desc = rev_item.get('desc', '') or existing_drawing.status
                                
                                if not r_no: continue
                                
                                # Check if this specific revision exists
                                found_r = None
                                for r in existing_drawing.revisions:
                                    if r.revision_no == r_no:
                                        found_r = r
                                        break
                                
                                if found_r:
                                    # Update with PDF data (Highest Priority)
                                    found_r.drawing_date = r_date
                                    found_r.status = r_desc
                                    found_r.filename = filename_only # Source is this PDF
                                else:
                                    new_extra_rev = models.DrawingRevision(
                                        drawing_id=existing_drawing.id,
                                        revision_no=r_no,
                                        drawing_date=r_date,
                                        status=r_desc,
                                        filename=filename_only
                                    )
                                    db.add(new_extra_rev)

                    else:
                        logger.info(f"New file detected: {filename_only}")
                        new_drawing = models.Drawing(
                            project_id=project.id,
                            filename=filename_only,
                            drawing_no=metadata.get("drawing_no"),
                            revision_no=extracted_rev,
                            description=metadata.get("description"),
                            drawing_type=dtype_enum,
                            status=metadata.get("remarks", "Active"),
                            drawing_date=metadata.get("date")
                        )
                        db.add(new_drawing)
                        db.flush() 

                        first_revision = models.DrawingRevision(
                            drawing_id=new_drawing.id,
                            revision_no=extracted_rev,
                            drawing_date=metadata.get("date"),
                            status=metadata.get("remarks", "Active"),
                            filename=filename_only
                        )
                        db.add(first_revision)

                        # Process ALL detected revisions (Rule 1)
                        all_revs = metadata.get("all_revisions", [])
                        if all_revs:
                            for rev_item in all_revs:
                                r_no = str(rev_item.get('rev', '')).strip()
                                # Skip if it's the one we just added
                                if r_no == extracted_rev: continue 
                                
                                r_date = rev_item.get('date', '')
                                r_desc = rev_item.get('desc', '') or metadata.get("remarks", "Active")
                                
                                extra_rev = models.DrawingRevision(
                                    drawing_id=new_drawing.id,
                                    revision_no=r_no,
                                    drawing_date=r_date,
                                    status=r_desc,
                                    filename=filename_only
                                )
                                db.add(extra_rev)

            except Exception as e:
                logger.error(f"DB Update failed for {filename_only}: {e}")
                # continue
        
        db.commit()
        
        # Reports generation is now handled by a separate endpoint
        
        return {"message": f"Processed {len(extracted_data)} drawings"}

    except Exception as e:
        print(f"Upload failed: {e}")
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    # 1. Check if project exists
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 2. Delete from Disk
    try:
        if os.path.exists(project.folder_path):
            shutil.rmtree(project.folder_path)
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        # Proceed to delete from DB even if folder delete fails (or handle as needed)

    # 3. Delete from MongoDB (Synchronous)
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        mongo_db = client[mongo_config.db_name]
        mongo_db.projects.delete_one({"sql_id": project_id})
        client.close()
    except Exception as e:
        logger.error(f"Error deleting from MongoDB: {e}")

    # 4. Delete from SQLite
    crud.delete_project(db, project_id)

    return {"message": "Project deleted successfully"}

@router.get("/{project_id}/download/{file_type}")
def download_file(project_id: int, file_type: str, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if file_type == "transmittal":
        file_path = os.path.join(project.folder_path, "transmittal.xlsx")
        filename = f"{project.title}_Transmittal.xlsx"
    elif file_type == "log":
        file_path = os.path.join(project.folder_path, "drawing_log.xlsx")
        filename = f"{project.title}_DrawingLog.xlsx"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File generated yet? Try uploading folders first.")
        
    return FileResponse(file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.post("/{project_id}/generate_reports")
def generate_reports(project_id: int, db: Session = Depends(get_db)):
    """
    Manually trigger generation of transmittal and drawing log reports.
    Call this after a batch upload is complete.
    """
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        all_drawings = crud.get_project_drawings(db, project_id)
        
        # --- NEW: Infer & Persist Missing Dates ---
        # 1. Calculate Common Date (Mode)
        valid_dates = []
        import re
        for d in all_drawings:
             # Check for reasonably valid date string
             if d.drawing_date and len(d.drawing_date.strip()) >= 8:
                  valid_dates.append(d.drawing_date)
        
        common_date = None
        if valid_dates:
             from collections import Counter
             common_date = Counter(valid_dates).most_common(1)[0][0]
             logger.info(f"Inferred Common Date from batch: {common_date}")
        else:
             from datetime import datetime
             common_date = datetime.now().strftime("%Y-%m-%d")
             logger.info(f"No dates in batch. Fallback to Today: {common_date}")

        # 2. Update DB Records with Missing Dates
        dates_updated = False
        for d in all_drawings:
             should_update = False
             if not d.drawing_date or len(d.drawing_date.strip()) < 8:
                  should_update = True
             
             if should_update:
                  d.drawing_date = common_date
                  dates_updated = True
                  
                  # Also update revisions
                  for r in d.revisions:
                       if not r.drawing_date or len(r.drawing_date.strip()) < 8:
                            r.drawing_date = common_date

        if dates_updated:
             db.commit()
             # No need to refresh 'project', but 'all_drawings' objects are attached to session so they are updated
        # ------------------------------------------
        transmittal_data = []
        for d in all_drawings:
            transmittal_data.append({
                "drawing_no": d.drawing_no,
                "revision_no": d.revision_no,
                "description": d.description,
                "date": d.drawing_date,
                "date_sent": d.created_at.strftime("%d/%m/%Y") if d.created_at else "",
                "status": d.status,
                "quantity": 1,
                "drawing_type": d.drawing_type.value if d.drawing_type else "UNKNOWN",
                "remarks": d.status 
            })

        # 2. Drawing Log Data
        drawing_log_data = []
        for d in all_drawings:
            revs = []
            if d.revisions:
                sorted_revs = sorted(d.revisions, key=lambda r: r.created_at)
                for r in sorted_revs:
                    revs.append({
                        "rev": r.revision_no,
                        "date": r.drawing_date,
                        "status": r.status
                    })
            else:
                revs.append({
                    "rev": d.revision_no,
                    "date": d.drawing_date,
                    "status": d.status
                })

            drawing_log_data.append({
                "drawing_no": d.drawing_no,
                "description": d.description,
                "status": d.status,
                "remarks": d.status,
                "revision_no": d.revision_no,
                "date": d.drawing_date,
                "revisions": revs
            })

        if transmittal_data:
            transmittal_path = os.path.join(project.folder_path, "transmittal.xlsx")
            excel_manager.create_transmittal(transmittal_data, transmittal_path, project.title)
            
            log_path = os.path.join(project.folder_path, "drawing_log.xlsx")
            excel_manager.update_drawing_log(drawing_log_data, log_path)
            
        return {"message": "Reports generated successfully"}
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
