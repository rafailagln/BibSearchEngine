function createNodeBox(node) {
    let nodeBox = document.createElement("div");
    nodeBox.id = "node-" + node.id;
    nodeBox.classList.add("rounded", "p-3", "bg-light", "border", "node-box");

    let title = document.createElement("h5");
    title.innerText = "Node " + node.id;
    nodeBox.appendChild(title);

    let status = document.createElement("p");
    let statusCircle = document.createElement("span");
    statusCircle.classList.add("status-circle");
    statusCircle.style.backgroundColor = node.alive ? "green" : "red";
    status.appendChild(statusCircle);
    status.appendChild(document.createTextNode(" " + (node.alive ? "Online" : "Offline")));
    nodeBox.appendChild(status);

    let host = document.createElement("p");
    host.innerText = "Host: " + node.host;
    nodeBox.appendChild(host);

    let port = document.createElement("p");
    port.innerText = "Port: " + node.port;
    nodeBox.appendChild(port);

    let logs = document.createElement("pre");
    logs.style.display = 'none';
    nodeBox.appendChild(logs);

    nodeBox.addEventListener("click", function(event) {
        event.stopPropagation();
        let activeBox = document.querySelector('.node-box.active');
        if(activeBox && activeBox !== this) {
            let activeLogs = activeBox.querySelector('pre');
            activeLogs.style.display = 'none';
            activeBox.classList.remove('active');
        }
        this.classList.toggle('active');
        if(this.classList.contains('active')) {
            axios.defaults.baseURL = 'http://127.0.0.1:5000';
            axios.get('/api/logs/' + node.id, {
                auth: {
                    username: 'testuser',
                    password: 'testpass'
                }
            })
                .then(function (response) {
                    logs.innerText = response.data.log_data;
                    logs.style.display = 'block';
                })
                .catch(function (error) {
                    console.log(error);
                });
        } else {
            logs.style.display = 'none';
        }
    });

    return nodeBox;
}

let nodes = JSON.parse(window.config).nodes;
let nodesContainer = document.getElementById("nodes");
for(let node of nodes) {
    let nodeBox = createNodeBox(node);
    nodesContainer.appendChild(nodeBox);
}

// document.addEventListener('click', function() {
//     let activeBox = document.querySelector('.node-box.active');
//     if(activeBox) {
//         let activeLogs = activeBox.querySelector('pre');
//         activeLogs.style.display = 'none';
//         activeBox.classList.remove('active');
//     }
// }, true);

// SSE listener
const eventSource = new EventSource('/api/sse');

eventSource.addEventListener('message', function(event) {
    const nodeStatus = JSON.parse(event.data);
    const nodeBox = document.getElementById("node-" + nodeStatus.id);

    if (nodeBox) {
        const statusCircle = nodeBox.querySelector('.status-circle');
        const status = nodeBox.querySelector('p:nth-child(2)');
        if (statusCircle) {
            if (nodeStatus.online) {
                statusCircle.style.backgroundColor = "green";
                status.childNodes[1].nodeValue = " Online";  // Change only the text
            } else {
                statusCircle.style.backgroundColor = "red";
                status.childNodes[1].nodeValue = " Offline";  // Change only the text
            }
        }
    }
}, false);


