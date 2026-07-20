import cadquery as cq
import datetime
import sys
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import traceback

app = FastAPI()

# Allow frontend origin (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    rows: int = 6
    cols: int = 10
    cell_width: int = 80
    cell_height: int = 50
    panel_width: int = 1000
    panel_height: int = 600
    frame_thickness: int = 30
    frame_width: int = 20
    bevel_size: int = 2
    cell_spacing_x: int = 10
    cell_spacing_y: int = 10

class GenerateResponse(BaseModel):
    stl_base64: str
    telemetry: List[str]

def log(telemetry: List[str], msg: str, success=True):
    ts = datetime.datetime.utcnow().isoformat()
    status = "OK" if success else "FAIL"
    line = f"[{ts}] [{status}] {msg}"
    telemetry.append(line)
    print(line, file=sys.stderr)

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_stl(req: GenerateRequest):
    telemetry = []
    try:
        log(telemetry, "Starting solar panel generation")
        log(telemetry, f"Params: rows={req.rows}, cols={req.cols}, panel={req.panel_width}x{req.panel_height}")

        # Extract parameters
        panel_width = req.panel_width
        panel_height = req.panel_height
        frame_thickness = req.frame_thickness
        frame_width = req.frame_width
        bevel_size = req.bevel_size
        cell_width = req.cell_width
        cell_height = req.cell_height
        cell_spacing_x = req.cell_spacing_x
        cell_spacing_y = req.cell_spacing_y
        num_rows = req.rows
        num_cols = req.cols

        # --- Frame ---
        log(telemetry, "Creating outer frame")
        frame = cq.Workplane("XY").rect(panel_width, panel_height).extrude(frame_thickness)
        log(telemetry, "Outer frame done")

        log(telemetry, "Cutting inner opening")
        frame = (frame
                 .faces(">Z")
                 .workplane()
                 .rect(panel_width - 2*frame_width, panel_height - 2*frame_width)
                 .cutBlind(-frame_thickness))
        log(telemetry, "Inner opening cut")

        log(telemetry, "Chamfering outer top edges")
        outer_edges = frame.faces(">Z").edges().filter(
            lambda e: (e.Center().x**2 + e.Center().y**2) > 1
        )
        frame = outer_edges.chamfer(bevel_size)
        log(telemetry, "Chamfer applied")

        # --- Cell block layout ---
        total_cells_width = num_cols * cell_width + (num_cols - 1) * cell_spacing_x
        total_cells_height = num_rows * cell_height + (num_rows - 1) * cell_spacing_y
        start_x = -panel_width/2 + frame_width + (panel_width - 2*frame_width - total_cells_width)/2 + cell_width/2
        start_y = -panel_height/2 + frame_width + (panel_height - 2*frame_width - total_cells_height)/2 + cell_height/2
        log(telemetry, f"Cell block size: {total_cells_width:.1f} x {total_cells_height:.1f} mm")
        log(telemetry, f"Start position: ({start_x:.1f}, {start_y:.1f})")

        # --- Generate cells ---
        cells = cq.Workplane("XY")
        cell_count = 0
        log(telemetry, "Starting cell generation loop")

        for row in range(num_rows):
            for col in range(num_cols):
                x = start_x + col * (cell_width + cell_spacing_x)
                y = start_y + row * (cell_height + cell_spacing_y)
                cell = (cq.Workplane("XY")
                        .rect(cell_width, cell_height)
                        .extrude(frame_thickness - 1)
                        .translate((x, y, 0)))
                cells = cells.union(cell)
                cell_count += 1
            log(telemetry, f"Row {row+1}/{num_rows} done – {cell_count} cells created so far")

        log(telemetry, f"Cell generation complete – {cell_count} cells created")

        # --- Union & export ---
        log(telemetry, "Combining frame and cells")
        result = frame.union(cells)
        log(telemetry, "Union done")

        log(telemetry, "Exporting STL to memory")
        # Export to bytes
        stl_bytes = io.BytesIO()
        cq.exporters.export(result, stl_bytes, "STL")
        stl_data = stl_bytes.getvalue()
        log(telemetry, f"Export complete – {len(stl_data)} bytes")

        # Encode as base64 for JSON response
        stl_base64 = base64.b64encode(stl_data).decode('ascii')
        log(telemetry, "Response prepared")

        return GenerateResponse(stl_base64=stl_base64, telemetry=telemetry)

    except Exception as e:
        log(telemetry, f"ERROR: {str(e)}", success=False)
        log(telemetry, traceback.format_exc(), success=False)
        raise HTTPException(status_code=500, detail={"error": str(e), "telemetry": telemetry})
