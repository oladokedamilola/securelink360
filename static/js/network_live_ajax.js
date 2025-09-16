// static/js/network_live_ajax.js
class NetworkLiveAJAX {
    constructor() {
        this.cy = null;
        this.pendingRequests = new Map();
        this.pollingInterval = null;
        this.isPolling = false;
        
        this.initializeCytoscape();
        this.initializeEventListeners();
        this.startPolling();
    }

    initializeCytoscape() {
        // Initialize Cytoscape instance
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#007bff',
                        'label': 'data(label)',
                        'width': 40,
                        'height': 40
                    }
                },
                {
                    selector: 'node[status = "online"]',
                    style: {
                        'background-color': '#198754'
                    }
                },
                {
                    selector: 'node[status = "offline"]',
                    style: {
                        'background-color': '#6c757d'
                    }
                },
                {
                    selector: 'node[status = "pending"]',
                    style: {
                        'background-color': '#ffc107'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 3,
                        'line-color': '#6c757d',
                        'target-arrow-color': '#6c757d',
                        'target-arrow-shape': 'triangle'
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 100,
                nodeOverlap: 20,
                refresh: 20,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100
            }
        });
    }

    startPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // Initial load
        this.fetchNetworkStatus();
        
        // Poll every 5 seconds
        this.pollingInterval = setInterval(() => {
            this.fetchNetworkStatus();
        }, 5000);
        
        this.isPolling = true;
        this.updateSessionStatus(true);
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isPolling = false;
        this.updateSessionStatus(false);
    }

    async fetchNetworkStatus() {
        try {
            const response = await fetch(`/n/live/api/network/${NETWORK_ID}/status/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.handleNetworkData(data);
            
        } catch (error) {
            console.error('Error fetching network status:', error);
            this.showNotification('Connection Error', 'Failed to fetch network updates', 'danger');
        }
    }

    handleNetworkData(data) {
        // Update devices in visualization
        this.updateDevices(data.devices);
        
        // Update join requests
        this.updateJoinRequests(data.pending_requests);
        
        // Update network info
        this.updateNetworkInfo(data.network);
    }

    updateDevices(devices) {
        // Clear existing device nodes
        this.cy.elements().filter(node => node.data().id?.startsWith('device_')).remove();
        
        // Add new devices
        devices.forEach(device => {
            this.cy.add({
                group: 'nodes',
                data: {
                    id: `device_${device.id}`,
                    label: device.name || device.mac_address,
                    status: device.status
                },
                position: { x: Math.random() * 400, y: Math.random() * 400 }
            });
        });
        
        // Refresh layout
        this.cy.layout({ name: 'cose' }).run();
    }

    updateJoinRequests(requests) {
        const currentRequestIds = new Set(this.pendingRequests.keys());
        const newRequestIds = new Set(requests.map(req => req.id));
        
        // Remove requests that are no longer pending
        currentRequestIds.forEach(requestId => {
            if (!newRequestIds.has(requestId)) {
                this.removeRequestFromUI(requestId);
                this.pendingRequests.delete(requestId);
            }
        });
        
        // Add new requests
        requests.forEach(request => {
            if (!this.pendingRequests.has(request.id)) {
                this.pendingRequests.set(request.id, request);
                this.addRequestToSidebar(request);
            }
        });
        
        this.updateRequestCount();
    }

    addRequestToSidebar(request) {
        const requestElement = `
            <div class="list-group-item alert-item join-request" data-request-id="${request.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${request.user_email}</h6>
                        <p class="mb-1 small">Device: ${request.device_name || 'Unknown'}</p>
                        <small class="text-muted">IP: ${request.ip_address}</small>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success approve-btn" title="Approve">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-outline-danger reject-btn" title="Reject">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <small class="text-muted">${new Date(request.created_at).toLocaleTimeString()}</small>
            </div>
        `;
        
        document.getElementById('join-requests-list').insertAdjacentHTML('afterbegin', requestElement);
        this.attachButtonListeners();
    }

    removeRequestFromUI(requestId) {
        const requestElement = document.querySelector(`[data-request-id="${requestId}"]`);
        if (requestElement) {
            requestElement.remove();
        }
    }

    attachButtonListeners() {
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.onclick = (e) => {
                const requestId = e.target.closest('.alert-item').dataset.requestId;
                this.approveRequest(requestId);
            };
        });

        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.onclick = (e) => {
                const requestId = e.target.closest('.alert-item').dataset.requestId;
                this.rejectRequest(requestId);
            };
        });
    }

    async approveRequest(requestId) {
        try {
            const response = await fetch(`/n/live/api/join-request/${requestId}/approve/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                this.removeRequestFromUI(requestId);
                this.pendingRequests.delete(parseInt(requestId));
                this.updateRequestCount();
                this.showNotification('Request Approved', 'Join request has been approved', 'success');
            } else {
                throw new Error('Failed to approve request');
            }
            
        } catch (error) {
            console.error('Error approving request:', error);
            this.showNotification('Error', 'Failed to approve request', 'danger');
        }
    }

    async rejectRequest(requestId) {
        try {
            const response = await fetch(`/n/live/api/join-request/${requestId}/reject/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                this.removeRequestFromUI(requestId);
                this.pendingRequests.delete(parseInt(requestId));
                this.updateRequestCount();
                this.showNotification('Request Rejected', 'Join request has been rejected', 'warning');
            } else {
                throw new Error('Failed to reject request');
            }
            
        } catch (error) {
            console.error('Error rejecting request:', error);
            this.showNotification('Error', 'Failed to reject request', 'danger');
        }
    }

    updateRequestCount() {
        const count = this.pendingRequests.size;
        document.getElementById('request-count').textContent = count;
        this.updateAlertBadge();
    }

    updateAlertBadge() {
        const totalAlerts = this.pendingRequests.size;
        const badge = document.getElementById('alert-badge');
        
        if (totalAlerts > 0) {
            badge.textContent = totalAlerts;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }

    updateNetworkInfo(network) {
        // Update network info in the control panel if needed
        const memberCountElement = document.querySelector('.list-group-item:last-child strong');
        if (memberCountElement) {
            memberCountElement.textContent = network.member_count;
        }
    }

    updateSessionStatus(isActive) {
        const statusElement = document.getElementById('session-status');
        const startBtn = document.getElementById('start-session-btn');
        const endBtn = document.getElementById('end-session-btn');

        if (isActive) {
            statusElement.className = 'alert alert-success';
            statusElement.innerHTML = `<i class="fas fa-play-circle"></i> Session active - Polling every 5 seconds`;
            startBtn.disabled = true;
            endBtn.disabled = false;
        } else {
            statusElement.className = 'alert alert-info';
            statusElement.innerHTML = '<i class="fas fa-info-circle"></i> Session not started';
            startBtn.disabled = false;
            endBtn.disabled = true;
        }
    }

    showNotification(title, message, type = 'info') {
        // Create Bootstrap toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = document.getElementById('toast-container') || this.createToastContainer();
        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    initializeEventListeners() {
        // Session control buttons
        document.getElementById('start-session-btn')?.addEventListener('click', () => this.startPolling());
        document.getElementById('end-session-btn')?.addEventListener('click', () => this.stopPolling());
        document.getElementById('refresh-network-btn')?.addEventListener('click', () => this.fetchNetworkStatus());
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    if (typeof NETWORK_ID !== 'undefined') {
        window.networkLive = new NetworkLiveAJAX();
    }
});