from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated
from . import crud
from .database import get_db, init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

class Device(BaseModel):
    id: str
    name: str
    type: str
    status: str
    relay_port: int

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    name: str
    type: str
    relay_port: Annotated[int, Field(ge=1, le=6)]


# GET Requet to get all devices
@app.get("/devices", response_model=list[Device])
def get_devices(db = Depends(get_db)):
    devices = crud.get_devices(db)
    print(devices)
    return [{
        **dict(device),
        'id': str(device['id'])
    } for device in devices]

# GET Requet to get a particular device with ID
@app.get("/devices/{device_id}", response_model=Device)
def get_device(device_id: str, db = Depends(get_db)):
    device = crud.get_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        **dict(device),
        'id': str(device['id'])
    }

# POST Request to toggle the device status
@app.post("/devices/{device_id}/toggle", response_model=Device)
def toggle_device(device_id: str, db = Depends(get_db)):
    device = crud.toggle_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return dict(device)

# POST Request to create device
@app.post("/devices", response_model=Device)
def create_device(device: DeviceCreate, db = Depends(get_db)):
    try:
        device_id = crud.create_device(
            db, 
            name=device.name, 
            device_type=device.type, 
            relay_port=device.relay_port
        )
        created_device = crud.get_device(db, str(device_id))
        if created_device is None:
            raise HTTPException(status_code=500, detail="Failed to create device")
        return {
            **dict(created_device),
            'id': str(created_device['id'])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE Request to delete a device
@app.delete("/devices/{device_id}")
def delete_device(device_id: str, db = Depends(get_db)):
    if crud.delete_device(db, device_id):
        return {"message": "Device deleted successfully"}
    raise HTTPException(status_code=404, detail="Device not found")
