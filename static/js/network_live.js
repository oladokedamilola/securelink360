// static/js/network_live.js
class NetworkLive {
    constructor() {
        this.cy = null;
        this.pendingRequests = new Map();
        this.intruderAlerts = new Map(); // store intruders for badge & auto-remove
        this.pollingInterval = null;
        this.isPolling = false;
        this.nodeAnimations = new Map();
        this.routerNodeId = `network_${NETWORK_ID}`;

        this.initializeCytoscape();
        this.addZoomControls();
        this.initializeEventListeners();
        this.startPolling();
    }

    // -------------------------
    // CYTOSCAPE INITIALIZATION
    // -------------------------
    initializeCytoscape() {
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#007bff',
                        'label': '', // hidden by default
                        'width': 8,
                        'height': 8,
                        'font-size': '5px',
                        'color': '#ffffff',
                        'text-outline-color': '#000000',
                        'text-outline-width': '0.5px',
                        'border-width': '1.5px',
                        'border-color': 'rgba(255, 255, 255, 0.4)',
                        'text-valign': 'center',
                        'text-halign': 'center'
                    }
                },
                {
                    selector: 'node:hover',
                    style: {
                        'label': 'data(label)', // show on hover
                        'text-background-color': 'rgba(0, 0, 0, 0.7)',
                        'text-background-opacity': 1,
                        'text-background-padding': '2px',
                        'text-background-shape': 'roundrectangle'
                    }
                },
                {
                    selector: 'node[role = "router"]',
                    style: {
                        'background-color': '#0d6efd',
                        'width': 18,
                        'height': 18,
                        'font-size': '7px',
                        'border-width': 2,
                        'border-color': '#ffffff',
                        'label': '' // hidden root label
                    }
                },
                {
                    selector: 'node[role = "router"]:hover',
                    style: { 'label': 'data(label)' }
                },
                {
                    selector: 'node[status = "online"]',
                    style: { 'background-color': '#198754', 'border-color': '#4cd98c' }
                },
                {
                    selector: 'node[status = "offline"]',
                    style: { 'background-color': '#6c757d', 'border-color': '#a0a7b0', 'opacity': 0.6 }
                },
                {
                    selector: 'node[status = "pending"]',
                    style: { 'background-color': '#ffc107', 'border-color': '#ffd965', 'color': '#000000' }
                },
                {
                    selector: 'node[status = "intruder"]',
                    style: { 'background-color': '#dc3545', 'border-color': '#ff6b7a' }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 1,
                        'line-color': 'rgba(255, 255, 255, 0.25)',
                        'target-arrow-color': 'rgba(255, 255, 255, 0.25)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.5,
                        'arrow-scale': 0.8
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 60,
                nodeOverlap: 10,
                fit: true,
                padding: 15,
                randomize: false,
                animate: false,
                componentSpacing: 60,
                nodeRepulsion: 3000
            },
            wheelSensitivity: 0,
            userZoomingEnabled: false,
            userPanningEnabled: true
        });

        this.cy.add({
            group: 'nodes',
            data: { id: this.routerNodeId, label: NETWORK_NAME, role: 'router' },
            position: { x: 300, y: 300 }
        });

        this.cy.on('tap', 'node', evt => this.showNodeDetails(evt.target));
        this.cy.on('mouseover', 'node', evt => {
            const n = evt.target;
            n.style('border-width', '2px');
            n.style('border-color', '#ffffff');
            n.style('z-index', '9999');
        });
        this.cy.on('mouseout', 'node', evt => {
            const n = evt.target;
            if (n.data('role') !== 'router') {
                n.style('border-width', '1.5px');
                n.style('border-color', this.getBorderColorForStatus(n.data('status')));
            }
            n.style('z-index', 'auto');
        });
    }

    // -------------------------
    // CUSTOM ZOOM CONTROLS
    // -------------------------
    addZoomControls() {
        const container = document.getElementById('cy');
        if (!container) return;

        const zoomControls = document.createElement('div');
        zoomControls.className = 'zoom-controls';
        zoomControls.style.position = 'absolute';
        zoomControls.style.bottom = '10px';
        zoomControls.style.left = '10px';
        zoomControls.style.display = 'flex';
        zoomControls.style.flexDirection = 'column';
        zoomControls.style.gap = '5px';
        zoomControls.style.zIndex = '9999';

        // Helper to style buttons
        const makeBtn = (label) => {
            const btn = document.createElement('button');
            btn.innerHTML = label;
            btn.style.padding = '5px 8px';
            btn.style.fontSize = '16px';
            btn.style.cursor = 'pointer';
            btn.className = 'btn btn-sm btn-outline-primary';
            return btn;
        };

        // Zoom in
        const zoomInBtn = makeBtn('+');
        zoomInBtn.onclick = () => this.cy.zoom({
            level: this.cy.zoom() * 1.2,
            renderedPosition: { x: container.clientWidth / 2, y: container.clientHeight / 2 }
        });

        // Zoom out
        const zoomOutBtn = makeBtn('−');
        zoomOutBtn.onclick = () => this.cy.zoom({
            level: this.cy.zoom() * 0.8,
            renderedPosition: { x: container.clientWidth / 2, y: container.clientHeight / 2 }
        });

        // Reset view
        const resetBtn = makeBtn('⟳');
        resetBtn.onclick = () => this.cy.fit(null, 30);

        zoomControls.appendChild(zoomInBtn);
        zoomControls.appendChild(zoomOutBtn);
        zoomControls.appendChild(resetBtn);

        container.style.position = 'relative';
        container.appendChild(zoomControls);
    }

    // -------------------------
    // DEVICE UPDATES
    // -------------------------
    updateDevices(devices) {
        const currentNodes = this.cy.nodes().filter(n => n.data('id')?.startsWith('device_'));

        devices.forEach((device, i) => {
            const nodeId = `device_${device.id}`;
            let node = this.cy.getElementById(nodeId);

            if (node.empty()) {
                node = this.cy.add({
                    group: 'nodes',
                    data: {
                        id: nodeId,
                        label: this.getNodeLabel(device),
                        status: device.status,
                        device: device
                    }
                });

                // Connect device to router
                this.cy.add({
                    group: 'edges',
                    data: { id: `edge_${this.routerNodeId}_${nodeId}`, source: this.routerNodeId, target: nodeId }
                });

                this.addNodeAnimation(node, device.status, i);
            } else {
                const oldStatus = node.data('status');
                node.data('status', device.status);
                node.data('device', device);
                node.data('label', this.getNodeLabel(device));
                node.style('background-color', this.getColorForStatus(device.status));
                node.style('border-color', this.getBorderColorForStatus(device.status));

                if (oldStatus !== device.status) {
                    this.removeNodeAnimation(node);
                    this.addNodeAnimation(node, device.status, i);
                }
            }
        });

        // Remove devices no longer present
        currentNodes.forEach(node => {
            const deviceId = node.data('id').replace('device_', '');
            if (!devices.find(d => d.id == deviceId)) {
                this.removeNodeAnimation(node);
                this.cy.remove(`#${node.id()}`);
            }
        });

        // Re-run layout
        this.cy.layout({ name: 'cose', fit: true, padding: 20, animate: false }).run();
    }

    getNodeLabel(device) {
        return device.name || device.mac_address || 'Unknown';
    }
    
    getColorForStatus(status) {
        const map = { online: '#198754', offline: '#6c757d', pending: '#ffc107', intruder: '#dc3545' };
        return map[status] || '#007bff';
    }
    
    getBorderColorForStatus(status) {
        const map = { online: '#4cd98c', offline: '#a0a7b0', pending: '#ffd965', intruder: '#ff6b7a' };
        return map[status] || 'rgba(255, 255, 255, 0.4)';
    }

    // -------------------------
    // ANIMATIONS
    // -------------------------
    addNodeAnimation(node, status, index = 0) {
        const delay = index * 200;
        const key = `anim-${node.id()}`;
        let anim1, anim2;

        switch (status) {
            case 'online':
                anim1 = node.animation({ style: { 'background-color': '#28a745' }, duration: 600, delay });
                anim2 = node.animation({ style: { 'background-color': '#198754' }, duration: 600 });
                break;
            case 'pending':
                anim1 = node.animation({ style: { 'background-color': '#ffe066' }, duration: 500, delay });
                anim2 = node.animation({ style: { 'background-color': '#ffc107' }, duration: 500 });
                break;
            case 'intruder':
                anim1 = node.animation({ style: { 'background-color': '#ff4d4f', opacity: 0.7 }, duration: 400, delay });
                anim2 = node.animation({ style: { 'background-color': '#dc3545', opacity: 1 }, duration: 400 });
                break;
        }

        if (anim1 && anim2) {
            anim1.play().promise().then(() => anim2.play().loop(key));
            this.nodeAnimations.set(node.id(), key);
        }
    }

    removeNodeAnimation(node) {
        const key = this.nodeAnimations.get(node.id());
        if (key) {
            node.stopAnimation(key);
            this.nodeAnimations.delete(node.id());
        }
    }

    // -------------------------
    // JOIN REQUESTS
    // -------------------------
    updateJoinRequests(requests) {
        const currentIds = new Set(this.pendingRequests.keys());
        const newIds = new Set(requests.map(r => r.id));

        currentIds.forEach(id => {
            if (!newIds.has(id)) {
                this.removeRequestFromUI(id);
                this.pendingRequests.delete(id);
            }
        });

        requests.forEach(req => {
            if (!this.pendingRequests.has(req.id)) {
                this.pendingRequests.set(req.id, req);
                this.addRequestToSidebar(req);
            }
        });

        this.updateRequestCount();
    }

    addRequestToSidebar(request) {
        const html = `
            <div class="list-group-item alert-item join-request" data-request-id="${request.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${request.user_email}</h6>
                        <p class="mb-1 small">Device: ${request.device_name || 'Unknown'}</p>
                        <small class="text-muted">IP: ${request.ip_address}</small>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success approve-btn"><i class="fas fa-check"></i></button>
                        <button class="btn btn-outline-danger reject-btn"><i class="fas fa-times"></i></button>
                    </div>
                </div>
                <small class="text-muted">${new Date(request.created_at).toLocaleTimeString()}</small>
            </div>`;
        document.getElementById('join-requests-list').insertAdjacentHTML('afterbegin', html);
        this.attachButtonListeners();
    }

    removeRequestFromUI(id) {
        document.querySelector(`[data-request-id="${id}"]`)?.remove();
    }

    attachButtonListeners() {
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.onclick = e => this.approveRequest(e.target.closest('.alert-item').dataset.requestId);
        });
        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.onclick = e => this.rejectRequest(e.target.closest('.alert-item').dataset.requestId);
        });
    }

    async approveRequest(id) {
        try {
            const res = await fetch(`/n/live/api/join-request/${id}/approve/`, {
                method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
            });
            if (res.ok) {
                this.removeRequestFromUI(id);
                this.pendingRequests.delete(parseInt(id));
                this.updateRequestCount();
                this.showNotification('Request Approved', 'Join request approved', 'success');
            }
        } catch { this.showNotification('Error', 'Failed to approve request', 'danger'); }
    }

    async rejectRequest(id) {
        try {
            const res = await fetch(`/n/live/api/join-request/${id}/reject/`, {
                method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
            });
            if (res.ok) {
                this.removeRequestFromUI(id);
                this.pendingRequests.delete(parseInt(id));
                this.updateRequestCount();
                this.showNotification('Request Rejected', 'Join request rejected', 'warning');
            }
        } catch { this.showNotification('Error', 'Failed to reject request', 'danger'); }
    }

    updateRequestCount() {
        const c = this.pendingRequests.size;
        document.getElementById('request-count').textContent = c;
        const badge = document.getElementById('alert-badge');
        const totalAlerts = c + this.intruderAlerts.size;
        if (totalAlerts > 0) { 
            badge.textContent = totalAlerts; 
            badge.classList.remove('d-none'); 
        } else { 
            badge.classList.add('d-none'); 
        }
    }

    // -------------------------
    // INTRUDERS HANDLING
    // -------------------------
    updateIntruders(intruders) {
        const listEl = document.getElementById("intruder-alerts-list");
        const badgeEl = document.getElementById("intruder-count");

        // Remove old intruder nodes from Cytoscape
        this.intruderAlerts.forEach((node, id) => {
            if (!intruders.find(i => i.id === id)) {
                this.cy.getElementById(`intruder_${id}`)?.remove();
                clearTimeout(node.timeout);
                this.intruderAlerts.delete(id);
                document.querySelector(`[data-intruder-id="${id}"]`)?.remove();
            }
        });

        intruders.forEach((intruder, index) => {
            const nodeId = `intruder_${intruder.id}`;
            let node = this.cy.getElementById(nodeId);

            // Add intruder node to Cytoscape if missing
            if (node.empty()) {
                node = this.cy.add({
                    group: 'nodes',
                    data: { id: nodeId, label: intruder.ip_address, status: 'intruder' },
                    position: { x: 200 + index * 20, y: 200 + index * 20 }
                });

                // Connect intruder to router
                this.cy.add({
                    group: 'edges',
                    data: { id: `edge_${this.routerNodeId}_${nodeId}`, source: this.routerNodeId, target: nodeId }
                });

                this.addNodeAnimation(node, 'intruder', index);

                // Auto-remove after 1 minute
                const timeout = setTimeout(() => {
                    this.cy.getElementById(nodeId)?.remove();
                    this.intruderAlerts.delete(intruder.id);
                    this.updateIntruderBadge();
                    this.updateRequestCount(); // Update total alert badge
                }, 60000);

                this.intruderAlerts.set(intruder.id, { node, timeout });
            }

            // Add to sidebar if not present
            if (!listEl.querySelector(`[data-intruder-id="${intruder.id}"]`)) {
                const html = `
                    <div class="list-group-item alert-item intruder-alert" data-intruder-id="${intruder.id}">
                        <div>
                            Intruder from IP: ${intruder.ip_address} <br>
                            MAC: ${intruder.mac_address || "Unknown"} <br>
                            Note: ${intruder.note || "N/A"}
                        </div>
                        <small class="text-muted">${new Date(intruder.detected_at || intruder.created_at).toLocaleTimeString()}</small>
                    </div>`;
                listEl.insertAdjacentHTML('afterbegin', html);
            }
        });

        this.updateIntruderBadge();
        this.updateRequestCount(); // Update total alert badge
    }

    updateIntruderBadge() {
        const badgeEl = document.getElementById("intruder-count");
        const count = this.intruderAlerts.size;
        if (count > 0) {
            badgeEl.textContent = count;
            badgeEl.classList.remove("d-none");
        } else {
            badgeEl.classList.add("d-none");
        }
    }

    // -------------------------
    // NETWORK STATUS POLLING
    // -------------------------
    startPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
        this.fetchNetworkStatus();
        this.pollingInterval = setInterval(() => this.fetchNetworkStatus(), 5000);
        this.isPolling = true;
        this.updateSessionStatus(true);
    }

    stopPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
        this.pollingInterval = null;
        this.isPolling = false;
        this.updateSessionStatus(false);
    }

    // -------------------------
    // FETCH NETWORK STATUS (Updated)
    // -------------------------
    async fetchNetworkStatus() {
        try {
            const res = await fetch(`/n/live/api/network/${NETWORK_ID}/status/`);
            if (!res.ok) throw new Error(res.status);
            const data = await res.json();

            this.updateDevices(data.devices);
            this.updateJoinRequests(data.pending_requests);
            this.updateIntruders(data.intruders || []);
            this.updateNetworkInfo(data.network);

            // 🚨 Show flash message if provided by API
            if (data.flash_message) {
                this.showNotification("Alert", data.flash_message, "danger", 5000);
            }

        } catch {
            this.showNotification('Connection Error', 'Failed to fetch updates', 'danger');
        }
    }

    updateNetworkInfo(network) {
        const el = document.querySelector('.list-group-item:last-child strong');
        if (el) el.textContent = network.member_count;
    }

    // -------------------------
    // HELPERS
    // -------------------------
    showNodeDetails(node) {
        if (node.data('role') === 'router') return; // skip router details
        const d = node.data('device');
        if (!d) return;
        this.showNotification('Device Details', `
            <div class="text-start">
                <strong>${d.name || 'Unnamed Device'}</strong><br>
                <small>MAC: ${d.mac_address}</small><br>
                <small>IP: ${d.ip_address || 'N/A'}</small><br>
                <small>Status: <span class="badge bg-${this.getStatusBadgeColor(d.status)}">${d.status}</span></small>
            </div>`, 'info', 5000);
    }

    getStatusBadgeColor(status) {
        const map = { online: 'success', offline: 'secondary', pending: 'warning', intruder: 'danger' };
        return map[status] || 'info';
    }

    showNotification(title, message, type = "info", delay = 3000) {
        const container = document.getElementById("toast-container") || this.createToastContainer();
        
        const toast = document.createElement("div");
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body"><strong>${title}</strong><br>${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>`;
        container.appendChild(toast);
        new bootstrap.Toast(toast, { delay }).show();
    }

    createToastContainer() {
        const c = document.createElement('div');
        c.id = 'toast-container';
        c.className = 'toast-container position-fixed top-0 end-0 p-3';
        c.style.zIndex = '9999';
        document.body.appendChild(c);
        return c;
    }

    // -------------------------
    // ALERT BADGE CLICK - clears immediately
    // -------------------------
    initializeEventListeners() {
        document.getElementById('start-session-btn')?.addEventListener('click', () => this.startPolling());
        document.getElementById('end-session-btn')?.addEventListener('click', () => this.stopPolling());
        document.getElementById('refresh-network-btn')?.addEventListener('click', () => this.fetchNetworkStatus());

        // Clear intruder badge on click
        const intrudersTab = document.getElementById("intruders-tab");
        if (intrudersTab) {
            intrudersTab.addEventListener("click", () => {
                const badgeEl = document.getElementById("intruder-count");
                badgeEl.classList.add("d-none");

                // Optionally notify backend admins
                fetch(`/n/live/api/mark-intruders-read/`, {
                    method: "POST",
                    headers: { "X-CSRFToken": CSRF_TOKEN, "Content-Type": "application/json" },
                    body: JSON.stringify({})
                });
            });
        }
    }

    updateSessionStatus(active) {
        const el = document.getElementById('session-status');
        const start = document.getElementById('start-session-btn');
        const end = document.getElementById('end-session-btn');
        if (active) {
            el.className = 'alert alert-success';
            el.innerHTML = `<i class="fas fa-play-circle"></i> Session active - Polling every 5s`;
            start.disabled = true; end.disabled = false;
        } else {
            el.className = 'alert alert-info';
            el.innerHTML = '<i class="fas fa-info-circle"></i> Session not started';
            start.disabled = false; end.disabled = true;
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (typeof NETWORK_ID !== 'undefined') {
        window.networkLive = new NetworkLive();
    }
});