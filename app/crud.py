from sqlite3 import Connection

def get_devices(db: Connection):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM devices')
    columns = [description[0] for description in cursor.description] # to fetch column
    rows = cursor.fetchall() # to fetch all rows

    #To convert Cursor Format to List of Dictionary, to make it easily parseable by frontend
    devices = [dict(zip(columns, row)) for row in rows]

    # Make id string, becauae JSON only accept string.
    for device in devices:
        device['id'] = str(device['id'])

    return devices

def get_device(db: Connection, device_id: str):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        device_dict = dict(zip(columns, row))
        device_dict['id'] = str(device_dict['id'])
        return device_dict
    return None

def toggle_device(db: Connection, device_id: str):
    device = get_device(db, device_id)
    if device:
        device_dict = dict(device)
        new_status = None
        if device_dict['type'] == "door":
            new_status = "open" if device_dict['status'] == "closed" else "closed"
        else:
            new_status = "on" if device_dict['status'] == "off" else "off"
        
        cursor = db.cursor()
        cursor.execute(
            'UPDATE devices SET status = ? WHERE id = ?',
            (new_status, device_id)
        )
        db.commit()
        return get_device(db, device_id)
    return None

def create_device(db: Connection , name: str, device_type: str, relay_port: int):
    try:
        # Convert inputs to their proper types to ensure clean data
        name = str(name)
        device_type = str(device_type)
        relay_port = int(relay_port)

        
        if not 1 <= relay_port <= 6:
            raise ValueError("Relay port must be between 1 and 6")
            
        cursor = db.cursor()
        initial_status = 'closed' if device_type == 'door' else 'off'
        cursor.execute(
            'INSERT INTO devices (name, type, status, relay_port) VALUES (?, ?, ?, ?)',
            (name, device_type, initial_status, relay_port)
        )
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create device: {str(e)}")

def update_device(db: Connection, device_id: str, name: str = None, device_type: str = None, relay_port: int = None):
    if relay_port is not None and not 1 <= relay_port <= 6:
        raise ValueError("Relay port must be between 1 and 6")
        
    updates = []
    values = []
    
    if name is not None:
        updates.append("name = ?")
        values.append(name)
    if device_type is not None:
        updates.append("type = ?")
        values.append(device_type)
    if relay_port is not None:
        updates.append("relay_port = ?")
        values.append(relay_port)
        
    if not updates:
        return get_device(db, device_id)
        
    values.append(device_id)
    cursor = db.cursor()
    cursor.execute(
        f'UPDATE devices SET {", ".join(updates)} WHERE id = ?',
        tuple(values)
    )
    db.commit()
    return get_device(db, device_id)

def delete_device(db: Connection, device_id: str):
    cursor = db.cursor()
    cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    db.commit()
    return cursor.rowcount > 0 