from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
from datetime import datetime

router = APIRouter(tags=["WebSocket"])

# ─── CONNECTION MANAGER ───────────────────────
class ConnectionManager:
    def __init__(self):
        # {room_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        print(f"Yangi ulanish: {room} | "
              f"Jami: {len(self.active_connections[room])}")

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
        print(f"Uzildi: {room}")

    async def send_personal(self, message: str, websocket: WebSocket):
        """Faqat bitta clientga"""
        await websocket.send_text(message)

    async def broadcast(self, message: str, room: str):
        """Xonadagi barcha clientlarga"""
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_text(message)

    async def broadcast_except(
        self,
        message: str,
        room: str,
        exclude: WebSocket
    ):
        """O'zidan boshqa barchaga"""
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                if connection != exclude:
                    await connection.send_text(message)

    def get_room_count(self, room: str) -> int:
        """Xonadagi odamlar soni"""
        return len(self.active_connections.get(room, []))


manager = ConnectionManager()


# ─── CHAT ENDPOINT ────────────────────────────
@router.websocket("/ws/chat/{room}/{username}")
async def chat_endpoint(
    websocket: WebSocket,
    room: str,
    username: str
):
    await manager.connect(websocket, room)

    # Kirish xabari
    join_message = json.dumps({
        "type": "system",
        "message": f"{username} xonaga kirdi!",
        "room": room,
        "users_count": manager.get_room_count(room),
        "timestamp": datetime.now().strftime("%H:%M")
    })
    await manager.broadcast(join_message, room)

    try:
        while True:
            # Xabar kutish
            data = await websocket.receive_text()

            # JSON formatida yuborish
            message = json.dumps({
                "type": "message",
                "username": username,
                "message": data,
                "room": room,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            await manager.broadcast(message, room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)

        # Chiqish xabari
        leave_message = json.dumps({
            "type": "system",
            "message": f"{username} xonadan chiqdi",
            "room": room,
            "users_count": manager.get_room_count(room),
            "timestamp": datetime.now().strftime("%H:%M")
        })
        await manager.broadcast(leave_message, room)


# ─── XONALAR RO'YXATI ─────────────────────────
@router.get("/ws/rooms")
def get_active_rooms():
    return {
        "rooms": {
            room: len(connections)
            for room, connections
            in manager.active_connections.items()
        }
    }