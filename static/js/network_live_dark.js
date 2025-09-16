// static/js/network_live_dark.js
class NetworkLiveDark {
    constructor() {
        this.cy = null;
        this.pendingRequests = new Map();
        this.pollingInterval = null;
        this.isPolling = false;
        this.nodeAnimations = new Map();
        
        this.initializeCytoscape();
        this.initializeEventListeners();
        this.startPolling();
    }

    initializeCytoscape() {
        // Initialize Cytoscape instance with dark theme
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#007bff',
                        'label': 'data(label)',
                        'width': 20,
                        'height': 20,
                        'font-size': '8px',
                        'color': '#ffffff',
                        'text-outline-color': '#000',
                        'text-outline-width': '1px',
                        'text-background-color': 'rgba(0, 0, 0, 0.7)',
                        'text-background-opacity': 1,
                        'text-background-padding': '2px',
                        'text-background-shape': 'roundrectangle',
                        'border-width': '2px',
                        'border-color': 'rgba(255, 255, 255, 0.3)',
                        'border-opacity': 0.7
                    }
                },
                {
                    selector: 'node[status = "online"]',
                    style: {
                        'background-color': '#198754',
                        'border-color': '#4cd98c'
                    }
                },
                {
                    selector: 'node[status = "offline"]',
                    style: {
                        'background-color': '#6c757d',
                        'border-color': '#a0a7b0',
                        'opacity': 0.6
                    }
                },
                {
                    selector: 'node[status = "pending"]',
                    style: {
                        'background-color': '#ffc107',
                        'border-color': '#ffd965',
                        'color': '#000000'
                    }
                },
                {
                    selector: 'node[status = "intruder"]',
                    style: {
                        'background-color': '#dc3545',
                        'border-color': '#ff6b7a'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': 'rgba(108, 117, 125, 0.6)',
                        'target-arrow-color': 'rgba(108, 117, 125, 0.6)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.7
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#0d6efd',
                        'target-arrow-color': '#0d6efd',
                        'opacity': 1
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 80,
                nodeOverlap: 15,
                refresh: 15,
                fit: true,
                padding: 20,
                randomize: true,
                componentSpacing: 80,
                nodeRepulsion: 4500
            }
        });

        // Add event listeners for interactivity
        this.cy.on('tap', 'node', (event) => {
            const node = event.target;
            this.showNodeDetails(node);
        });

        this.cy.on('mouseover', 'node', (event) => {
            const node = event.target;
            node.style('border-width', '3px');
            node.style('border-color', '#ffffff');
        });

        this.cy.on('mouseout', 'node', (event) => {
            const node = event.target;
            const status = node.data('status');
            node.style('border-width', '2px');
            node.style('border-color', this.getBorderColorForStatus(status));
        });
    }

    getBorderColorForStatus(status) {
        const colors = {
            'online': '#4cd98c',
            'offline': '#a0a7b0',
            'pending': '#ffd965',
            'intruder': '#ff6b7a'
        };
        return colors[status] || 'rgba(255, 255, 255, 0.3)';
    }

    // ... (keep all the existing methods from your AJAX version)

    updateDevices(devices) {
        // Clear existing device nodes but keep animations
        const currentNodes = this.cy.elements().filter(node => node.data().id?.startsWith('device_'));
        
        devices.forEach(device => {
            const nodeId = `device_${device.id}`;
            let node = this.cy.getElementById(nodeId);
            
            if (node.length === 0) {
                // Create new node
                node = this.cy.add({
                    group: 'nodes',
                    data: {
                        id: nodeId,
                        label: device.name || device.mac_address.slice(-4),
                        status: device.status,
                        device: device
                    },
                    position: {
                        x: Math.random() * 300 + 50,
                        y: Math.random() * 300 + 50
                    }
                });
                
                // Add animation for new nodes
                this.addNodeAnimation(node, device.status);
            } else {
                // Update existing node
                node.data('status', device.status);
                node.style('background-color', this.getColorForStatus(device.status));
                node.style('border-color', this.getBorderColorForStatus(device.status));
                
                // Update animation if status changed
                if (node.data('previousStatus') !== device.status) {
                    this.removeNodeAnimation(node);
                    this.addNodeAnimation(node, device.status);
                    node.data('previousStatus', device.status);
                }
            }
        });
        
        // Remove nodes that no longer exist
        currentNodes.forEach(node => {
            const deviceId = node.data('id').replace('device_', '');
            if (!devices.find(d => d.id == deviceId)) {
                this.removeNodeAnimation(node);
                node.remove();
            }
        });
        
        // Refresh layout with smooth transition
        this.cy.layout({
            name: 'cose',
            fit: true,
            padding: 20,
            animate: true,
            animationDuration: 500
        }).run();
    }

    addNodeAnimation(node, status) {
        const animationKey = `blink-${node.id()}`;
        
        switch(status) {
            case 'online':
                node.animation({
                    style: { 'opacity': 0.7 },
                    duration: 1000
                }, {
                    style: { 'opacity': 1 },
                    duration: 1000
                }).play().loop(animationKey);
                break;
                
            case 'pending':
                node.animation({
                    style: { 'scale': 1.1 },
                    duration: 750
                }, {
                    style: { 'scale': 1 },
                    duration: 750
                }).play().loop(animationKey);
                break;
                
            case 'intruder':
                node.animation({
                    style: { 'scale': 1.2, 'opacity': 0.6 },
                    duration: 400
                }, {
                    style: { 'scale': 1, 'opacity': 1 },
                    duration: 400
                }).play().loop(animationKey);
                break;
        }
        
        this.nodeAnimations.set(node.id(), animationKey);
    }

    removeNodeAnimation(node) {
        const animationKey = this.nodeAnimations.get(node.id());
        if (animationKey) {
            node.stopAnimation(animationKey);
            this.nodeAnimations.delete(node.id());
        }
    }

    showNodeDetails(node) {
        const device = node.data('device');
        if (!device) return;

        // Create a simple popup for node details
        const detailsHtml = `
            <div class="card bg-dark border-secondary">
                <div class="card-header">
                    <h6 class="mb-0">Device Details</h6>
                </div>
                <div class="card-body">
                    <p><strong>Name:</strong> ${device.name || 'Unnamed'}</p>
                    <p><strong>MAC:</strong> ${device.mac_address}</p>
                    <p><strong>IP:</strong> ${device.ip_address || 'N/A'}</p>
                    <p><strong>Status:</strong> 
                        <span class="badge bg-${this.getStatusBadgeColor(device.status)}">
                            ${device.status}
                        </span>
                    </p>
                    <p><strong>User:</strong> ${device.user_email}</p>
                </div>
            </div>
        `;

        // You could use a modal or toast for this
        this.showNotification('Device Details', detailsHtml, 'info', 5000);
    }

    getStatusBadgeColor(status) {
        const colors = {
            'online': 'success',
            'offline': 'secondary',
            'pending': 'warning',
            'intruder': 'danger'
        };
        return colors[status] || 'info';
    }

    // ... (keep all other existing methods)
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    if (typeof NETWORK_ID !== 'undefined') {
        window.networkLive = new NetworkLiveDark();
    }
});