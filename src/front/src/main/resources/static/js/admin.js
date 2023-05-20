function createNodeBox(node) {
    let nodeBox = document.createElement("div");
    nodeBox.id = "node-" + node.id;
    nodeBox.classList.add("rounded", "p-3", "bg-light", "border", "node-box");

    let flexContainer = document.createElement("div");
    flexContainer.style.display = "flex";
    flexContainer.style.justifyContent = "space-between";
    flexContainer.style.alignItems = "center";

    let title = document.createElement("h5");
    title.style.margin = "0";  // Reset margin
    title.innerText = "Node " + node.id;

    let status = document.createElement("p");
    status.style.margin = "0";  // Reset margin
    let statusCircle = document.createElement("span");
    statusCircle.classList.add("status-circle");
    statusCircle.style.backgroundColor = node.alive ? "green" : "red";
    status.appendChild(statusCircle);

    let statusText = document.createElement("span");
    statusText.classList.add("status-text");  // This is your new class
    statusText.appendChild(document.createTextNode(" " + node.host + ":" + node.port));
    // statusText.appendChild(document.createTextNode(" " + (node.alive ? "Online" : "Offline") + " (" + node.host + ":" + node.port + ")"));
    status.appendChild(statusText);

    flexContainer.appendChild(title);
    flexContainer.appendChild(status);

    nodeBox.appendChild(flexContainer);

    let logs = document.createElement("pre");
    logs.style.display = 'none';
    nodeBox.appendChild(logs);

    nodeBox.addEventListener("click", function(event) {
        event.stopPropagation();
        this.classList.toggle('active');
        let logs = this.querySelector('pre');
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


