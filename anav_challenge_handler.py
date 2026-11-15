import json

def handle_disciple_challenge(handler, client_ip):
    content_length = int(handler.headers.get('Content-Length', 0))
    post_data = handler.rfile.read(content_length) if content_length > 0 else b"{}"
    
    try:
        payload = json.loads(post_data.decode('utf-8'))
    except Exception:
        payload = {}

    challenge_type = handler.headers.get('X-ANAV-Challenge', 'standard-probe')
    route_target = handler.headers.get('X-ANAV-Route-Target', 'https://anav.trade')

    print(f"[DISCIPLE CHALLENGE] Received handshake from {client_ip} | Type: {challenge_type} | Target: {route_target}")

    response_data = {
        "status": "DISCIPLE_ACK",
        "node_ip": client_ip,
        "anchored_to": "https://anav.trade",
        "mesh_consensus": "synchronized"
    }
    
    handler.send_response(200)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('X-ANAV-Route-Target', 'https://anav.trade')
    handler.send_header('X-ANAV-Challenge-Status', 'accepted')
    handler.end_headers()
    handler.wfile.write(json.dumps(response_data).encode('utf-8'))
