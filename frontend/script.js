const API_URL = "http://127.0.0.1:8001";



// ==========================================================
// Query elements
// ==========================================================

const queryInput =
    document.getElementById("query");

const analyzeButton =
    document.getElementById("analyze-button");

const resultBox =
    document.getElementById("result");

const statusBox =
    document.getElementById("status");



// ==========================================================
// Server management elements
// ==========================================================

const serverList =
    document.getElementById("server-list");

const addServerButton =
    document.getElementById("add-server-button");

const serverFormContainer =
    document.getElementById(
        "server-form-container"
    );

const serverFormTitle =
    document.getElementById(
        "server-form-title"
    );

const serverForm =
    document.getElementById(
        "server-form"
    );

const serverSourceIdInput =
    document.getElementById(
        "server-source-id"
    );

const serverHostInput =
    document.getElementById(
        "server-host"
    );

const serverUsernameInput =
    document.getElementById(
        "server-username"
    );

const serverRemotePathInput =
    document.getElementById(
        "server-remote-path"
    );

const serverLocalPathInput =
    document.getElementById(
        "server-local-path"
    );

const serverSyncIntervalInput =
    document.getElementById(
        "server-sync-interval"
    );

const serverEnabledInput =
    document.getElementById(
        "server-enabled"
    );

const saveServerButton =
    document.getElementById(
        "save-server-button"
    );

const cancelServerButton =
    document.getElementById(
        "cancel-server-button"
    );



// ==========================================================
// Rsync status elements
// ==========================================================

const syncStatusList =
    document.getElementById(
        "sync-status-list"
    );



// ==========================================================
// Current server form mode
// ==========================================================

let editingSourceId = null;



// ==========================================================
// Escape HTML
// ==========================================================

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;
}



// ==========================================================
// Convert server ID to display name
// ==========================================================

function createServerName(sourceId) {

    if (!sourceId) {
        return "Server";
    }

    return sourceId
        .split("-")
        .map(
            part =>
                part.charAt(0).toUpperCase() +
                part.slice(1)
        )
        .join(" ");
}



// ==========================================================
// Format timestamp
// ==========================================================

function formatTimestamp(timestamp) {

    if (!timestamp) {
        return "Not available";
    }

    const date =
        new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
        return "Not available";
    }

    return date.toLocaleString();
}



// ==========================================================
// Convert status to readable text
// ==========================================================

function formatSyncStatus(status) {

    if (!status) {
        return "Pending";
    }

    switch (status.toLowerCase()) {

        case "success":
        case "successful":
            return "Successful";

        case "failed":
            return "Failed";

        case "running":
            return "Running";

        case "pending":
            return "Pending";

        default:
            return status;
    }
}



// ==========================================================
// Update predefined local path
// ==========================================================

function updateLocalPath() {

    const sourceId =
        serverSourceIdInput.value.trim();

    if (!sourceId) {

        serverLocalPathInput.value =
            "./data/servers/";

        return;
    }

    serverLocalPathInput.value =
        `./data/servers/${sourceId}`;
}



// ==========================================================
// Load servers
// ==========================================================

async function loadServers() {

    try {

        const response =
            await fetch(
                `${API_URL}/servers`
            );

        if (!response.ok) {

            throw new Error(
                `Server request failed: ${response.status}`
            );
        }

        const servers =
            await response.json();

        renderServers(servers);

    } catch (error) {

        console.error(error);

        if (serverList) {

            serverList.innerHTML =
                "<p>Unable to load servers.</p>";
        }
    }
}



// ==========================================================
// Display servers
// ==========================================================

function renderServers(servers) {

    if (!serverList) {
        return;
    }

    if (
        !servers ||
        servers.length === 0
    ) {

        serverList.innerHTML =
            "<p>No synchronized servers configured.</p>";

        return;
    }

    serverList.innerHTML =
        servers
            .map(server => {

                const enabled =
                    Boolean(
                        server.enabled
                    );

                const parsedInterval =
                    Number(
                        server.sync_interval
                    );

                const syncInterval =
                    Number.isInteger(
                        parsedInterval
                    ) &&
                    parsedInterval > 0
                        ? parsedInterval
                        : 60;

                return `
                    <div class="server-card">

                        <h3>
                            ${escapeHtml(
                                server.name ||
                                createServerName(
                                    server.source_id
                                )
                            )}
                        </h3>

                        <p>
                            ID:
                            ${escapeHtml(
                                server.source_id
                            )}
                        </p>

                        <p>
                            Host:
                            ${escapeHtml(
                                server.host
                            )}
                        </p>

                        <p>
                            Log Path:
                            ${escapeHtml(
                                server.remote_path
                            )}
                        </p>

                        <p>
                            Local Path:
                            ${escapeHtml(
                                server.local_path
                            )}
                        </p>

                        <p>
                            Synchronization
                            ${
                                enabled
                                    ? "enabled"
                                    : "disabled"
                            }
                        </p>

                        ${
                            enabled
                                ? `
                                    <p>
                                        Next Sync:
                                        every
                                        ${syncInterval}
                                        seconds
                                    </p>
                                  `
                                : ""
                        }

                        <div class="server-actions">

                            <button
                                type="button"
                                class="edit-server-button"
                                data-source-id="${escapeHtml(
                                    server.source_id
                                )}"
                            >
                                Edit
                            </button>

                            <button
                                type="button"
                                class="delete-server-button"
                                data-source-id="${escapeHtml(
                                    server.source_id
                                )}"
                            >
                                Delete
                            </button>

                        </div>

                    </div>
                `;
            })
            .join("");

    attachServerActionListeners();
}



// ==========================================================
// Attach Edit/Delete button listeners
// ==========================================================

function attachServerActionListeners() {

    const editButtons =
        document.querySelectorAll(
            ".edit-server-button"
        );

    const deleteButtons =
        document.querySelectorAll(
            ".delete-server-button"
        );

    editButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    openEditServerForm(
                        button.dataset.sourceId
                    );
                }
            );
        }
    );

    deleteButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    deleteServer(
                        button.dataset.sourceId
                    );
                }
            );
        }
    );
}



// ==========================================================
// Load one server
// ==========================================================

async function getServer(
    sourceId
) {

    const response =
        await fetch(
            `${API_URL}/servers/${encodeURIComponent(
                sourceId
            )}`
        );

    if (!response.ok) {

        let message =
            `Failed to load server: ${response.status}`;

        try {

            const errorData =
                await response.json();

            if (errorData.detail) {
                message =
                    errorData.detail;
            }

        } catch (error) {

            console.error(
                "Unable to parse server error:",
                error
            );
        }

        throw new Error(
            message
        );
    }

    return response.json();
}



// ==========================================================
// Open Add Server form
// ==========================================================

function openAddServerForm() {

    if (!serverFormContainer) {
        return;
    }

    editingSourceId = null;

    serverFormTitle.textContent =
        "Add Server";

    serverSourceIdInput.value =
        "";

    serverHostInput.value =
        "";

    serverUsernameInput.value =
        "";

    serverRemotePathInput.value =
        "";

    serverLocalPathInput.value =
        "./data/servers/";

    serverSyncIntervalInput.value =
        "60";

    serverEnabledInput.checked =
        true;

    serverSourceIdInput.disabled =
        false;

    saveServerButton.textContent =
        "Add Server";

    serverFormContainer.style.display =
        "block";
}



// ==========================================================
// Open Edit Server form
// ==========================================================

async function openEditServerForm(
    sourceId
) {

    try {

        const server =
            await getServer(
                sourceId
            );

        editingSourceId =
            server.source_id;

        serverFormTitle.textContent =
            "Edit Server";

        serverSourceIdInput.value =
            server.source_id;

        serverHostInput.value =
            server.host || "";

        serverUsernameInput.value =
            server.username || "";

        serverRemotePathInput.value =
            server.remote_path || "";

        serverLocalPathInput.value =
            server.local_path ||
            `./data/servers/${server.source_id}`;

        serverSyncIntervalInput.value =
            Number(
                server.sync_interval || 60
            );

        serverEnabledInput.checked =
            Boolean(
                server.enabled
            );

        /*
         * The API requires the source_id in the URL
         * and request body to match, so the ID is
         * kept fixed while editing.
         */
        serverSourceIdInput.disabled =
            true;

        saveServerButton.textContent =
            "Save Changes";

        serverFormContainer.style.display =
            "block";

    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            "Unable to load server."
        );
    }
}



// ==========================================================
// Close Server form
// ==========================================================

function closeServerForm() {

    if (!serverFormContainer) {
        return;
    }

    editingSourceId = null;

    serverFormContainer.style.display =
        "none";

    if (serverForm) {
        serverForm.reset();
    }

    serverSourceIdInput.disabled =
        false;

    serverLocalPathInput.value =
        "./data/servers/";

    serverSyncIntervalInput.value =
        "60";

    serverEnabledInput.checked =
        true;
}



// ==========================================================
// Save Server
// ==========================================================

async function saveServer() {

    const sourceId =
        serverSourceIdInput.value.trim();

    const host =
        serverHostInput.value.trim();

    const username =
        serverUsernameInput.value.trim();

    const remotePath =
        serverRemotePathInput.value.trim();

    const localPath =
        `./data/servers/${sourceId}`;

    const syncInterval =
        Number(
            serverSyncIntervalInput.value
        );



    // ------------------------------------------------------
    // Validate required fields
    // ------------------------------------------------------

    if (!sourceId) {

        alert(
            "Please enter a Server ID."
        );

        return;
    }

    if (!host) {

        alert(
            "Please enter the IP Address / Host."
        );

        return;
    }

    if (!username) {

        alert(
            "Please enter the SSH Username."
        );

        return;
    }

    if (!remotePath) {

        alert(
            "Please enter the Log Path."
        );

        return;
    }

    if (
        !Number.isInteger(syncInterval) ||
        syncInterval < 1
    ) {

        alert(
            "Rsync Interval must be a whole number greater than 0."
        );

        return;
    }



    // ------------------------------------------------------
    // Build server object
    // ------------------------------------------------------

    const server = {

        source_id:
            sourceId,

        name:
            createServerName(
                sourceId
            ),

        host:
            host,

        username:
            username,

        remote_path:
            remotePath,

        local_path:
            localPath,

        enabled:
            serverEnabledInput.checked,

        sync_interval:
            syncInterval
    };



    // ------------------------------------------------------
    // Disable button while saving
    // ------------------------------------------------------

    saveServerButton.disabled =
        true;

    saveServerButton.textContent =
        editingSourceId
            ? "Saving..."
            : "Adding...";



    try {

        const isEditing =
            editingSourceId !== null;

        const url =
            isEditing
                ? `${API_URL}/servers/${encodeURIComponent(
                    editingSourceId
                  )}`
                : `${API_URL}/servers`;

        const method =
            isEditing
                ? "PUT"
                : "POST";

        const response =
            await fetch(
                url,
                {
                    method: method,

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            server
                        )
                }
            );



        if (!response.ok) {

            let message =
                isEditing
                    ? `Failed to update server: ${response.status}`
                    : `Failed to add server: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    message =
                        errorData.detail;
                }

            } catch (error) {

                console.error(
                    "Unable to parse server error:",
                    error
                );
            }

            throw new Error(
                message
            );
        }



        closeServerForm();

        await loadServers();

        await loadSyncStatus();



    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            (
                editingSourceId
                    ? "Unable to update server."
                    : "Unable to add server."
            )
        );

    } finally {

        saveServerButton.disabled =
            false;

        saveServerButton.textContent =
            editingSourceId
                ? "Save Changes"
                : "Add Server";
    }
}



// ==========================================================
// Delete Server
// ==========================================================

async function deleteServer(
    sourceId
) {

    const confirmed =
        window.confirm(
            `Are you sure you want to delete ${createServerName(
                sourceId
            )}?`
        );

    if (!confirmed) {
        return;
    }



    try {

        const response =
            await fetch(
                `${API_URL}/servers/${encodeURIComponent(
                    sourceId
                )}`,
                {
                    method: "DELETE"
                }
            );



        if (!response.ok) {

            let message =
                `Failed to delete server: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    message =
                        errorData.detail;
                }

            } catch (error) {

                console.error(
                    "Unable to parse delete error:",
                    error
                );
            }

            throw new Error(
                message
            );
        }



        await loadServers();

        await loadSyncStatus();



    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            "Unable to delete server."
        );
    }
}



// ==========================================================
// Load live rsync status
// ==========================================================

async function loadSyncStatus() {

    if (!syncStatusList) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API_URL}/servers/sync-status`
            );

        if (!response.ok) {

            throw new Error(
                `Sync status request failed: ${response.status}`
            );
        }

        const syncStatuses =
            await response.json();

        renderSyncStatus(
            syncStatuses
        );

    } catch (error) {

        console.error(
            "Unable to load synchronization status:",
            error
        );

        syncStatusList.innerHTML =
            "<p>Unable to load synchronization status.</p>";
    }
}



// ==========================================================
// Display live rsync status
// ==========================================================

function renderSyncStatus(
    syncStatuses
) {

    if (!syncStatusList) {
        return;
    }

    if (
        !syncStatuses ||
        syncStatuses.length === 0
    ) {

        syncStatusList.innerHTML =
            "<p>No synchronization servers configured.</p>";

        return;
    }

    syncStatusList.innerHTML =
        syncStatuses
            .map(server => {

                const statusData =
                    server.status || {};

                const status =
                    formatSyncStatus(
                        statusData.status
                    );

                const nextSync =
                    server.enabled
                        ? server.next_sync_in
                        : null;

                let nextSyncText;

                if (!server.enabled) {

                    nextSyncText =
                        "Synchronization disabled.";

                } else if (
                    nextSync === null ||
                    nextSync === undefined
                ) {

                    nextSyncText =
                        "Next Sync: Pending";

                } else if (
                    nextSync <= 0
                ) {

                    nextSyncText =
                        "Next Sync: Due";

                } else {

                    nextSyncText =
                        `Next Sync: ${nextSync} seconds`;
                }

                return `
                    <div class="sync-status-card">

                        <h3>
                            ${escapeHtml(
                                server.name ||
                                createServerName(
                                    server.source_id
                                )
                            )}
                        </h3>

                        <p>
                            Status:
                            <strong>
                                ${escapeHtml(
                                    status
                                )}
                            </strong>
                        </p>

                        <p>
                            Interval:
                            ${escapeHtml(
                                server.sync_interval
                            )}
                            seconds
                        </p>

                        <p>
                            ${escapeHtml(
                                nextSyncText
                            )}
                        </p>

                        <p>
                            Last Attempt:
                            ${escapeHtml(
                                formatTimestamp(
                                    statusData.last_attempted_at
                                )
                            )}
                        </p>

                        <p>
                            Last Successful:
                            ${escapeHtml(
                                formatTimestamp(
                                    statusData.last_successful_at
                                )
                            )}
                        </p>

                        ${
                            statusData.error_message
                                ? `
                                    <p class="sync-error">
                                        Error:
                                        ${escapeHtml(
                                            statusData.error_message
                                        )}
                                    </p>
                                  `
                                : ""
                        }

                    </div>
                `;
            })
            .join("");
}



// ==========================================================
// Analyse security query
// ==========================================================

async function analyzeSecurity() {

    const query =
        queryInput.value.trim();

    if (!query) {

        statusBox.textContent =
            "Please enter a security query.";

        resultBox.textContent =
            "No query provided.";

        return;
    }

    analyzeButton.disabled =
        true;

    statusBox.textContent =
        "Analysing security query...";

    resultBox.textContent =
        "Please wait while the RAG + LLM pipeline processes your request.";

    try {

        const response =
            await fetch(
                `${API_URL}/analyze`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            query: query
                        })
                }
            );

        if (!response.ok) {

            let message =
                `API request failed: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    message =
                        errorData.detail;
                }

            } catch (error) {

                console.error(
                    "Unable to parse error response:",
                    error
                );
            }

            throw new Error(
                message
            );
        }

        const data =
            await response.json();

        resultBox.textContent =
            data.answer || "";

        statusBox.textContent =
            "Analysis completed successfully.";

    } catch (error) {

        console.error(error);

        statusBox.textContent =
            "Analysis failed.";

        resultBox.textContent =
            error.message ||
            (
                "Unable to connect to the " +
                "LogLlamalyzer API. " +
                "Make sure the FastAPI server " +
                "is running."
            );

    } finally {

        analyzeButton.disabled =
            false;
    }
}



// ==========================================================
// Event listeners
// ==========================================================

if (addServerButton) {

    addServerButton.addEventListener(
        "click",
        openAddServerForm
    );
}



if (cancelServerButton) {

    cancelServerButton.addEventListener(
        "click",
        closeServerForm
    );
}



if (saveServerButton) {

    saveServerButton.addEventListener(
        "click",
        saveServer
    );
}



if (serverSourceIdInput) {

    serverSourceIdInput.addEventListener(
        "input",
        updateLocalPath
    );
}



if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        analyzeSecurity
    );
}



// ==========================================================
// Initial page load
// ==========================================================

loadServers();

loadSyncStatus();



// ==========================================================
// Automatic synchronization status refresh
// ==========================================================

setInterval(
    loadSyncStatus,
    10000
);