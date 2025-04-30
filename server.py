import asyncio
import websockets
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ws_proxy")

# Server WebSocket endpoint
SERVER_URL = "wss://api.tenclass.net/xiaozhi/v1/"

# Headers to include with server connection
SERVER_HEADERS = {
    "Authorization": "Bearer test_token",
    "Protocol-Version": "1",
    "Device-Id": "d4:d8:53:70:88:94",
    "Client-Id": "9cd8b05e-bbae-478e-8ea9-58bc908fb16a",
}

# Proxy configuration
PROXY_HOST = "0.0.0.0"  # Listen on all interfaces
PROXY_PORT = 8765  # Port for clients to connect to


async def forward_messages(source, destination, name):
    """Forward messages from source to destination WebSocket"""
    try:
        async for message in source:
            logger.info(f"{name} message: {message[:100]}...")  # Log first 100 chars
            await destination.send(message)
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"{name} connection closed")
    except Exception as e:
        logger.error(f"Error in {name} forwarding: {e}")


async def proxy_handler(client_websocket, path):
    """Handle each client connection by connecting to the server and forwarding traffic"""
    logger.info(f"Client connected from {client_websocket.remote_address}")

    try:
        # Connect to the server with specified headers
        async with websockets.connect(
            SERVER_URL, extra_headers=SERVER_HEADERS
        ) as server_websocket:
            logger.info(f"Connected to server at {SERVER_URL}")

            # Create two tasks for bidirectional forwarding
            client_to_server = asyncio.create_task(
                forward_messages(client_websocket, server_websocket, "Client → Server")
            )
            server_to_client = asyncio.create_task(
                forward_messages(server_websocket, client_websocket, "Server → Client")
            )

            # Wait for either forwarding direction to complete (or error)
            done, pending = await asyncio.wait(
                [client_to_server, server_to_client],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the remaining task
            for task in pending:
                task.cancel()

            logger.info("Proxy connection terminated")

    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"Failed to connect to server: {e}")
        await client_websocket.close(1011, f"Failed to connect to server: {e}")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        await client_websocket.close(1011, f"Proxy error: {e}")


async def main():
    """Start the WebSocket proxy server"""
    logger.info(f"Starting WebSocket proxy server on {PROXY_HOST}:{PROXY_PORT}")
    logger.info(f"Forwarding to {SERVER_URL}")

    async with websockets.serve(proxy_handler, PROXY_HOST, PROXY_PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Proxy server stopped by user")
