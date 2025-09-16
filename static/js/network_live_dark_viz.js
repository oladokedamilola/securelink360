// static/js/network_live_dark_viz.js
class NetworkLiveDarkViz {
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
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#007bff',
                        'label': 'data(label)',
                        'width': 12,
                        'height': 12,
                        'font-size': '6px',
                        'color': '#ffffff',
                        'text-outline-color': '#000000',
                        'text-outline-width': '1px',
                        'text-background-color': 'rgba(0, 0, 0, 0.7)',
                        'text-background-opacity': 1,
                        'text-background-padding': '2px',
                        'text-background-shape': 'roundrectangle',
                        'border-width': '2px',
                        'border-color': 'rgba(255, 255, 255, 0.4)',
                        'text-valign': 'center',
                        'text-halign': 'center'
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
                        'width': 1.5,
                        'line-color': 'rgba(255, 255, 255, 0.3)',
                        'target-arrow-color': 'rgba(255, 255, 255, 0.3)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'opacity': 0.6,
                        'arrow-scale': 1.2
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#0d6efd',
                        'target-arrow-color': '#0d6efd',
                        'opacity': 1,
                        'width': 2
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 70,
                nodeOverlap: 12,
                refresh: 12,
                fit: true,
                padding: 15,
                randomize: true,
                componentSpacing: 70,
                nodeRepulsion: 4000
            }
        });

        this.cy.on('tap', 'node', (event) => {
            const node = event.target;
            this.showNodeDetails(node);
        });

        this.cy.on('mouseover', 'node', (event) => {
            const node = event.target;
            node.style('border-width', '3px');
            node.style('border-color', '#ffffff');
            node.style('z-index', '9999');
        });

        this.cy.on('mouseout', 'node', (event) => {
            const node = event.target;
            const status = node.data('status');
            node.style('border-width', '2px');
            node.style('border-color', this.getBorderColorForStatus(status));
            node.style('z-index', 'auto');
        });
    }

    getBorderColorForStatus(status) {
        const colors = {
            'online': '#4cd98c',
            'offline': '#a0a7b0',
            'pending': '#ffd965',
            'intruder': '#ff6b7a'
        };
        return colors[status] || 'rgba(255, 255, 255, 0.4)';
    }

    updateDevices(devices) {
        const currentNodes = this.cy.elements().filter(node => node.data().id?.startsWith('device_'));

        devices.forEach((device, i) => {
            const nodeId = `device_${device.id}`;
            let node = this.cy.getElementById(nodeId);

            if (node.length === 0) {
                node = this.cy.add({
                    group: 'nodes',
                    data: {
                        id: nodeId,
                        label: this.getNodeLabel(device),
                        status: device.status,
                        device: device
                    },
                    position: {
                        x: Math.random() * 400 + 50,
                        y: Math.random() * 400 + 50
                    }
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

        currentNodes.forEach(node => {
            const deviceId = node.data('id').replace('device_', '');
            if (!devices.find(d => d.id == deviceId)) {
                this.removeNodeAnimation(node);
                node.remove();
            }
        });

        this.cy.layout({
            name: 'cose',
            fit: true,
            padding: 15,
            animate: true,
            animationDuration: 800,
            animationEasing: 'ease-out'
        }).run();
    }

    getNodeLabel(device) {
        return device.name || device.mac_address || 'Unknown';
    }

    getColorForStatus(status) {
        const colors = {
            'online': '#198754',
            'offline': '#6c757d',
            'pending': '#ffc107',
            'intruder': '#dc3545'
        };
        return colors[status] || '#007bff';
    }

    addNodeAnimation(node, status, index = 0) {
        const delay = index * 300;
        const animationKey = `animate-${node.id()}`;
        let anim1, anim2;

        switch (status) {
            case 'online':
                anim1 = node.animation({
                    style: { 'opacity': 0.8, 'width': 14, 'height': 14, 'background-color': '#28a745' },
                    duration: 1000,
                    delay
                });
                anim2 = node.animation({
                    style: { 'opacity': 1, 'width': 12, 'height': 12, 'background-color': '#198754' },
                    duration: 1000
                });
                break;

            case 'pending':
                anim1 = node.animation({
                    style: { 'width': 16, 'height': 16, 'background-color': '#ffe066' },
                    duration: 600,
                    delay
                });
                anim2 = node.animation({
                    style: { 'width': 12, 'height': 12, 'background-color': '#ffc107' },
                    duration: 600
                });
                break;

            case 'intruder':
                anim1 = node.animation({
                    style: { 'width': 18, 'height': 18, 'opacity': 0.7, 'background-color': '#ff4d4f' },
                    duration: 400,
                    delay
                });
                anim2 = node.animation({
                    style: { 'width': 12, 'height': 12, 'opacity': 1, 'background-color': '#dc3545' },
                    duration: 400
                });
                break;
        }

        if (anim1 && anim2) {
            anim1.play().promise().then(() => {
                anim2.play().loop(animationKey);
            });
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

        this.showNotification(
            'Device Details',
            `<div class="text-start">
                <strong>${device.name || 'Unnamed Device'}</strong><br>
                <small>MAC: ${device.mac_address}</small><br>
                <small>IP: ${device.ip_address || 'N/A'}</small><br>
                <small>Status: <span class="badge bg-${this.getStatusBadgeColor(device.status)}">${device.status}</span></small>
            </div>`,
            'info',
            5000
        );
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

    // keep existing polling + AJAX methods...
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (typeof NETWORK_ID !== 'undefined') {
        window.networkLive = new NetworkLiveDarkViz();
    }
});
