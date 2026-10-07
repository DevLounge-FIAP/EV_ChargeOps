// Dashboard Administrativo (Bruno Santos)
// Busca os dados na API (/api/admin/dashboard, /payments, /chargers e /users)
// e desenha cartões, gráficos e tabelas. Os cálculos ficam no backend.
// Usa o Chart.js (js/vendor/chart.umd.js) e o API_BASE_URL que vem do app.js.

(function () {
    "use strict";

    const PAGE_SIZE = 15;
    const dash = { loaded: false, charts: {}, payOffset: 0, payTotal: 0 };

    const COLORS = {
        cyan: "#00e5ff", blue: "#0284c7", green: "#10b981", amber: "#f59e0b",
        text: "#94a3b8", grid: "rgba(255,255,255,0.06)"
    };

    const $ = (id) => document.getElementById(id);
    const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

    const nf = (v, d) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
    const fmt = {
        kwh: (v) => (v == null ? "--" : `${nf(v, 1)} kWh`),
        brl: (v) => (v == null ? "--" : Number(v).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })),
        pct: (v) => (v == null ? "--" : `${nf(v, 1)}%`),
        min: (v) => (v == null ? "--" : `${nf(v, 0)} min`),
        int: (v) => (v == null ? "--" : nf(v, 0))
    };

    const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
    const mesLabel = (m) => { const [a, n] = m.split("-"); return `${MESES[Number(n) - 1]}/${a.slice(2)}`; };

    function qs(params) {
        const p = Object.entries(params).filter(([, v]) => v !== "" && v != null);
        return p.length ? "?" + new URLSearchParams(p).toString() : "";
    }

    async function getJson(path) {
        const res = await fetch(`${API_BASE_URL}${path}`);
        if (!res.ok) throw new Error(`HTTP ${res.status} em ${path.split("?")[0]}`);
        return res.json();
    }

    function setStatus(msg, isError) {
        const el = $("dash-status");
        el.textContent = msg || "";
        el.classList.toggle("error", !!isError);
    }

    const filters = () => ({
        user_id: $("dash-user").value,
        inicio: $("dash-inicio").value,
        fim: $("dash-fim").value
    });

    // ---------------------------------------------------------------- KPIs
    function renderKpis(k) {
        $("dk-consumo").textContent = fmt.kwh(k.consumo.energia_total_kwh);
        $("dk-consumo-meta").textContent = `${fmt.int(k.consumo.sessoes)} sessões · média ${fmt.kwh(k.consumo.energia_media_sessao_kwh)}`;

        $("dk-bateria").textContent = fmt.pct(k.bateria.pct_medio_por_sessao);
        $("dk-bateria-meta").textContent = `Estimado por sessão · carregador ${k.bateria.status_carregador === "operational" ? "operacional" : k.bateria.status_carregador}`;

        $("dk-tempo").textContent = k.tempo_carga.media_formatada || "--";
        $("dk-tempo-meta").textContent = k.tempo_carga.mediana_min == null
            ? "Sem sessões no período"
            : `Mediana ${fmt.min(k.tempo_carga.mediana_min)} · maior ${fmt.min(k.tempo_carga.maior_min)}`;

        $("dk-fatura").textContent = fmt.brl(k.faturamento.total_brl);
        const inad = k.faturamento.inadimplencia_medida
            ? `Pendente ${fmt.brl(k.faturamento.pendente_brl)}`
            : "Inadimplência: sem dados";
        $("dk-fatura-meta").textContent = `Ticket médio ${fmt.brl(k.faturamento.ticket_medio_brl)} · ${inad}`;

        $("dk-auto").textContent = fmt.pct(k.eficiencia.autoconsumo_pct);
        $("dk-auto-meta").textContent = `Contribuição ${fmt.pct(k.eficiencia.contribuicao_pct)} do consumo`;

        $("dk-prod").textContent = `${nf(k.eficiencia.produtividade_kwh_kwp ?? 0, 1)} kWh/kWp`;
        $("dk-prod-meta").textContent = `Geração ${fmt.kwh(k.eficiencia.geracao_kwh)} · ${k.eficiencia.capacidade_pv_kwp} kWp`;
    }

    // -------------------------------------------------------------- gráficos
    function baseOptions(extra) {
        const o = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: COLORS.text, boxWidth: 12 } } },
            scales: {
                x: { ticks: { color: COLORS.text }, grid: { display: false } },
                y: { beginAtZero: true, ticks: { color: COLORS.text }, grid: { color: COLORS.grid } }
            }
        };
        return Object.assign(o, extra || {});
    }

    function drawChart(key, empty, buildConfig) {
        const box = $(`${key}`).parentElement;
        box.classList.toggle("is-empty", empty);
        if (dash.charts[key]) { dash.charts[key].destroy(); delete dash.charts[key]; }
        if (empty) return;
        dash.charts[key] = new Chart($(key), buildConfig());
    }

    function renderCharts(d) {
        const ses = d.series_mensais, est = d.estacao_mensal;
        const sesL = ses.map((r) => mesLabel(r.mes)), estL = est.map((r) => mesLabel(r.mes));

        drawChart("ch-energia", !ses.length, () => ({
            type: "bar",
            data: { labels: sesL, datasets: [{ label: "Energia entregue (kWh)", data: ses.map((r) => r.energia_kwh), backgroundColor: COLORS.cyan, borderRadius: 4 }] },
            options: baseOptions()
        }));

        drawChart("ch-fatura", !ses.length, () => ({
            type: "bar",
            data: { labels: sesL, datasets: [{ label: "Faturamento (R$)", data: ses.map((r) => r.faturamento_brl), backgroundColor: COLORS.green, borderRadius: 4 }] },
            options: baseOptions({ plugins: { legend: { labels: { color: COLORS.text, boxWidth: 12 } },
                tooltip: { callbacks: { label: (c) => ` ${fmt.brl(c.parsed.y)}` } } } })
        }));

        const usu = d.por_usuario.filter((u) => u.sessoes > 0);
        drawChart("ch-tempo", !usu.length, () => ({
            type: "bar",
            data: { labels: usu.map((u) => u.nome), datasets: [{ label: "Tempo médio de carga (min)", data: usu.map((u) => u.duracao_media_min), backgroundColor: COLORS.amber, borderRadius: 4 }] },
            options: baseOptions({ indexAxis: "y", scales: {
                x: { beginAtZero: true, ticks: { color: COLORS.text }, grid: { color: COLORS.grid } },
                y: { ticks: { color: COLORS.text }, grid: { display: false } } } })
        }));

        const vei = d.por_veiculo;
        drawChart("ch-bateria", !vei.length, () => ({
            type: "bar",
            data: { labels: vei.map((v) => v.modelo), datasets: [{ label: "% médio da bateria carregada por sessão (estimado)", data: vei.map((v) => v.pct_bateria_medio), backgroundColor: COLORS.blue, borderRadius: 4 }] },
            options: baseOptions({ scales: {
                x: { ticks: { color: COLORS.text }, grid: { display: false } },
                y: { beginAtZero: true, max: 100, ticks: { color: COLORS.text, callback: (v) => `${v}%` }, grid: { color: COLORS.grid } } } })
        }));

        drawChart("ch-estacao", !est.length, () => ({
            type: "bar",
            data: { labels: estL, datasets: [
                { label: "Geração (kWh)", data: est.map((r) => r.geracao_kwh), backgroundColor: COLORS.green, borderRadius: 3 },
                { label: "Consumo (kWh)", data: est.map((r) => r.consumo_kwh), backgroundColor: COLORS.cyan, borderRadius: 3 }] },
            options: baseOptions()
        }));

        drawChart("ch-eficiencia", !est.length, () => ({
            type: "line",
            data: { labels: estL, datasets: [
                { label: "Autoconsumo (%)", data: est.map((r) => r.autoconsumo_pct), borderColor: COLORS.cyan, backgroundColor: COLORS.cyan, tension: 0.25, spanGaps: true },
                { label: "Contribuição (%)", data: est.map((r) => r.contribuicao_pct), borderColor: COLORS.amber, backgroundColor: COLORS.amber, tension: 0.25, spanGaps: true }] },
            options: baseOptions({ scales: {
                x: { ticks: { color: COLORS.text }, grid: { display: false } },
                y: { beginAtZero: true, max: 100, ticks: { color: COLORS.text, callback: (v) => `${v}%` }, grid: { color: COLORS.grid } } } })
        }));
    }

    // ------------------------------------------------------------- tabelas
    function emptyRow(cols, msg) { return `<tr><td colspan="${cols}" class="dash-empty-td">${esc(msg)}</td></tr>`; }

    function renderUsers(lista) {
        $("dash-users-body").innerHTML = lista.length ? lista.map((u) => `
            <tr>
                <td>${esc(u.nome)}</td>
                <td>${esc(u.unidade)}</td>
                <td>${esc(u.veiculo)}</td>
                <td class="num">${fmt.int(u.sessoes)}</td>
                <td class="num">${fmt.kwh(u.energia_kwh)}</td>
                <td class="num">${fmt.brl(u.faturamento_brl)}</td>
                <td class="num">${fmt.min(u.duracao_media_min)}</td>
                <td>${esc(u.ultima_sessao || "--")}</td>
            </tr>`).join("") : emptyRow(8, "Nenhum usuário encontrado.");
    }

    function renderChargers(lista) {
        $("dash-chargers-body").innerHTML = lista.length ? lista.map((c) => `
            <tr>
                <td>${esc(c.modelo)}<br><small>${esc(c.local || "")}</small></td>
                <td class="num">${c.potencia_nominal_kw == null ? "--" : nf(c.potencia_nominal_kw, 1) + " kW"}</td>
                <td>${esc(c.conector || "--")}</td>
                <td><span class="dash-badge ${c.status === "operational" ? "" : "warn"}">${c.status === "operational" ? "Operacional" : esc(c.status)}</span></td>
                <td class="num">${fmt.int(c.sessoes)}</td>
                <td class="num">${fmt.kwh(c.energia_kwh)}</td>
                <td class="num">${c.horas_em_uso == null ? "--" : nf(c.horas_em_uso, 1) + " h"}</td>
                <td class="num">${fmt.pct(c.taxa_ocupacao_pct)}</td>
            </tr>`).join("") : emptyRow(8, "Nenhum carregador cadastrado.");
    }

    function renderWarnings(avisos) {
        $("dash-warnings-list").innerHTML = (avisos || []).map((a) => `<li>${esc(a)}</li>`).join("");
        $("dash-warnings").style.display = avisos && avisos.length ? "" : "none";
    }

    async function loadPayments(reset) {
        const body = $("dash-pay-body");
        if (reset) { dash.payOffset = 0; body.innerHTML = ""; }
        const p = await getJson("/api/admin/payments" + qs({ ...filters(), limit: PAGE_SIZE, offset: dash.payOffset }));
        dash.payTotal = p.total_registros;
        if (reset && !p.itens.length) body.innerHTML = emptyRow(8, "Nenhum pagamento no período.");
        body.insertAdjacentHTML("beforeend", p.itens.map((r) => `
            <tr>
                <td>${esc(r.session_id)}</td>
                <td>${esc(r.usuario)}</td>
                <td>${esc(r.unidade)}</td>
                <td>${esc(r.data)}</td>
                <td class="num">${fmt.kwh(r.energia_kwh)}</td>
                <td class="num">${r.tarifa_brl_kwh == null ? "--" : fmt.brl(r.tarifa_brl_kwh)}</td>
                <td class="num">${fmt.brl(r.valor_brl)}</td>
                <td><span class="dash-badge ${r.status === "completed" ? "" : "warn"}">${r.status === "completed" ? "Concluída" : esc(r.status)}</span></td>
            </tr>`).join(""));
        dash.payOffset += p.itens.length;
        $("dash-pay-info").textContent = `Mostrando ${fmt.int(dash.payOffset)} de ${fmt.int(dash.payTotal)} · total ${fmt.brl(p.total_brl)}`;
        $("dash-pay-more").disabled = dash.payOffset >= dash.payTotal;
    }

    // ------------------------------------------------------------- carga geral
    async function loadDashboard() {
        const btn = $("dash-refresh");
        btn.disabled = true;
        setStatus("Carregando dados do dashboard...");
        try {
            const [d, ch] = await Promise.all([
                getJson("/api/admin/dashboard" + qs(filters())),
                getJson("/api/admin/chargers")
            ]);
            renderKpis(d.kpis);
            renderCharts(d);
            renderUsers(d.por_usuario);
            renderChargers(ch.carregadores);
            renderWarnings(d.avisos);
            await loadPayments(true);
            dash.loaded = true;
            const per = d.filtros.periodo_disponivel;
            setStatus(per.inicio ? `Dados de sessões de ${per.inicio} a ${per.fim}.` : "");
        } catch (err) {
            setStatus(`Não foi possível carregar o dashboard (${err.message}). Verifique se o backend está ativo na porta 8000.`, true);
        } finally {
            btn.disabled = false;
        }
    }

    async function fillUserFilter() {
        try {
            const r = await getJson("/api/admin/users");
            const sel = $("dash-user");
            (r.usuarios || []).forEach((u) => {
                const o = document.createElement("option");
                o.value = u.user_id;
                o.textContent = `${u.name} (${u.unit})`;
                sel.appendChild(o);
            });
        } catch (_) { /* o filtro continua com a opção "Todos" */ }
    }

    function initDashboard() {
        const tabBtn = $("btn-tab-dashboard");
        if (!tabBtn) return;
        if (typeof Chart === "undefined") {
            setStatus("Biblioteca de gráficos (Chart.js) não carregada.", true);
        }
        tabBtn.addEventListener("click", () => {
            // espera a aba ficar visível para o Chart.js medir o tamanho correto
            setTimeout(() => {
                if (!dash.loaded) { fillUserFilter().then(loadDashboard); }
                else Object.values(dash.charts).forEach((c) => c.resize());
            }, 50);
        });
        $("dash-refresh").addEventListener("click", loadDashboard);
        ["dash-user", "dash-inicio", "dash-fim"].forEach((id) => $(id).addEventListener("change", loadDashboard));
        $("dash-pay-more").addEventListener("click", () =>
            loadPayments(false).catch((e) => setStatus(`Falha ao carregar pagamentos (${e.message}).`, true)));
    }

    document.addEventListener("DOMContentLoaded", initDashboard);
})();
