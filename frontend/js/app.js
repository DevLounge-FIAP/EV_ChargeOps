/**
 * EV ChargeOps — Frontend Application Logic
 * Integracao com FastAPI & Assistente IA EVA (GoodWe + FIAP)
 */

const API_BASE_URL = "http://localhost:8000";

// Estado global da aplicacao
const state = {
    unit: "Apto 42B",
    chatHistory: [],
    apiOnline: false
};

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initUnitInput();
    initChat();
    initSimulator();
    initHistory();
    checkApiHealth();

    // Polling suave de status a cada 30 segundos
    setInterval(checkApiHealth, 30000);
});

// ==========================================================================
// 1. Healthcheck e Status da API
// ==========================================================================
async function checkApiHealth() {
    const statusBadge = document.getElementById("api-status");
    const statusLabel = document.getElementById("status-label");

    try {
        const res = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
        if (res.ok) {
            state.apiOnline = true;
            statusBadge.classList.remove("offline");
            statusLabel.textContent = "API FastAPI Online (8000)";
            loadMetrics();
        } else {
            throw new Error();
        }
    } catch (e) {
        state.apiOnline = false;
        statusBadge.classList.add("offline");
        statusLabel.textContent = "API Offline";
        resetMetrics();
    }
}

// ==========================================================================
// 2. Navegacao entre Abas
// ==========================================================================
function initTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTabId = btn.getAttribute("data-tab");

            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetPane = document.getElementById(targetTabId);
            if (targetPane) {
                targetPane.classList.add("active");
            }
        });
    });
}

// ==========================================================================
// 3. Entrada de Unidade do Condomino
// ==========================================================================
function initUnitInput() {
    const unitInput = document.getElementById("user-unit-input");
    if (unitInput) {
        unitInput.addEventListener("change", (e) => {
            state.unit = e.target.value.trim() || "Geral";
        });
    }
}

// ==========================================================================
// 4. Metricas e KPIs
// ==========================================================================
async function loadMetrics() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/sessions/metrics`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("kpi-total-kwh").textContent = `${data.total_energy_kwh.toFixed(1).replace('.', ',')} kWh`;
            document.getElementById("kpi-total-revenue").textContent = `R$ ${data.total_revenue_brl.toFixed(2).replace('.', ',')}`;
            document.getElementById("kpi-current-rate").textContent = `R$ ${data.current_rate_per_kwh.toFixed(2).replace('.', ',')}`;
        }
    } catch (e) {
        resetMetrics();
    }
}

function resetMetrics() {
    document.getElementById("kpi-total-kwh").textContent = "0,0 kWh";
    document.getElementById("kpi-total-revenue").textContent = "R$ 0,00";
    document.getElementById("kpi-current-rate").textContent = "R$ 0,95";
}

// ==========================================================================
// 5. Modulo Chatbot IA EVA
// ==========================================================================
function initChat() {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const quickChips = document.querySelectorAll(".chip-btn");

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            sendMessage(text);
            chatInput.value = "";
        }
    });

    quickChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            if (prompt) {
                sendMessage(prompt);
            }
        });
    });
}

async function sendMessage(text) {
    appendMessage("user", text);
    const typingId = showTypingIndicator();

    try {
        let reply = "";
        if (state.apiOnline) {
            const res = await fetch(`${API_BASE_URL}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    user_id: state.unit,
                    history: state.chatHistory.slice(-4)
                })
            });

            if (res.ok) {
                const data = await res.json();
                reply = data.reply;
            } else {
                throw new Error();
            }
        } else {
            await new Promise(r => setTimeout(r, 400));
            reply = generateOfflineResponse(text);
        }

        removeTypingIndicator(typingId);
        appendMessage("assistant", reply);

        state.chatHistory.push({ role: "user", content: text });
        state.chatHistory.push({ role: "assistant", content: reply });
    } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage("assistant", "Instabilidade na conexao com a API. Certifique-se de que o backend FastAPI esteja ativo na porta 8000.");
    }
}

function appendMessage(sender, text) {
    const chatBox = document.getElementById("chat-messages-box");
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const formattedText = formatMarkdown(text);
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    row.innerHTML = `
        <div class="msg-bubble">
            <div class="msg-sender">${sender === 'user' ? state.unit : 'EVA • Assistente IA'}</div>
            <div class="msg-text">${formattedText}</div>
            <div class="msg-time">${timeStr}</div>
        </div>
    `;

    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById("chat-messages-box");
    const id = "typing-" + Date.now();
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.id = id;
    row.innerHTML = `
        <div class="msg-bubble">
            <div class="msg-sender">EVA processando...</div>
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n- /g, '<br>&bull; ')
        .replace(/\n/g, '<br>');
}

function generateOfflineResponse(text) {
    const m = text.toLowerCase();
    if (m.includes("horas") || m.includes("aguenta") || m.includes("autonomia")) {
        return "A autonomia do veiculo depende da capacidade util da bateria (kWh) e do consumo medio (tipicamente entre 14 e 18 kWh/100 km). Em uso urbano, uma carga completa costuma proporcionar entre 250 km e 350 km de deslocamento.";
    }
    if (m.includes("kwh") || m.includes("completar") || m.includes("faltam")) {
        return "O volume de energia necessario para completar a carga equivale a diferenca percentual entre a carga atual e 100% multiplicada pela capacidade nominal da bateria. No GoodWe HCA G2 (7.4 kW), cada hora entrega aproximadamente 6.8 kWh uteis.";
    }
    if (m.includes("custo") || m.includes("preço") || m.includes("valor")) {
        return "O valor e calculado pela formula direta: Fatura = Energia Consumida (kWh) × Tarifa (R$ 0,95/kWh). O usuario paga exclusivamente pelo volume de energia efetivamente recebido pelo veiculo.";
    }
    return "Ola! Sou a EVA, assistente do EV ChargeOps. Estou integrada ao carregador GoodWe HCA G2 para tirar duvidas sobre autonomia, rateio por kWh e faturamento.";
}

// ==========================================================================
// 6. Modulo Simulador de Recarga & Rateio
// ==========================================================================
function initSimulator() {
    const sliderCurrent = document.getElementById("sim-current-soc");
    const sliderTarget = document.getElementById("sim-target-soc");
    const valCurrent = document.getElementById("val-current-soc");
    const valTarget = document.getElementById("val-target-soc");
    const batteryInput = document.getElementById("sim-battery");
    const btnSimulate = document.getElementById("btn-run-simulation");
    const btnPay = document.getElementById("btn-simulate-payment");

    sliderCurrent.addEventListener("input", (e) => {
        valCurrent.textContent = `${e.target.value}%`;
        if (parseInt(sliderTarget.value) < parseInt(e.target.value)) {
            sliderTarget.value = e.target.value;
            valTarget.textContent = `${e.target.value}%`;
        }
    });

    sliderTarget.addEventListener("input", (e) => {
        if (parseInt(e.target.value) < parseInt(sliderCurrent.value)) {
            e.target.value = sliderCurrent.value;
        }
        valTarget.textContent = `${e.target.value}%`;
    });

    btnSimulate.addEventListener("click", runSimulation);

    btnPay.addEventListener("click", () => {
        const cost = document.getElementById("res-cost").textContent;
        const kwh = document.getElementById("res-kwh").textContent;
        const msg = document.getElementById("payment-status-msg");
        msg.innerHTML = `<strong>Autorizacao confirmada.</strong> Fatura estimada em <strong>${cost}</strong> para o volume de <strong>${kwh}</strong> vinculada a unidade <strong>${state.unit}</strong>.`;
        msg.style.color = "var(--accent-green)";
    });
}

async function runSimulation() {
    const battery = parseFloat(document.getElementById("sim-battery").value) || 40.0;
    const curSoc = parseFloat(document.getElementById("sim-current-soc").value) || 0;
    const targetSoc = parseFloat(document.getElementById("sim-target-soc").value) || 0;

    try {
        if (state.apiOnline) {
            const res = await fetch(`${API_BASE_URL}/api/billing/simulate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    vehicle_battery_kwh: battery,
                    current_soc_percent: curSoc,
                    target_soc_percent: targetSoc,
                    charger_power_kw: 7.4,
                    rate_per_kwh: 0.95
                })
            });

            if (res.ok) {
                const data = await res.json();
                updateSimulationUI(data);
                return;
            }
        }
    } catch (e) {
        // Fallback matemático local
    }

    const delta = Math.max(0, (targetSoc - curSoc) / 100.0);
    const neededKwh = battery * delta;
    const timeHours = neededKwh / (7.4 * 0.92);
    const totalMins = Math.round(timeHours * 60);
    const h = Math.floor(totalMins / 60);
    const m = totalMins % 60;
    const cost = neededKwh * 0.95;

    updateSimulationUI({
        energy_needed_kwh: neededKwh,
        estimated_time_formatted: `${h}h ${m < 10 ? '0' : ''}${m}min`,
        total_cost_brl: cost,
        estimated_added_range_km: neededKwh * 6.8
    });
}

function updateSimulationUI(data) {
    document.getElementById("res-kwh").textContent = `${data.energy_needed_kwh.toFixed(2).replace('.', ',')} kWh`;
    document.getElementById("res-time").textContent = data.estimated_time_formatted;
    document.getElementById("res-cost").textContent = `R$ ${data.total_cost_brl.toFixed(2).replace('.', ',')}`;
    document.getElementById("res-range").textContent = `+${Math.round(data.estimated_added_range_km)} km`;

    const baseEnergy = (data.energy_needed_kwh * 0.82).toFixed(2).replace('.', ',');
    const maint = (data.energy_needed_kwh * 0.13).toFixed(2).replace('.', ',');
    document.getElementById("res-base-energy").textContent = `R$ ${baseEnergy}`;
    document.getElementById("res-maintenance").textContent = `R$ ${maint}`;
}

// ==========================================================================
// 7. Modulo Historico de Sessoes & Telemetria
// ==========================================================================
function initHistory() {
    const btnRefresh = document.getElementById("btn-refresh-history");
    if (btnRefresh) {
        btnRefresh.addEventListener("click", () => {
            loadHistory();
            loadMetrics();
        });
    }
    loadHistory();
}

async function loadHistory() {
    const tbody = document.getElementById("sessions-table-body");
    tbody.innerHTML = `<tr><td colspan="9" class="loading-td">Carregando sessoes...</td></tr>`;

    let sessions = [];

    try {
        if (state.apiOnline) {
            const res = await fetch(`${API_BASE_URL}/api/sessions`);
            if (res.ok) {
                const data = await res.json();
                sessions = data.sessions;
            }
        }
    } catch (e) {
        sessions = [];
    }

    renderTableRows(sessions);
}

function renderTableRows(sessions) {
    const tbody = document.getElementById("sessions-table-body");
    tbody.innerHTML = "";

    if (!sessions || sessions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="loading-td">Nenhuma sessao registrada. Aguardando leitura de dados do GoodWe HCA G2.</td></tr>`;
        return;
    }

    sessions.forEach(s => {
        const tr = document.createElement("tr");
        const statusBadge = s.status === 'completed' 
            ? `<span class="badge-status badge-completed">Concluida</span>`
            : `<span class="badge-status badge-in-progress">Em andamento</span>`;

        tr.innerHTML = `
            <td><code>${s.session_id}</code></td>
            <td><strong>${s.user_name}</strong></td>
            <td>${s.unit}</td>
            <td>${s.vehicle_model}</td>
            <td>${s.start_time}</td>
            <td>${s.duration_minutes} min</td>
            <td><strong>${s.energy_delivered_kwh.toFixed(2).replace('.', ',')} kWh</strong></td>
            <td class="text-green"><strong>R$ ${s.total_cost_brl.toFixed(2).replace('.', ',')}</strong></td>
            <td>${statusBadge}</td>
        `;
        tbody.appendChild(tr);
    });
}
