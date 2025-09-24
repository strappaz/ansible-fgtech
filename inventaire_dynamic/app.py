import docker
from flask import Flask, render_template_string
import sys

app = Flask(__name__)

# Full HTML template for the main page
MAIN_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docker Container Scanner</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 2rem;
        }
        .container {
            background-color: white;
            padding: 2rem;
            border-radius: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            max-width: 90%;
            width: 100%;
        }
        #scan-button {
            transition: all 0.3s ease;
        }
        #scan-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 0.5rem;
        }
        th, td {
            text-align: left;
            padding: 1rem;
        }
        thead th {
            background-color: #e5e7eb;
            color: #4b5563;
        }
        thead tr {
            border-radius: 1.5rem;
        }
        tbody tr {
            background-color: #f9fafb;
            transition: transform 0.2s ease;
            border-radius: 1.5rem;
        }
        tbody tr:hover {
            transform: scale(1.01);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status-running {
            background-color: #d1fae5;
            color: #065f46;
        }
        .status-exited {
            background-color: #fee2e2;
            color: #991b1b;
        }
        .loading-indicator {
            display: none;
            text-align: center;
            margin-top: 1rem;
            color: #6b7280;
        }
        @keyframes spin {
            from {
                transform: rotate(0deg);
            }
            to {
                transform: rotate(360deg);
            }
        }
        .spinner {
            display: inline-block;
            width: 1.5rem;
            height: 1.5rem;
            border: 3px solid #cbd5e1;
            border-top: 3px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body class="bg-gray-100 flex flex-col items-center justify-center p-8">
    <div class="container rounded-3xl shadow-xl p-8 max-w-4xl w-full">
        <h1 class="text-3xl font-bold text-center mb-6">Docker Container Scanner</h1>
        <p class="text-center text-gray-600 mb-8">Click the button below to scan for active Docker containers on the local machine.</p>

        <div class="flex flex-col items-center justify-center space-y-4">
            <button id="scan-button" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full shadow-lg">
                Scan for Containers
            </button>
            <div id="loading-indicator" class="loading-indicator">
                <span class="spinner"></span>
                <span class="ml-2">Scanning...</span>
            </div>
        </div>

        <div id="results" class="mt-8 overflow-x-auto">
            <!-- Results will be displayed here -->
        </div>
    </div>

    <script>
        document.getElementById('scan-button').addEventListener('click', async () => {
            const resultsDiv = document.getElementById('results');
            const loadingIndicator = document.getElementById('loading-indicator');
            const scanButton = document.getElementById('scan-button');

            resultsDiv.innerHTML = '';
            loadingIndicator.style.display = 'flex';
            scanButton.disabled = true;
            scanButton.classList.add('opacity-50', 'cursor-not-allowed');

            try {
                const response = await fetch('/api/scan');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const html = await response.text();
                resultsDiv.innerHTML = html;

            } catch (error) {
                console.error('Error fetching data:', error);
                resultsDiv.innerHTML = `<p class="text-center text-red-500">Failed to load data: ${error.message}. Please ensure the Flask server is running and the Docker daemon is accessible.</p>`;
            } finally {
                loadingIndicator.style.display = 'none';
                scanButton.disabled = false;
                scanButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        });
    </script>
</body>
</html>
"""

# HTML template for the table body to be inserted into the main page
TABLE_TEMPLATE = """
<table class="table-auto rounded-xl overflow-hidden">
    <thead>
        <tr class="rounded-xl">
            <th class="rounded-tl-xl">Container Name</th>
            <th>Image</th>
            <th>Status</th>
            <th class="rounded-tr-xl">Ports</th>
        </tr>
    </thead>
    <tbody>
        {% for container in containers %}
        <tr>
            <td class="container-name">{{ container.name }}</td>
            <td>{{ container.image }}</td>
            <td><span class="status-badge status-{{ 'running' if container.status == 'running' else 'exited' }}">{{ container.status }}</span></td>
            <td>{{ container.ports }}</td>
        </tr>
        {% else %}
        <tr>
            <td colspan="4">No active containers found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
"""


def test_docker_connection():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except docker.errors.DockerException as e:
        print(f"Error: Unable to connect to the Docker daemon. Is Docker running?", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Docker connection test: {e}", file=sys.stderr)
        return None


@app.route('/')
def main_page():
    return render_template_string(MAIN_PAGE_TEMPLATE)


@app.route('/api/scan')
def get_docker_containers():
    client = test_docker_connection()
    if client is None:
        return "<h1>Error: Unable to connect to the Docker daemon.</h1><p>Please ensure the Docker service is running.</p>"

    try:
        all_containers = client.containers.list(all=True)

        containers_data = []
        for container in all_containers:
            ports_list = []
            if container.ports:
                for k, v in container.ports.items():
                    if v:
                        for binding in v:
                            public_port = binding.get('HostPort', '')
                            private_port = k.split('/')[0]
                            port_type = k.split('/')[1]
                            ports_list.append(f"{public_port}->{private_port}/{port_type}")

            ports_str = ", ".join(ports_list)

            containers_data.append({
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else 'N/A',
                'status': container.status,
                'ports': ports_str
            })

        return render_template_string(TABLE_TEMPLATE, containers=containers_data)

    except Exception as e:
        error_message = f"<h1>Error: Unable to retrieve container list.</h1>" \
                        f"<p>An unexpected error occurred:</p>" \
                        f"<pre>{e}</pre>" \
                        f"<p>Please check your Docker daemon's status and logs for more information.</p>"
        return error_message


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
