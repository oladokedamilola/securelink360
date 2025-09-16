// static/js/network_join.js
class NetworkJoin {
    constructor() {
        this.socket = null;
        this.initializeWebSocket();
        this.initializeEventListeners();
    }

    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/network/join/`;
        
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('Connected to join service');
            this.updateStatus('Connected', 'info');
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleSocketMessage(data);
        };

        this.socket.onclose = () => {
            this.updateStatus('Disconnected from join service', 'warning');
        };
    }

    handleSocketMessage(data) {
        switch (data.type) {
            case 'join_response':
                this.handleJoinResponse(data);
                break;
            case 'error':
                this.updateStatus(data.message, 'danger');
                break;
        }
    }

    handleJoinResponse(data) {
        const statusElement = document.getElementById('join-status');
        
        switch (data.status) {
            case 'pending':
                this.updateStatus('Request sent! Waiting for admin approval...', 'warning');
                document.getElementById('join-btn').disabled = true;
                break;
            case 'approved':
                this.updateStatus('Request approved! You are now connected to the network.', 'success');
                break;
            case 'denied':
                this.updateStatus('Request denied by administrator.', 'danger');
                break;
            case 'intruder_detected':
                this.updateStatus('ACCESS DENIED: Unauthorized access attempt detected and logged.', 'danger');
                break;
        }
    }

    updateStatus(message, type) {
        const statusElement = document.getElementById('join-status');
        statusElement.className = `alert alert-${type}`;
        statusElement.innerHTML = `<i class="bi bi-info-circle"></i> ${message}`;
    }

    initializeEventListeners() {
        const deviceSelect = document.getElementById('device-select');
        const joinBtn = document.getElementById('join-btn');

        deviceSelect.addEventListener('change', () => {
            joinBtn.disabled = !deviceSelect.value;
        });

        joinBtn.addEventListener('click', () => {
            this.sendJoinRequest(deviceSelect.value);
        });
    }

    sendJoinRequest(deviceId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'join_request',
                network_identifier: NETWORK_ID,
                device_id: deviceId
            }));
            this.updateStatus('Sending join request...', 'info');
        } else {
            this.updateStatus('Connection error. Please refresh the page.', 'danger');
        }
    }
}

// Initialize the join page
document.addEventListener('DOMContentLoaded', () => {
    new NetworkJoin();
});