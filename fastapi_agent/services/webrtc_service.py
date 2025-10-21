"""
WebRTC Service for browser-based voice calls
Uses aiortc for WebRTC implementation
"""
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRecorder, MediaPlayer
import logging
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

# Store active peer connections
_peer_connections: Dict[str, RTCPeerConnection] = {}


class AudioProcessor:
    """
    Process audio from WebRTC stream
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.audio_buffer = []
    
    async def process_frame(self, frame):
        """Process a single audio frame"""
        # TODO: Implement audio processing
        # - Buffer audio frames
        # - Send to STT when enough data accumulated
        # - Process with agent
        # - Generate TTS response
        pass


async def create_peer_connection(session_id: str) -> RTCPeerConnection:
    """
    Create a new RTCPeerConnection
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        RTCPeerConnection instance
    """
    logger.info(f"Creating peer connection for session: {session_id}")
    
    pc = RTCPeerConnection()
    _peer_connections[session_id] = pc
    
    # Handle track events
    @pc.on("track")
    async def on_track(track: MediaStreamTrack):
        logger.info(f"Track received: {track.kind}")
        
        if track.kind == "audio":
            processor = AudioProcessor(session_id)
            
            while True:
                try:
                    frame = await track.recv()
                    await processor.process_frame(frame)
                except Exception as e:
                    logger.error(f"Error processing track: {str(e)}")
                    break
    
    # Handle connection state changes
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state changed: {pc.connectionState}")
        
        if pc.connectionState == "failed":
            await close_peer_connection(session_id)
    
    return pc


async def handle_offer(session_id: str, offer_sdp: str) -> str:
    """
    Handle WebRTC offer and create answer
    
    Args:
        session_id: Session ID
        offer_sdp: SDP offer from client
    
    Returns:
        SDP answer
    """
    try:
        logger.info(f"Handling offer for session: {session_id}")
        
        # Get or create peer connection
        pc = _peer_connections.get(session_id)
        if pc is None:
            pc = await create_peer_connection(session_id)
        
        # Set remote description (offer)
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        logger.info(f"Created answer for session: {session_id}")
        
        return pc.localDescription.sdp
    
    except Exception as e:
        logger.error(f"Error handling offer: {str(e)}", exc_info=True)
        raise


async def close_peer_connection(session_id: str):
    """
    Close and cleanup a peer connection
    
    Args:
        session_id: Session ID
    """
    logger.info(f"Closing peer connection: {session_id}")
    
    pc = _peer_connections.get(session_id)
    if pc:
        await pc.close()
        del _peer_connections[session_id]


async def cleanup_all():
    """Close all peer connections"""
    logger.info("Cleaning up all peer connections")
    
    for session_id in list(_peer_connections.keys()):
        await close_peer_connection(session_id)


# Note: For MVP, we're using WebSocket audio streaming instead of full WebRTC
# WebRTC with aiortc requires more complex setup including STUN/TURN servers
# The WebSocket implementation in calls.py is simpler for initial testing

