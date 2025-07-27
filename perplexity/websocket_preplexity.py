import websocket  # This should be from websocket-client, not any other package
import json
import time
import random
from threading import Thread
from queue import Queue
import ssl

class PerplexityWebSocketMonitor:
    def __init__(self):
        # Correct WebSocket endpoint for Perplexity.ai
        self.ws_url = "wss://www.perplexity.ai/socket.io/?EIO=4&transport=websocket"
        self.message_queue = Queue()
        self.connection_active = False
        self.ws = None

    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            if message.startswith('42["'):
                payload = json.loads(message[2:])
                event_type = payload[0]
                data = payload[1]
                
                if event_type == "query_response":
                    self.process_response(data)
                elif event_type == "progress_update":
                    print(f"Progress: {data.get('progress', 0)}%")
                
            self.message_queue.put(message)
        except Exception as e:
            print(f"Message processing error: {str(e)}")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {str(error)}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connection_active = False
        print(f"Disconnected (Code: {close_status_code}, Reason: {close_msg})")

    def on_open(self, ws):
        """Initialize connection with handshake"""
        self.connection_active = True
        print("Connected to Perplexity WebSocket")
        
        # Initial handshake (adjust based on actual protocol)
        ws.send('40{"token":null,"deviceId":"' + self.generate_device_id() + '"}')
        time.sleep(0.5)
        ws.send('42["session_init",{}]')

    def generate_device_id(self):
        """Generate realistic device ID"""
        return f"web:{random.randint(1000000000, 9999999999)}"

    def process_response(self, data):
        """Process and save complete responses"""
        response = {
            "timestamp": int(time.time()),
            "query": data.get("query"),
            "answer": data.get("answer"),
            "sources": data.get("sources", []),
            "related": data.get("related_questions", [])
        }
        
        filename = f"perplexity_ws_{response['timestamp']}.json"
        with open(filename, 'w') as f:
            json.dump(response, f, indent=2)
        
        print(f"Saved response to {filename}")

    def start_connection(self):
        """Establish WebSocket connection with SSL context"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            header={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin": "https://www.perplexity.ai/search/top-10-cars-in-india-LNcLFbJ4Q4WaCFPZbJvdog"
            }
        )
        
        # Run in background thread
        self.ws_thread = Thread(target=self.ws.run_forever, kwargs={
            "sslopt": {"cert_reqs": ssl.CERT_NONE},
            "ping_interval": 25,
            "ping_timeout": 10
        })
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def send_query(self, question):
        """Send question through WebSocket"""
        if not self.connection_active:
            print("Connection not active")
            return False
            
        query_payload = {
            "query": question,
            "source": "web",
            "language": "en",
            "version": "2.0",
            "session_id": str(random.randint(100000, 999999))
        }
        
        message = f'42["query",{json.dumps(query_payload)}]'
        self.ws.send(message)
        return True

    def monitor(self, duration=60):
        """Run monitoring for specified duration"""
        self.start_connection()
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    print(f"Raw Message: {message[:200]}...")  # Truncate long messages
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Stopping monitor...")
        finally:
            self.ws.close()

if __name__ == "__main__":
    monitor = PerplexityWebSocketMonitor()
    
    # Start monitoring for 2 minutes
    Thread(target=monitor.monitor, kwargs={"duration": 120}).start()
    
    # Example query after 5 seconds
    time.sleep(5)
    monitor.send_query("Explain quantum computing in simple terms")
    
    # Keep main thread alive
    while True:
        time.sleep(1)