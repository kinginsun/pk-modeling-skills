#!/usr/bin/env python3
"""HTML template for build_theophylline_report.py — NONMEM + Monolix ECharts report."""

import json

CSS = """
:root {
  --bg: #0d1117; --card: #161d2e; --border: #263049;
  --text: #e6edf3; --muted: #8b98b8; --accent: #5b8ff9; --ok: #5ad8a6;
  --warn: #f0b429; --bad: #e8684a; --nm: #5b8ff9; --mx: #f6bd16;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text);
  font-family: "PingFang SC", -apple-system, "Segoe UI", sans-serif;
  padding: 28px 32px 56px; max-width: 1500px; margin: 0 auto; }
header { margin-bottom: 20px; }
header h1 { font-size: 23px; font-weight: 650; letter-spacing: .3px; }
header .sub { color: var(--muted); font-size: 13px; margin-top: 6px; line-height: 1.8; }
code, .mono { font-family: "SF Mono", Menlo, Consolas, monospace; }
header .sub code, .card code, td code, .note code, li code {
  background: #1f2937; padding: 1px 6px; border-radius: 5px; font-size: 12px; color: #9ecbff; }
nav { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0 22px; }
nav a { color: var(--accent); text-decoration: none; font-size: 12.5px;
  background: var(--card); border: 1px solid var(--border); padding: 5px 12px; border-radius: 8px; }
nav a:hover { border-color: var(--accent); }
h2.sec { font-size: 17px; font-weight: 640; margin: 34px 0 6px; padding-top: 10px;
  border-top: 1px solid var(--border); }
h2.sec .chip { font-size: 11px; font-weight: 500; color: var(--muted); margin-left: 10px;
  border: 1px solid var(--border); border-radius: 6px; padding: 2px 8px; vertical-align: 2px; }
.sec-desc { color: var(--muted); font-size: 12.5px; margin-bottom: 14px; line-height: 1.7; }
.stats { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }
.stat { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; }
.stat .k { color: var(--muted); font-size: 11.5px; }
.stat .v { font-size: 20px; font-weight: 700; margin-top: 4px; font-variant-numeric: tabular-nums; }
.stat .v small { font-size: 11.5px; color: var(--muted); font-weight: 400; margin-left: 4px; }
.stat.nm { border-left: 3px solid var(--nm); }
.stat.mx { border-left: 3px solid var(--mx); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px 18px 12px; margin-bottom: 16px; }
.grid .card, .grid3 .card { margin-bottom: 0; }
.card.wide { grid-column: 1 / -1; }
.card h3 { font-size: 14px; font-weight: 600; }
.card .desc { color: var(--muted); font-size: 12px; margin: 3px 0 8px; line-height: 1.7; }
.chart { width: 100%; height: 320px; }
.chart.tall { height: 420px; }
.chart.xtall { height: 520px; }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 6px; }
th, td { text-align: right; padding: 5px 10px; border-bottom: 1px solid var(--border);
  font-variant-numeric: tabular-nums; }
th { color: var(--muted); font-weight: 500; }
th:first-child, td:first-child { text-align: left; }
.tag { display: inline-block; background: #1d3b2a; color: var(--ok); border-radius: 5px;
  padding: 1px 7px; font-size: 11px; margin-left: 6px; }
.tag.warn { background: #3b2f1d; color: var(--warn); }
.tag.bad { background: #3b1d1d; color: var(--bad); }
.tag.nm { background: #16294a; color: #8db4ff; }
.tag.mx { background: #3b3016; color: #ffd666; }
.sel { margin: 4px 0 8px; }
.sel label { color: var(--muted); font-size: 12px; margin-right: 8px; }
.sel select { background: #1f2937; color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 8px; font-size: 12px; }
details { background: #10162480; border: 1px solid var(--border); border-radius: 10px;
  padding: 10px 14px; margin: 10px 0; }
details summary { cursor: pointer; font-size: 13px; color: var(--accent); font-weight: 550; }
details pre { margin-top: 10px; overflow-x: auto; font-size: 11.5px; line-height: 1.6;
  color: #c9d6ee; white-space: pre; }
.eq { background: #10162480; border: 1px solid var(--border); border-left: 3px solid var(--accent);
  border-radius: 10px; padding: 12px 16px; margin: 8px 0; font-size: 13px; line-height: 2.0;
  font-family: "STIX Two Math", "SF Mono", Menlo, serif; overflow-x: auto; }
.eq b { color: #9ecbff; font-family: inherit; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.note { color: var(--muted); font-size: 12px; line-height: 1.8; margin-top: 8px; }
ul.tight { margin: 6px 0 6px 20px; font-size: 12.5px; color: var(--text); line-height: 1.9; }
ul.tight li::marker { color: var(--muted); }
footer { color: var(--muted); font-size: 12px; margin-top: 30px; line-height: 1.8;
  border-top: 1px solid var(--border); padding-top: 14px; }
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 6px 0 2px; }
.pill { font-size: 11.5px; color: var(--muted); border: 1px solid var(--border);
  border-radius: 999px; padding: 2px 10px; }
@media (max-width: 1100px) {
  .stats { grid-template-columns: repeat(3, 1fr); }
  .grid, .grid3, .two-col { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  body { padding: 18px 14px 40px; }
  .stats { grid-template-columns: 1fr 1fr; }
}
"""

JS = r"""
const D = __DATA__;

const baseAxis = {
  axisLine: { lineStyle: { color: '#3a4660' } },
  axisLabel: { color: '#8b98b8', fontSize: 11 },
  splitLine: { lineStyle: { color: '#1f2a40' } }
};
const nameStyle = { color: '#8b98b8', fontSize: 11 };
const NM_C = '#5b8ff9', MX_C = '#f6bd16', OK_C = '#5ad8a6', BAD_C = '#e8684a';
const palette = ['#5b8ff9','#5ad8a6','#f6bd16','#e8684a','#6dc8ec','#9270ca','#ff9d4d',
                 '#269a99','#ff99c3','#5d7092','#c2c8d5','#b6e3ff'];
const charts = {};
function init(id) {
  const el = document.getElementById(id);
  if (!el) return null;
  const c = echarts.init(el, null, { renderer: 'canvas' });
  charts[id] = c;
  return c;
}
window.addEventListener('resize', () => Object.values(charts).forEach(c => c.resize()));
const fmt = (x, d=3) => (x===null||x===undefined||Number.isNaN(x)) ? '—'
  : Number(x).toPrecision(d);
function rseBadge(v){
  if (v===null||v===undefined) return '—';
  const c = v>50 ? BAD_C : v>30 ? '#f0b429' : OK_C;
  return `<span style="color:${c}">${v.toFixed(1)}%</span>`;
}

/* ============ shared: forest plot (est + 95% CI, log x) ============ */
function forestOption(items, color, xName) {
  // items: [{label, est, lo, hi, rse}]
  const cats = items.map(i => i.label);
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p => {
      const it = items[p.dataIndex]; if (!it) return '';
      return `${it.label}<br/>估计 ${fmt(it.est,4)}<br/>95% CI [${fmt(it.lo,3)}, ${fmt(it.hi,3)}]`
        + (it.rse!=null ? `<br/>RSE ${it.rse.toFixed(1)}%` : '');
    }},
    grid: { left: 10, right: 40, top: 30, bottom: 30, containLabel: true },
    xAxis: { type: 'log', name: xName || '', nameTextStyle: nameStyle,
      nameLocation: 'middle', nameGap: 26, ...baseAxis,
      axisLabel: { color: '#8b98b8', fontSize: 11, formatter: v => +v.toPrecision(2) } },
    yAxis: { type: 'category', data: cats, inverse: true,
      axisLabel: { color: '#c9d6ee', fontSize: 11.5, fontFamily: 'Menlo, monospace' },
      axisLine: { lineStyle: { color: '#3a4660' } }, splitLine: { show: false } },
    series: [{
      type: 'custom',
      renderItem: (params, api) => {
        const y = api.coord([0, api.value(0)])[1];
        const xLo = api.coord([api.value(1), 0])[0];
        const xHi = api.coord([api.value(2), 0])[0];
        const xEst = api.coord([api.value(3), 0])[0];
        const h = 9;
        return { type: 'group', children: [
          { type: 'line', shape: { x1: xLo, y1: y, x2: xHi, y2: y },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'line', shape: { x1: xLo, y1: y-h, x2: xLo, y2: y+h },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'line', shape: { x1: xHi, y1: y-h, x2: xHi, y2: y+h },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'circle', shape: { cx: xEst, cy: y, r: 5 },
            style: { fill: color } }
        ]};
      },
      encode: { x: [1,2,3], y: 0 },
      data: items.map((it, i) => [i, it.lo, it.hi, it.est])
    }]
  };
}

/* ============ shared: individual-fits subject selector ============ */
function fitsController(selId, chartId, byId, ipredIdx, predIdx, obsIdx, engineLabel) {
  const ids = Object.keys(byId).sort((a,b)=>+a-+b);
  const sel = document.getElementById(selId);
  sel.innerHTML = ids.map(id => `<option value="${id}">ID ${id}</option>`).join('')
    + '<option value="ALL">全部叠加</option>';
  const c = init(chartId);
  function render(mode) {
    if (mode === 'ALL') {
      const series = [];
      ids.forEach((id, i) => {
        const col = palette[i % palette.length];
        series.push({ name: 'ID'+id+' obs', type: 'scatter', symbolSize: 6,
          itemStyle: { color: col, opacity: 0.9 },
          data: byId[id].map(rr => [rr[0], rr[obsIdx]]) });
        series.push({ name: 'ID'+id, type: 'line', showSymbol: false, smooth: 0.15,
          lineStyle: { width: 1.5, color: col },
          data: byId[id].map(rr => [rr[0], rr[ipredIdx]]) });
      });
      c.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { type: 'scroll', top: 0, textStyle: { color: '#8b98b8', fontSize: 10 },
          data: ids.map(id => 'ID'+id) },
        grid: { left: 46, right: 16, top: 36, bottom: 56 },
        xAxis: { type: 'value', name: 'Time (h)', nameTextStyle: nameStyle, ...baseAxis },
        yAxis: { type: 'value', name: '浓度 (mg/L)', nameTextStyle: nameStyle, ...baseAxis },
        dataZoom: [{ type: 'inside' }, { type: 'slider', height: 16, bottom: 8 }],
        series
      }, true);
    } else {
      const rows = byId[mode];
      const dense = [];
      const tmax = Math.max(...rows.map(rr => rr[0]));
      const p = engineParamsFor(mode, engineLabel);
      if (p) {  // dense model curve from individual parameters (1-cpt oral)
        const { ka, k, v, amtPerKg } = p;
        for (let t = 0.01; t <= tmax * 1.02; t += tmax / 240) {
          dense.push([+t.toFixed(3), +(amtPerKg * ka / (v * (ka - k))
            * (Math.exp(-k * t) - Math.exp(-ka * t))).toFixed(4)]);
        }
      }
      c.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        legend: { top: 0, textStyle: { color: '#8b98b8' } },
        grid: { left: 46, right: 16, top: 36, bottom: 40 },
        xAxis: { type: 'value', name: 'Time (h)', nameTextStyle: nameStyle, ...baseAxis },
        yAxis: { type: 'value', name: '浓度 (mg/L)', nameTextStyle: nameStyle, ...baseAxis },
        series: [
          { name: '观测 DV', type: 'scatter', symbolSize: 9, z: 5,
            itemStyle: { color: '#e6edf3', borderColor: NM_C, borderWidth: 1.5 },
            data: rows.map(rr => [rr[0], rr[obsIdx]]) },
          { name: '个体预测 IPRED', type: 'line', showSymbol: true, symbolSize: 4,
            lineStyle: { width: 2, color: OK_C }, itemStyle: { color: OK_C },
            data: rows.map(rr => [rr[0], rr[ipredIdx]]) },
          ...(dense.length ? [{ name: '模型曲线 (个体参数)', type: 'line', showSymbol: false,
            smooth: true, lineStyle: { width: 1.4, color: MX_C, type: 'dashed' },
            data: dense }] : []),
          ...(predIdx != null ? [{ name: '群体预测 PRED', type: 'line', showSymbol: false,
            smooth: 0.15, lineStyle: { width: 1.6, color: '#9270ca', type: 'dotted' },
            data: rows.map(rr => [rr[0], rr[predIdx]]) }] : [])
        ]
      }, true);
    }
  }
  sel.onchange = () => render(sel.value);
  sel.value = '1';
  render('1');
}
function engineParamsFor(id, engine) {
  const AMT = 4.02;  // mg/kg
  if (engine === 'nm') {
    const s = D.nonmem.subjects.find(x => x.id == id);
    return s ? { ka: s.ka, k: s.cl / s.v, v: s.v, amtPerKg: AMT } : null;
  }
  const s = D.monolix.subjects.find(x => x.id == id);
  return s ? { ka: s.ka, k: s.Cl / s.V, v: s.V, amtPerKg: AMT } : null;
}

/* ================= 1) NONMEM ================= */
const NM = D.nonmem;

// N1 convergence
(function () {
  const c = init('nmConv');
  const its = NM.iters.filter(p => p.iter >= 0);
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: ps => {
      const p = ps[0]; return `迭代 ${p.data[0]}<br/>OFV = ${(+p.data[1]).toFixed(4)}`; }},
    grid: { left: 52, right: 20, top: 34, bottom: 40 },
    xAxis: { type: 'value', name: '迭代次数', nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'log', name: 'OFV (log)', nameTextStyle: nameStyle, ...baseAxis,
      axisLabel: { color: '#8b98b8', fontSize: 11, formatter: v => +v.toPrecision(3) } },
    series: [{
      type: 'line', data: its.map(p => [p.iter, p.obj]), showSymbol: true, symbolSize: 7,
      lineStyle: { width: 2.2, color: NM_C }, itemStyle: { color: NM_C },
      markPoint: { symbolSize: 46, itemStyle: { color: OK_C },
        label: { fontSize: 9, color: '#0d1117' },
        data: [{ coord: [its[its.length-1].iter, its[its.length-1].obj],
                 value: '收敛\n' + its[its.length-1].obj.toFixed(2) }] },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(91,143,249,.28)' },
                     { offset: 1, color: 'rgba(91,143,249,0)' }] } }
    }]
  });
})();

// N2 forest of thetas
(function () {
  const items = NM.params.filter(p => ['KA','CL','V'].includes(p.name))
    .map(p => ({ label: p.label + '  (' + p.unit + ')', est: p.est, lo: p.lo, hi: p.hi,
                 rse: p.rse }));
  init('nmForest').setOption(forestOption(items, NM_C, '估计值（对数轴）'));
})();

// N3 individual fits
fitsController('nmSubjSel', 'nmFits', NM.by_id, 2, 3, 1, 'nm');

// N4 GOF: DV vs IPRED / DV vs PRED
(function () {
  const c = init('nmGof');
  const all = NM.gof.map(g => Math.max(g[0], g[1], g[2]));
  const m = Math.max(...all) * 1.05;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p =>
      p.seriesType === 'line' ? '' :
      `ID ${p.data[2]}<br/>观测 ${p.data[1]}<br/>预测 ${p.data[0]}` },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 48, right: 18, top: 34, bottom: 42 },
    xAxis: { type: 'value', name: '预测', min: 0, max: m, nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'value', name: '观测 DV', min: 0, max: m, nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { name: 'DV vs IPRED', type: 'scatter', symbolSize: 7,
        itemStyle: { color: OK_C, opacity: .8 }, data: NM.gof.map(g => [g[0], g[2], g[5]]) },
      { name: 'DV vs PRED', type: 'scatter', symbolSize: 7,
        itemStyle: { color: '#9270ca', opacity: .7 }, data: NM.gof.map(g => [g[1], g[2], g[5]]) },
      { name: 'y = x', type: 'line', showSymbol: false, silent: true,
        data: [[0,0],[m,m]], lineStyle: { type: 'dashed', color: '#8b98b8', width: 1.2 } }
    ]
  });
})();

// N5 CWRES vs time / vs PRED
(function () {
  const c = init('nmCwres');
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p =>
      `ID ${p.data[2]}<br/>${p.seriesName} = ${p.data[0]}<br/>CWRES = ${p.data[1]}` },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: [{ left: 46, right: '53%', top: 34, bottom: 40 },
           { left: '55%', right: 18, top: 34, bottom: 40 }],
    xAxis: [
      { type: 'value', name: 'Time (h)', gridIndex: 0, nameTextStyle: nameStyle, ...baseAxis },
      { type: 'value', name: 'PRED', gridIndex: 1, nameTextStyle: nameStyle, ...baseAxis }],
    yAxis: [
      { type: 'value', name: 'CWRES', gridIndex: 0, nameTextStyle: nameStyle, ...baseAxis },
      { type: 'value', name: 'CWRES', gridIndex: 1, nameTextStyle: nameStyle, ...baseAxis }],
    series: [
      { name: '时间', type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbolSize: 7,
        data: NM.gof.map(g => [g[4], g[3], g[5]]),
        itemStyle: { color: p => p.data[1] >= 0 ? NM_C : BAD_C, opacity: .8 },
        markLine: { silent: true, symbol: 'none', label: { show: false },
          lineStyle: { color: '#8b98b8', type: 'dashed' },
          data: [{ yAxis: 0 }, { yAxis: 2, lineStyle: { color: '#3a4660' } },
                 { yAxis: -2, lineStyle: { color: '#3a4660' } }] } },
      { name: 'PRED', type: 'scatter', xAxisIndex: 1, yAxisIndex: 1, symbolSize: 7,
        data: NM.gof.map(g => [g[1], g[3], g[5]]),
        itemStyle: { color: p => p.data[1] >= 0 ? '#9270ca' : BAD_C, opacity: .8 } }
    ]
  });
})();

// N6 eta bars + posterior SD
(function () {
  const c = init('nmEta');
  const ids = NM.phi.map(p => 'ID' + p.id);
  function bars(key, sdKey, color, name) {
    return { name, type: 'bar', barGap: '10%',
      data: NM.phi.map(p => p[key]),
      itemStyle: { color },
      label: { show: false } };
  }
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: ps => {
        const i = ps[0].dataIndex, p = NM.phi[i];
        return `ID ${p.id}<br/>η_KA ${p.eta1} ± ${p.sd1}<br/>η_CL ${p.eta2} ± ${p.sd2}` +
               `<br/>η_V ${p.eta3} ± ${p.sd3}`;
      }},
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 46, right: 16, top: 34, bottom: 34 },
    xAxis: { type: 'category', data: ids, axisLabel: { color: '#8b98b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    yAxis: { type: 'value', name: 'η (EBE)', nameTextStyle: nameStyle, ...baseAxis },
    series: [
      bars('eta1', 'sd1', NM_C, 'η_KA'),
      bars('eta2', 'sd2', OK_C, 'η_CL'),
      bars('eta3', 'sd3', MX_C, 'η_V'),
      { type: 'line', markLine: { silent: true, symbol: 'none',
        lineStyle: { color: '#8b98b8', type: 'dashed' }, data: [{ yAxis: 0 }] }, data: [] }
    ]
  });
})();

// N7 correlation heatmap
function corrHeatmap(elId, corr, rotate) {
  const c = init(elId);
  const data = [];
  corr.names.forEach((ri, i) => corr.names.forEach((rj, j) =>
    data.push([j, i, +(corr.mat[i][j] || 0).toFixed(3)])));
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { formatter: p =>
      `${corr.names[p.value[1]]} × ${corr.names[p.value[0]]}<br/>r = ${p.value[2]}` },
    grid: { left: 80, right: 30, top: 16, bottom: 84 },
    xAxis: { type: 'category', data: corr.names, position: 'bottom',
      axisLabel: { color: '#8b98b8', rotate: rotate || 38, fontSize: 10 },
      axisLine: { lineStyle: { color: '#3a4660' } }, splitArea: { show: false } },
    yAxis: { type: 'category', data: corr.names,
      axisLabel: { color: '#8b98b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    visualMap: { min: -1, max: 1, calculable: true, orient: 'horizontal',
      left: 'center', bottom: 0, itemHeight: 90,
      inRange: { color: ['#3b82f6', '#0d1117', '#ef4444'] },
      textStyle: { color: '#8b98b8' } },
    series: [{ type: 'heatmap', data,
      label: { show: true, fontSize: 9, color: '#e6edf3',
        formatter: p => Math.abs(p.value[2]) < 0.05 ? '' : p.value[2] } }]
  });
}
corrHeatmap('nmCorr', NM.corr);

/* ================= 2) Monolix ================= */
const MX = D.monolix;

// M1 forest of population params (base)
(function () {
  const order = ['ka_pop','V_pop','Cl_pop'];
  const items = MX.params.filter(p => order.includes(p.parameter) && p.lo > 0)
    .map(p => ({ label: p.parameter, est: p.value, lo: p.lo, hi: p.hi, rse: p.rse }));
  init('mxForest').setOption(forestOption(items, MX_C, '估计值（对数轴，线性化 SE）'));
})();

// M2 individual fits
fitsController('mxSubjSel', 'mxFits', MX.by_id, 2, 3, 1, 'mx');

// M3 GOF
(function () {
  const c = init('mxGof');
  const m = Math.max(...MX.gof.map(g => Math.max(g[0], g[1], g[2]))) * 1.05;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p =>
      p.seriesType === 'line' ? '' :
      `ID ${p.data[2]}<br/>观测 ${p.data[1]}<br/>预测 ${p.data[0]}` },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 48, right: 18, top: 34, bottom: 42 },
    xAxis: { type: 'value', name: '预测', min: 0, max: m, nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'value', name: '观测 CONC', min: 0, max: m, nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { name: 'Obs vs indivPred (SAEM)', type: 'scatter', symbolSize: 7,
        itemStyle: { color: OK_C, opacity: .8 }, data: MX.gof.map(g => [g[1], g[2], g[3]]) },
      { name: 'Obs vs popPred', type: 'scatter', symbolSize: 7,
        itemStyle: { color: '#9270ca', opacity: .7 }, data: MX.gof.map(g => [g[0], g[2], g[3]]) },
      { name: 'y = x', type: 'line', showSymbol: false, silent: true,
        data: [[0,0],[m,m]], lineStyle: { type: 'dashed', color: '#8b98b8', width: 1.2 } }
    ]
  });
})();

// M4 IWRES vs time
(function () {
  const c = init('mxIwres');
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p =>
      `ID ${p.data[2]}<br/>t = ${p.data[0]} h<br/>IWRES = ${p.data[1]}` },
    grid: { left: 46, right: 18, top: 24, bottom: 40 },
    xAxis: { type: 'value', name: 'Time (h)', nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'value', name: 'IWRES', nameTextStyle: nameStyle, ...baseAxis },
    series: [{ type: 'scatter', symbolSize: 8,
      data: MX.iwres.map(rr => ({ value: rr,
        itemStyle: { color: rr[1] >= 0 ? MX_C : BAD_C, opacity: .85 } })),
      markLine: { silent: true, symbol: 'none', label: { show: false },
        lineStyle: { color: '#8b98b8', type: 'dashed' },
        data: [{ yAxis: 0 }, { yAxis: 2, lineStyle: { color: '#3a4660' } },
               { yAxis: -2, lineStyle: { color: '#3a4660' } }] } }]
  });
})();

// M5 eta bars
(function () {
  const c = init('mxEta');
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 46, right: 16, top: 34, bottom: 34 },
    xAxis: { type: 'category', data: MX.etas.map(e => 'ID'+e.id),
      axisLabel: { color: '#8b98b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    yAxis: { type: 'value', name: 'η (条件估计)', nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { name: 'η_ka', type: 'bar', data: MX.etas.map(e => e.ka), itemStyle: { color: MX_C } },
      { name: 'η_V', type: 'bar', data: MX.etas.map(e => e.V), itemStyle: { color: OK_C } },
      { name: 'η_Cl', type: 'bar', data: MX.etas.map(e => e.Cl), itemStyle: { color: NM_C } },
      { type: 'line', markLine: { silent: true, symbol: 'none',
        lineStyle: { color: '#8b98b8', type: 'dashed' }, data: [{ yAxis: 0 }] }, data: [] }
    ]
  });
})();

// M6 correlation (linearized FIM)
corrHeatmap('mxCorr', MX.corr, 40);

// M7 COSSAC model building
(function () {
  const c = init('mxMb');
  const mb = MX.model_building.models;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 52, right: 20, top: 34, bottom: 64 },
    xAxis: { type: 'category', data: mb.map(m => 'M' + m.model + '\n' + m.cov),
      axisLabel: { color: '#8b98b8', fontSize: 10, interval: 0 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    yAxis: { type: 'value', scale: true, name: '−2LL / BICc', nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { name: '−2LL (线性化)', type: 'bar', data: mb.map(m => m.ofv), barWidth: 26,
        itemStyle: { color: p => mb[p.dataIndex].model === MX.model_building.best
          ? OK_C : MX_C, borderRadius: [4,4,0,0] } },
      { name: 'BICc', type: 'line', data: mb.map(m => m.bicc),
        itemStyle: { color: '#9270ca' }, lineStyle: { width: 2 }, symbolSize: 7 }
    ]
  });
})();

// M8 variant comparison (Base / kaWT / ka_cWT / allometric)
(function () {
  const c = init('mxModels');
  const vs = MX.variants;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 52, right: 20, top: 34, bottom: 56 },
    xAxis: { type: 'category', data: vs.map(v => v.name),
      axisLabel: { color: '#8b98b8', fontSize: 10.5, interval: 0 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    yAxis: { type: 'value', scale: true, nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { name: 'OFV (IS)', type: 'bar', data: vs.map(v => v.ofv),
        itemStyle: { color: MX_C, borderRadius: [4,4,0,0] } },
      { name: 'AIC', type: 'bar', data: vs.map(v => v.aic),
        itemStyle: { color: '#6dc8ec', borderRadius: [4,4,0,0] } },
      { name: 'BIC', type: 'bar', data: vs.map(v => v.bic),
        itemStyle: { color: OK_C, borderRadius: [4,4,0,0] } },
      { name: 'BICc', type: 'bar', data: vs.map(v => v.bicc),
        itemStyle: { color: '#9270ca', borderRadius: [4,4,0,0] } }
    ]
  });
})();

/* ================= 3) cross-engine ================= */
const X = D.cross;

// X1 typical parameters NM vs MX with CI
(function () {
  const c = init('xTyp');
  const cats = [];
  const itemsNM = [], itemsMX = [];
  X.typical.forEach(t => {
    cats.push(t.label + ' (' + t.unit + ')');
    itemsNM.push({ est: t.nm, lo: t.nm_lo, hi: t.nm_hi });
    itemsMX.push({ est: t.mx, lo: t.mx_lo, hi: t.mx_hi });
  });
  function series(items, color, name, dy) {
    return { name, type: 'custom',
      renderItem: (params, api) => {
        const idx = api.value(0);
        const y = api.coord([0, idx])[1] + dy;
        const xLo = api.coord([api.value(1), 0])[0];
        const xHi = api.coord([api.value(2), 0])[0];
        const xEst = api.coord([api.value(3), 0])[0];
        return { type: 'group', children: [
          { type: 'line', shape: { x1: xLo, y1: y, x2: xHi, y2: y },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'line', shape: { x1: xLo, y1: y-6, x2: xLo, y2: y+6 },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'line', shape: { x1: xHi, y1: y-6, x2: xHi, y2: y+6 },
            style: { stroke: color, lineWidth: 2 } },
          { type: 'circle', shape: { cx: xEst, cy: y, r: 5 }, style: { fill: color } }
        ]};
      },
      encode: { x: [1,2,3], y: 0 },
      data: items.map((it, i) => [i, it.lo, it.hi, it.est]) };
  }
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p => {
      const it = (p.seriesName.startsWith('NONMEM') ? itemsNM : itemsMX)[p.value[0]];
      return `${p.seriesName}<br/>${cats[p.value[0]]}<br/>估计 ${fmt(it.est,4)}` +
             `<br/>95% CI [${fmt(it.lo,3)}, ${fmt(it.hi,3)}]`; }},
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 10, right: 40, top: 34, bottom: 34, containLabel: true },
    xAxis: { type: 'log', name: '估计值（对数轴）', nameLocation: 'middle', nameGap: 26,
      nameTextStyle: nameStyle, ...baseAxis,
      axisLabel: { color: '#8b98b8', fontSize: 11, formatter: v => +v.toPrecision(2) } },
    yAxis: { type: 'category', data: cats, inverse: true,
      axisLabel: { color: '#c9d6ee', fontSize: 11.5, fontFamily: 'Menlo, monospace' },
      axisLine: { lineStyle: { color: '#3a4660' } }, splitLine: { show: false } },
    series: [ series(itemsNM, NM_C, 'NONMEM FOCE-I', -8),
              series(itemsMX, MX_C, 'Monolix SAEM', +8) ]
  });
})();

// X2 relative difference
(function () {
  const c = init('xDiff');
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: ps => {
      const t = X.typical[ps[0].dataIndex];
      return `${t.label}<br/>NONMEM ${fmt(t.nm,4)} vs Monolix ${fmt(t.mx,4)} ${t.unit}` +
             `<br/>相对差 ${t.diff_pct > 0 ? '+' : ''}${t.diff_pct}%`; }},
    grid: { left: 52, right: 40, top: 20, bottom: 34 },
    xAxis: { type: 'category', data: X.typical.map(t => t.label),
      axisLabel: { color: '#8b98b8', fontSize: 12 },
      axisLine: { lineStyle: { color: '#3a4660' } } },
    yAxis: { type: 'value', name: '(NM−MLX)/MLX ×100%', nameTextStyle: nameStyle, ...baseAxis },
    series: [{ type: 'bar', barWidth: 44,
      data: X.typical.map(t => ({ value: t.diff_pct,
        itemStyle: { color: Math.abs(t.diff_pct) <= 2 ? OK_C : '#f0b429',
                     borderRadius: [4,4,0,0] } })),
      label: { show: true, position: 'top', color: '#c9d6ee', fontSize: 11,
        formatter: p => (p.value > 0 ? '+' : '') + p.value.toFixed(2) + '%' },
      markLine: { silent: true, symbol: 'none', label: { show: false },
        lineStyle: { color: '#8b98b8', type: 'dashed' }, data: [{ yAxis: 0 }] } }]
  });
})();

// X3 IPRED NM vs MLX
(function () {
  const c = init('xIpred');
  const m = Math.max(...X.ipred_pairs.map(p => Math.max(p[0], p[1]))) * 1.05;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p => p.seriesType === 'line' ? '' :
      `ID ${p.data[2]}, t=${p.data[3]} h<br/>NONMEM IPRED ${p.data[0]}<br/>Monolix iPred ${p.data[1]}` },
    grid: { left: 52, right: 20, top: 20, bottom: 42 },
    xAxis: { type: 'value', name: 'Monolix 个体预测', min: 0, max: m,
      nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'value', name: 'NONMEM IPRED', min: 0, max: m,
      nameTextStyle: nameStyle, ...baseAxis },
    series: [
      { type: 'scatter', symbolSize: 8, data: X.ipred_pairs,
        itemStyle: { color: OK_C, opacity: .8 } },
      { type: 'line', showSymbol: false, silent: true, data: [[0,0],[m,m]],
        lineStyle: { type: 'dashed', color: '#8b98b8', width: 1.2 } }
    ],
    graphic: [{ type: 'text', right: 26, top: 26,
      style: { text: 'RMSE = ' + X.rmse_ipred, fill: '#8b98b8', fontSize: 12 } }]
  });
})();

// X4 EBE comparison scatter
(function () {
  const c = init('xEbe');
  const sets = [
    { key: ['nm_ka','mx_ka'], name: 'η_KA', color: NM_C },
    { key: ['nm_cl','mx_cl'], name: 'η_CL', color: OK_C },
    { key: ['nm_v','mx_v'],   name: 'η_V',  color: MX_C }
  ];
  const ext = Math.max(...X.ebe.flatMap(e =>
    [Math.abs(e.nm_ka), Math.abs(e.mx_ka), Math.abs(e.nm_cl), Math.abs(e.mx_cl),
     Math.abs(e.nm_v), Math.abs(e.mx_v)])) * 1.1;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p => p.seriesType === 'line' ? '' :
      `ID ${p.data[2]}<br/>${p.seriesName}: NONMEM ${p.data[0]} vs Monolix ${p.data[1]}` },
    legend: { top: 0, textStyle: { color: '#8b98b8' } },
    grid: { left: 46, right: 20, top: 34, bottom: 42 },
    xAxis: { type: 'value', name: 'Monolix η', min: -ext, max: ext,
      nameTextStyle: nameStyle, ...baseAxis },
    yAxis: { type: 'value', name: 'NONMEM η', min: -ext, max: ext,
      nameTextStyle: nameStyle, ...baseAxis },
    series: sets.map(s => ({ name: s.name, type: 'scatter', symbolSize: 9,
      itemStyle: { color: s.color, opacity: .85 },
      data: X.ebe.map(e => [e[s.key[1]], e[s.key[0]], e.id]) }))
      .concat([{ name: 'y = x', type: 'line', showSymbol: false, silent: true,
        data: [[-ext,-ext],[ext,ext]],
        lineStyle: { type: 'dashed', color: '#8b98b8', width: 1.2 } }])
  });
})();

// X5 individual CL/V vs WT (both engines, allometric check)
(function () {
  const c = init('xCov');
  const nmS = NM.subjects, mxS = MX.subjects;
  c.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: p =>
      `${p.seriesName}<br/>ID ${p.data[2]} · WT ${p.data[0]} kg<br/>值 ${p.data[1]}` },
    legend: { top: 0, textStyle: { color: '#8b98b8', fontSize: 11 } },
    grid: [{ left: 52, right: '55%', top: 40, bottom: 40 },
           { left: '53%', right: 20, top: 40, bottom: 40 }],
    xAxis: [
      { gridIndex: 0, type: 'value', name: 'WT (kg)', nameTextStyle: nameStyle, ...baseAxis },
      { gridIndex: 1, type: 'value', name: 'WT (kg)', nameTextStyle: nameStyle, ...baseAxis }],
    yAxis: [
      { gridIndex: 0, type: 'value', name: '个体 CL (L/h/kg)', nameTextStyle: nameStyle, ...baseAxis },
      { gridIndex: 1, type: 'value', name: '个体 V (L/kg)', nameTextStyle: nameStyle, ...baseAxis }],
    series: [
      { name: 'NONMEM CL', type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbolSize: 9,
        itemStyle: { color: NM_C }, data: nmS.map(s => [s.wt, +s.cl.toFixed(4), s.id]) },
      { name: 'Monolix Cl', type: 'scatter', xAxisIndex: 0, yAxisIndex: 0, symbolSize: 9,
        symbol: 'triangle', itemStyle: { color: MX_C },
        data: mxS.map(s => [s.wt, +s.Cl.toFixed(4), s.id]) },
      { name: 'NONMEM V', type: 'scatter', xAxisIndex: 1, yAxisIndex: 1, symbolSize: 9,
        itemStyle: { color: NM_C }, data: nmS.map(s => [s.wt, +s.v.toFixed(4), s.id]) },
      { name: 'Monolix V', type: 'scatter', xAxisIndex: 1, yAxisIndex: 1, symbolSize: 9,
        symbol: 'triangle', itemStyle: { color: MX_C },
        data: mxS.map(s => [s.wt, +s.V.toFixed(4), s.id]) }
    ]
  });
})();

/* ================= tables ================= */
function paramTable(el, rows, cols) {
  let html = '<tr>' + cols.map(c => `<th>${c.label}</th>`).join('') + '</tr>';
  rows.forEach(rr => {
    html += '<tr>' + cols.map(c => `<td>${c.get(rr)}</td>`).join('') + '</tr>';
  });
  document.getElementById(el).innerHTML = html;
}
paramTable('tabNm', NM.params, [
  { label: '参数', get: p => `<span class="mono">${p.label}</span>` },
  { label: '单位', get: p => p.unit },
  { label: '估计值', get: p => `<b>${fmt(p.est,4)}</b>` },
  { label: 'RSE%', get: p => rseBadge(p.rse) },
  { label: '95% CI', get: p => `${fmt(p.lo,3)} – ${fmt(p.hi,3)}` }
]);
(function () {
  const rows = [
    ['ETABAR (η_KA, η_CL, η_V)', NM.etabar.map(x => fmt(x,3)).join(' , ')],
    ['ETABAR SE', NM.etabar_se.map(x => fmt(x,3)).join(' , ')],
    ['P 值 (H₀: 均值=0)', NM.etabar_p.map(x => fmt(x,3)).join(' , ')],
    ['η 收缩率 SD%', NM.eta_shrink_sd.map(x => x + '%').join(' , ')],
    ['EBV 收缩率 SD%', NM.ebv_shrink_sd.map(x => x + '%').join(' , ')],
    ['ε 收缩率 SD%', NM.eps_shrink_sd.map(x => x + '%').join(' , ')],
    ['相对信息量%', NM.rel_info.map(x => x + '%').join(' , ')]
  ];
  document.getElementById('tabNmShrink').innerHTML =
    '<tr><th>诊断量</th><th>值</th></tr>' +
    rows.map(rr => `<tr><td>${rr[0]}</td><td class="mono">${rr[1]}</td></tr>`).join('');
})();
paramTable('tabMx', MX.params, [
  { label: '参数', get: p => `<span class="mono">${p.parameter}</span>` },
  { label: '估计值', get: p => `<b>${fmt(p.value,4)}</b>` },
  { label: 'SE (lin)', get: p => fmt(p.se,3) },
  { label: 'RSE%', get: p => rseBadge(p.rse) },
  { label: '95% CI', get: p => `${fmt(p.lo,3)} – ${fmt(p.hi,3)}` },
  { label: 'IIV CV%', get: p => p.cv != null ? p.cv.toFixed(1) : '—' }
]);
(function () {
  const fin = MX.variants.find(v => v.folder === 'theophylline_final_ka_cWT');
  if (!fin) return;
  const wald = Object.fromEntries(fin.wald.map(w => [w.param, w.p]));
  document.getElementById('tabMxFinal').innerHTML =
    '<tr><th>参数</th><th>估计值</th><th>SE</th><th>RSE%</th><th>95% CI</th><th>Wald p</th></tr>' +
    fin.params.map(p =>
      `<tr><td class="mono">${p.parameter}</td><td><b>${fmt(p.value,4)}</b></td>` +
      `<td>${fmt(p.se,3)}</td><td>${rseBadge(p.rse)}</td>` +
      `<td>${fmt(p.lo,3)} – ${fmt(p.hi,3)}</td>` +
      `<td>${wald[p.parameter] != null ? wald[p.parameter].toFixed(4) : '—'}</td></tr>`
    ).join('');
})();
(function () {
  document.getElementById('tabMxShrink').innerHTML =
    '<tr><th>参数</th><th>收缩率% (mode)</th><th>收缩率% (mean)</th><th>收缩率% (condDist)</th></tr>' +
    MX.shrinkage.map(s =>
      `<tr><td class="mono">${s.parameter}</td><td>${s.mode}</td><td>${s.mean}</td>` +
      `<td>${s.condDist}</td></tr>`).join('');
})();
(function () {
  document.getElementById('tabCross').innerHTML =
    '<tr><th>参数</th><th>NONMEM FOCE-I</th><th>Monolix SAEM</th><th>相对差</th><th>说明</th></tr>' +
    X.typical.map(t =>
      `<tr><td class="mono">${t.label} (${t.unit})</td><td>${fmt(t.nm,4)}</td>` +
      `<td>${fmt(t.mx,4)}</td>` +
      `<td style="color:${Math.abs(t.diff_pct)<=2?'#5ad8a6':'#f0b429'}">` +
      `${t.diff_pct>0?'+':''}${t.diff_pct.toFixed(2)}%</td>` +
      `<td style="text-align:left;color:#8b98b8">结构参数</td></tr>`).join('') +
    X.iiv.map(t =>
      `<tr><td class="mono">IIV ${t.label} (CV%)</td><td>${fmt(t.nm,3)}</td>` +
      `<td>${fmt(t.mx,3)}</td>` +
      `<td style="color:#8b98b8">${fmt(t.nm-t.mx,3)} pp</td>` +
      `<td style="text-align:left;color:#8b98b8">随机效应（模型设定不同）</td></tr>`).join('') +
    `<tr><td class="mono">残差误差</td><td>比例 ${fmt(X.residual.nm_prop_cv,3)}% CV + 加性 ${fmt(X.residual.nm_add_sd,3)} mg/L</td>` +
    `<td>combined1: a=${fmt(X.residual.mx_a,3)}, b=${fmt(X.residual.mx_b,3)}</td>` +
    `<td style="color:#8b98b8">—</td><td style="text-align:left;color:#8b98b8">参数化方式不同，不可直接比</td></tr>` +
    `<tr><td class="mono">t½ = ln2·V/CL (h)</td><td>${fmt(X.t_half.nm,3)}</td>` +
    `<td>${fmt(X.t_half.mx,3)}</td>` +
    `<td style="color:#5ad8a6">${(((X.t_half.nm-X.t_half.mx)/X.t_half.mx)*100).toFixed(2)}%</td>` +
    `<td style="text-align:left;color:#8b98b8">派生参数</td></tr>` +
    `<tr><td class="mono">目标函数值</td><td>OFV ${fmt(D.nonmem.ofv,5)}（FOCE-I，不含常数）</td>` +
    `<td>OFV ${fmt(D.monolix.ofv,5)}（重要性采样 −2LL）</td>` +
    `<td style="color:#e8684a">不可比</td>` +
    `<td style="text-align:left;color:#8b98b8">常数项/算法不同，禁止跨引擎比较 OFV</td></tr>`;
})();

/* source code blocks */
function putPre(id, txt) {
  const el = document.getElementById(id);
  if (el) el.textContent = txt;
}
putPre('srcMod', D.sources.mod);
putPre('srcMlx', D.sources.mlxtran);
putPre('srcMlxFinal', D.sources.mlxtran_final);
putPre('srcPrep', D.sources.prep);
putPre('srcGof', D.sources.gof);
"""


def render_html(data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    js = JS.replace("__DATA__", payload)

    meta = data["meta"]
    nm, mx, x = data["nonmem"], data["monolix"], data["cross"]
    nmr, mxr = nm["raw"], mx["raw"]

    def pct(a, b):
        return "%+.1f%%" % ((a - b) / b * 100)

    stats_nm = f"""
  <div class="stat nm"><div class="k">OFV (FOCE-I)</div>
    <div class="v">{nm['ofv']:.3f}</div></div>
  <div class="stat nm"><div class="k">KA</div>
    <div class="v">{nmr['ka']:.3f}<small>h⁻¹</small></div></div>
  <div class="stat nm"><div class="k">CL</div>
    <div class="v">{nmr['cl']:.4f}<small>L/h/kg</small></div></div>
  <div class="stat nm"><div class="k">V</div>
    <div class="v">{nmr['v']:.3f}<small>L/kg</small></div></div>
  <div class="stat nm"><div class="k">t½ = ln2·V/CL</div>
    <div class="v">{nmr['t_half']:.2f}<small>h</small></div></div>
  <div class="stat nm"><div class="k">最小化 / 协方差</div>
    <div class="v" style="font-size:15px">{'成功' if nm['minimization_successful'] else '失败'}
      <small>{nm['nfe']} 次函数评估 · {nm['t_est']}s</small></div></div>"""

    stats_mx = f"""
  <div class="stat mx"><div class="k">OFV (重要性采样 −2LL)</div>
    <div class="v">{mx['ofv']:.2f}<small>SE {mx['ll_se']}</small></div></div>
  <div class="stat mx"><div class="k">ka_pop</div>
    <div class="v">{mxr['ka']:.3f}<small>h⁻¹</small></div></div>
  <div class="stat mx"><div class="k">Cl_pop</div>
    <div class="v">{mxr['cl']:.4f}<small>L/h/kg</small></div></div>
  <div class="stat mx"><div class="k">V_pop</div>
    <div class="v">{mxr['v']:.3f}<small>L/kg</small></div></div>
  <div class="stat mx"><div class="k">BIC / AIC</div>
    <div class="v" style="font-size:15px">{mx['bic']:.1f} / {mx['aic']:.1f}</div></div>
  <div class="stat mx"><div class="k">SAEM 迭代</div>
    <div class="v" style="font-size:15px">{mx['saem']['exploratory']}+{mx['saem']['smoothing']}
      <small>Autostop · {mx['saem']['elapsed_s']}s</small></div></div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Theophylline popPK — NONMEM × Monolix 双引擎建模报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<header>
  <h1>Theophylline 群体药动学（popPK）建模报告 — NONMEM × Monolix 双引擎</h1>
  <div class="sub">
    数据：<code>theophylline_data.csv</code>（经典 theophylline 数据集 · {meta['n_id']} 名受试者 ·
    {meta['dose']} ·
    {meta['n_obs']} 个观测 · 体重 {meta['wt_range'][0]:.1f}–{meta['wt_range'][1]:.1f} kg ·
    男 {meta['sex_counts']['M']} / 女 {meta['sex_counts']['F']}）。
    剂量按 <b>mg/kg</b> 给药，因此 CL、V 均为每千克单位（L/h/kg、L/kg）。<br/>
    引擎：<span class="tag nm">NONMEM 7.6 · FOCE-I · PsN execute</span>
    <span class="tag mx">MonolixSuite 2024R1 · SAEM · --no-gui 无界面</span>
    本页所有数值均直接来自仓库中已提交的结果文件（run1.ext / run1.cor / run1.phi / sdtab1 ·
    populationParameters.txt / predictions.txt / LogLikelihood / FisherInformation），未重新运行估计。
  </div>
  <nav>
    <a href="#model">模型与建模方法</a>
    <a href="#nonmem">NONMEM 结果</a>
    <a href="#monolix">Monolix 结果</a>
    <a href="#cross">双引擎对比</a>
    <a href="#repro">复现步骤</a>
  </nav>
</header>

<!-- ============================ MODEL & METHOD ============================ -->
<h2 class="sec" id="model">一、模型与建模方法</h2>
<div class="sec-desc">
  同一份数据、同一个结构模型（一级吸收单房室），分别用两种主流群体 PK 工具独立估计，
  以验证工作流可复现、跨引擎结果一致。
</div>

<div class="two-col">
  <div class="card">
    <h3>1.1 结构模型 — 一级吸收单房室（口服）</h3>
    <div class="desc">NONMEM <code>ADVAN2 TRANS2</code>；Monolix 内置库模型 <code>lib:oral1_1cpt_kaVCl</code>。两者数学上完全等价。</div>
    <div class="eq">
      <b>房室：</b> 吸收室 (depot, CMT=1) → 中央室 (central, CMT=2)<br/>
      <b>血药浓度：</b><br/>
      &nbsp;&nbsp;C(t) = (F·D·k<sub>a</sub>) / (V·(k<sub>a</sub>−k)) · (e<sup>−k·t</sup> − e<sup>−k<sub>a</sub>·t</sup>)<br/>
      <b>消除速率：</b> k = CL / V<br/>
      <b>典型达峰时间：</b> t<sub>max</sub> = ln(k<sub>a</sub>/k) / (k<sub>a</sub>−k)
      ≈ {nmr['t_max_typ']:.2f} h（NONMEM 典型值）
    </div>
    <div class="pill-row">
      <span class="pill">ka — 一级吸收速率常数</span>
      <span class="pill">V — 表观分布容积</span>
      <span class="pill">CL — 表观清除率</span>
      <span class="pill">F 并入剂量（mg/kg 给药）</span>
    </div>
  </div>

  <div class="card">
    <h3>1.2 统计模型 — 随机效应与残差误差</h3>
    <div class="desc">个体间变异（IIV）用对数正态（指数）模型；残差误差用「比例 + 加性」组合模型。</div>
    <div class="eq">
      <b>NONMEM（含体重异速缩放协变量）：</b><br/>
      &nbsp;&nbsp;KA<sub>i</sub> = θ<sub>KA</sub> · e<sup>η₁ᵢ</sup><br/>
      &nbsp;&nbsp;CL<sub>i</sub> = θ<sub>CL</sub> · (WT/70)<sup>0.75</sup> · e<sup>η₂ᵢ</sup><br/>
      &nbsp;&nbsp;V<sub>i</sub>&nbsp; = θ<sub>V</sub> · (WT/70)<sup>1.00</sup> · e<sup>η₃ᵢ</sup><br/>
      &nbsp;&nbsp;η ~ N(0, Ω)，Ω = diag(ω²₁, ω²₂, ω²₃)<br/>
      &nbsp;&nbsp;Y<sub>ij</sub> = IPRED·(1+ε₁) + ε₂，ε₁~N(0,σ²₁)，ε₂~N(0,σ²₂)<br/><br/>
      <b>Monolix Base（无协变量，walkthrough 主运行）：</b><br/>
      &nbsp;&nbsp;P<sub>i</sub> = P<sub>pop</sub> · e<sup>ηᵢ</sup>（logNormal，P ∈ {{ka, V, Cl}}）<br/>
      &nbsp;&nbsp;combined1: sd = a + b·f（a 加性 mg/L，b 比例，c=1 固定）
    </div>
    <div class="note">
      注意两处模型设定差异：① NONMEM 控制流固定了体重异速指数（0.75/1.0，参考 70 kg），
      Monolix Base 不含协变量；② 误差模型参数化不同（NONMEM σ²₁ 为比例方差、σ²₂ 为加性方差；
      Monolix combined1 为 a + b·f 的<b>标准差</b>形式）。因此 IIV / 残差项只做定性对比。
    </div>
  </div>
</div>

<div class="two-col">
  <div class="card">
    <h3>1.3 估计方法</h3>
    <table>
      <tr><th></th><th><span class="tag nm">NONMEM</span></th><th><span class="tag mx">Monolix</span></th></tr>
      <tr><td>算法</td><td>FOCE-I（条件估计 + 交互）</td><td>SAEM（随机逼近 EM）</td></tr>
      <tr><td>驱动</td><td>PsN <code>execute</code> → nmfe76</td><td><code>monolix.sh --no-gui</code></td></tr>
      <tr><td>个体参数</td><td>POSTHOC 经验贝叶斯 (EBE)</td><td>条件分布 / 条件众数</td></tr>
      <tr><td>标准误</td><td>协方差步（$COVARIANCE，PRINT=E 特征值）</td><td>线性化 Fisher 信息 (FIM)</td></tr>
      <tr><td>似然值</td><td>OFV = −2LL（不含 N·log2π 常数 {nm['obj_const']:.1f}）</td>
        <td>重要性采样 −2LL（Monte-Carlo SE = {mx['ll_se']}）</td></tr>
      <tr><td>收敛</td><td>{nm['nfe']} 次函数评估 · {nm['sigdig']} 位有效数字 · {nm['t_est']} s</td>
        <td>探索 {mx['saem']['exploratory']} + 平滑 {mx['saem']['smoothing']} 迭代（Autostop）· {mx['saem']['elapsed_s']} s</td></tr>
    </table>
    <div class="note">
      协变量建模（Monolix 侧）：COSSAC 策略在 ka / V / Cl 上筛选 WEIGHT、SEX，
      停止准则为 LRT（0.05, 0.01）与相关阈值（0.3, 0.01），最终选出 <b>ka ~ WEIGHT</b>；
      报告版本对体重做中心化 <code>ka ~ (WT−70)</code> 以保证 ka_pop 可解释（Wald p = 0.023）。
      NONMEM 侧则直接采用文献常用的固定异速缩放（CL∝WT<sup>0.75</sup>, V∝WT<sup>1</sup>）。
    </div>
  </div>

  <div class="card">
    <h3>1.4 数据准备与建模流程</h3>
    <ul class="tight">
      <li><b>数据转换</b>（<code>prep_data.R</code>）：Monolix 长表 → NONMEM 事件记录格式
        （剂量行 EVID=1/CMT=1/MDV=1，观测行 EVID=0/CMT=2/MDV=0，缺失用 <code>.</code>）。
        踩坑：<code>read.csv</code> 默认不把 <code>"."</code> 当缺失，需 <code>na.strings=c("NA",".")</code>。</li>
      <li><b>控制流编写</b>：按 easy-nonmem skill 的 bundled 参考（ADVAN 目录 / $INPUT 规范）
        确认一级吸收单房室 = ADVAN2 TRANS2，观测默认中央室。</li>
      <li><b>运行</b>：<code>execute run1.mod -directory=theo_run -threads=4</code>；
        Monolix 侧用 x86shim 强制插件以 x86_64 编译（Apple Silicon）。</li>
      <li><b>诊断</b>（<code>gof_plots.R</code>）：读取 $TABLE 输出 sdtab1 画 GOF；
        踩坑：文件首行是 <code>TABLE NO. 1</code> 横幅，需 <code>skip=1</code>，剂量行 DV 为 NA 需剔除。</li>
      <li><b>验收标准</b>：MINIMIZATION SUCCESSFUL、协方差步完成、ETABAR≈0、
        收缩率 &lt;20–30%、GOF 无系统性趋势。</li>
    </ul>
    <details>
      <summary>run1.mod — NONMEM 控制流（点击查看全文）</summary>
      <pre id="srcMod" class="mono"></pre>
    </details>
    <details>
      <summary>theophylline_project.mlxtran — Monolix Base 项目</summary>
      <pre id="srcMlx" class="mono"></pre>
    </details>
    <details>
      <summary>theophylline_final_ka_cWT.mlxtran — Monolix 最终协变量模型</summary>
      <pre id="srcMlxFinal" class="mono"></pre>
    </details>
    <details>
      <summary>prep_data.R / gof_plots.R — 数据准备与 GOF 绘图脚本</summary>
      <pre id="srcPrep" class="mono"></pre>
      <pre id="srcGof" class="mono"></pre>
    </details>
  </div>
</div>

<!-- ============================ NONMEM ============================ -->
<h2 class="sec" id="nonmem">二、NONMEM 结果 <span class="chip">FOCE-I · ADVAN2 TRANS2 · 全异速体重缩放</span></h2>
<div class="sec-desc">
  <code>run1.lst</code>：MINIMIZATION SUCCESSFUL，协方差步完成，相关矩阵最小特征值
  {nm['eigen_min']:.2e}（&gt;0，无病态方向）。ETABAR 三项 p 值均 &gt;0.89 → η 均值与 0 无显著差异。
</div>
<div class="stats">{stats_nm}</div>

<div class="grid">
  <div class="card">
    <h3>N1 · 收敛历程（run1.ext）</h3>
    <div class="desc">OFV 从初值 185.9 降至 {nm['ofv']:.3f}，第 23 次迭代达到 3 位有效数字收敛。</div>
    <div class="chart" id="nmConv"></div>
  </div>
  <div class="card">
    <h3>N2 · 固定效应 θ — 估计值与 95% CI</h3>
    <div class="desc">对数轴森林图；CI 由协方差步 SE 计算（θ 为正值有界参数，CI 取对数尺度回变换）。</div>
    <div class="chart" id="nmForest"></div>
  </div>
</div>

<div class="card wide" style="margin-top:16px">
  <h3>N3 · 个体拟合 — 观测 (DV) vs 个体预测 (IPRED)</h3>
  <div class="desc">
    白色散点 = 实测浓度；绿线 = NONMEM IPRED（POSTHOC EBE）；黄色虚线 = 由个体参数
    (KA, CL, V，含体重缩放) 解析重算的密集模型曲线（与 IPRED 重合即验证 ADVAN2 解正确）；
    紫点线 = 群体预测 PRED。可选单个受试者或 12 人叠加。
  </div>
  <div class="sel"><label>受试者</label><select id="nmSubjSel"></select></div>
  <div class="chart tall" id="nmFits"></div>
</div>

<div class="grid">
  <div class="card">
    <h3>N4 · GOF — DV vs IPRED / PRED</h3>
    <div class="desc">点贴近 y=x 对角线；IPRED（绿）比 PRED（紫）显著收紧 → IIV 被随机效应正确吸收。</div>
    <div class="chart" id="nmGof"></div>
  </div>
  <div class="card">
    <h3>N5 · CWRES 诊断</h3>
    <div class="desc">条件加权残差 vs 时间 / vs PRED：围绕 0（虚线）随机散布，无漏斗形或趋势 → 结构模型与组合误差设定合理。±2 参考线内占绝大多数。</div>
    <div class="chart" id="nmCwres"></div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h3>N6 · 个体随机效应 η（run1.phi，POSTHOC EBE）</h3>
    <div class="desc">柱高 = η 点估计；悬停可见后验标准差 ETC。ID9 的 η_KA≈+1.38 最大（吸收快个体）。</div>
    <div class="chart" id="nmEta"></div>
  </div>
  <div class="card">
    <h3>N7 · 参数估计相关矩阵（run1.cor）</h3>
    <div class="desc">θ_CL×θ_V 相关 0.86 偏高但可接受（单房室口服经典相关对）；未出现 |r|&gt;0.95 的过参数化信号。</div>
    <div class="chart" id="nmCorr"></div>
  </div>
</div>

<div class="two-col" style="margin-top:16px">
  <div class="card">
    <h3>N8 · 最终参数估计一览</h3>
    <table id="tabNm"></table>
    <div class="note">
      ω² → CV%：IIV_KA = {nmr['cv_ka']:.0f}%、IIV_CL = {nmr['cv_cl']:.0f}%、IIV_V = {nmr['cv_v']:.0f}%（√(e^ω²−1)）。
      残差：比例 {nmr['res_prop_cv']:.1f}% CV + 加性 {nmr['res_add_sd']:.3f} mg/L。
      70 kg 典型个体：CL = {nmr['cl_70']:.2f} L/h，V = {nmr['v_70']:.1f} L，t½ = {nmr['t_half']:.2f} h —
      与茶碱文献值（CL≈0.04 L/h/kg，t½≈8 h）一致。
    </div>
  </div>
  <div class="card">
    <h3>N9 · ETABAR 与收缩率（run1.lst）</h3>
    <table id="tabNmShrink"></table>
    <div class="note">
      所有 η 收缩率（SD 尺度 {nm['eta_shrink_sd'][0]:.1f}/{nm['eta_shrink_sd'][1]:.1f}/{nm['eta_shrink_sd'][2]:.1f}%）
      远低于 20–30% 警戒线；相对信息量 ≈ 85–89% → 每人 10 点的采样设计足以支撑 EBE 诊断。
    </div>
  </div>
</div>

<!-- ============================ MONOLIX ============================ -->
<h2 class="sec" id="monolix">三、Monolix 结果 <span class="chip">SAEM · oral1_1cpt_kaVCl · combined1 · COSSAC 协变量筛选</span></h2>
<div class="sec-desc">
  Base 模型（无协变量）为 walkthrough 主运行；随后 COSSAC 筛选出 ka~WEIGHT，
  并给出中心化最终模型与异速生长对照模型。似然值均由重要性采样（IS）计算。
</div>
<div class="stats">{stats_mx}</div>

<div class="grid">
  <div class="card">
    <h3>M1 · Base 群体参数 — 估计值与 95% CI</h3>
    <div class="desc">线性化 FIM 的 SE；对数轴森林图。V_pop、Cl_pop 精估（RSE&lt;9%），ka_pop 因吸收相点数少 RSE≈21%。</div>
    <div class="chart" id="mxForest"></div>
  </div>
  <div class="card">
    <h3>M2 · GOF — Obs vs indivPred / popPred</h3>
    <div class="desc">SAEM 条件估计的个体预测贴近 y=x；群体预测的分散体现 IIV（ω_ka≈73% CV 最大）。</div>
    <div class="chart" id="mxGof"></div>
  </div>
</div>

<div class="card wide" style="margin-top:16px">
  <h3>M3 · 个体拟合 — 观测 vs SAEM 个体预测</h3>
  <div class="desc">黄色虚线 = 用 SAEM 个体参数 (ka, V, Cl) 解析重算的密集曲线；绿线 = indivPred_SAEM；紫点线 = popPred。</div>
  <div class="sel"><label>受试者</label><select id="mxSubjSel"></select></div>
  <div class="chart tall" id="mxFits"></div>
</div>

<div class="grid">
  <div class="card">
    <h3>M4 · IWRES vs 时间</h3>
    <div class="desc">个体加权残差围绕 0 随机分布、无时间趋势 → combined1(a,b) 误差模型合适。</div>
    <div class="chart" id="mxIwres"></div>
  </div>
  <div class="card">
    <h3>M5 · 个体随机效应 η（条件估计）</h3>
    <div class="desc">η_ka 跨度最大（ID9 ≈ +1.45，与 NONMEM 同一受试者、同一方向）；η_V 收缩 13.9%。</div>
    <div class="chart" id="mxEta"></div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h3>M6 · 参数相关矩阵（线性化 FIM）</h3>
    <div class="desc">a 与 b 强负相关（r≈−0.90）是 combined 误差的固有特征；固定效应之间相关温和。</div>
    <div class="chart tall" id="mxCorr"></div>
  </div>
  <div class="card">
    <h3>M7 · COSSAC 协变量搜索（线性化 −2LL）</h3>
    <div class="desc">
      M1 无协变量 → M2 加 V~WEIGHT → M3 加 ka~WEIGHT → M4 两者 → M5 ka~WEIGHT+V~SEX。
      Best = <b>M3（ka~WEIGHT）</b>：M4 的 −2LL 更低但 BICc 回升，按停止准则不再加协变量；SEX 未入选。
    </div>
    <div class="chart tall" id="mxMb"></div>
  </div>
</div>

<div class="card wide" style="margin-top:16px">
  <h3>M8 · 模型变体比较（重要性采样判据）</h3>
  <div class="desc">
    四个已运行模型：Base、ka~WEIGHT（未中心化）、ka~(WT−70)（最终报告模型）、V,Cl~log(WT/70) 自由指数（异速对照）。
    n=12 时 BICc 惩罚重，异速模型未优于 Base；加 ka 协变量的两个模型 OFV/AIC/BIC/BICc 全面占优。
  </div>
  <div class="two-col">
    <div class="chart" id="mxModels"></div>
    <div>
      <h3 style="font-size:13px;margin-top:4px">最终模型 ka ~ (WT−70) 参数表</h3>
      <table id="tabMxFinal"></table>
      <div class="note">
        β_ka_cWEIGHT = 0.0422（每 +1 kg，ka ×e<sup>0.042</sup>≈1.043），Wald p = 0.0228，t-Test p = 0.0389。
        未中心化版本 ka_pop 的 RSE&gt;500%（外推至 WT=0），故报告用中心化版本。
      </div>
    </div>
  </div>
</div>

<div class="two-col">
  <div class="card">
    <h3>M9 · Base 模型完整参数表</h3>
    <table id="tabMx"></table>
  </div>
  <div class="card">
    <h3>M10 · η 收缩率</h3>
    <table id="tabMxShrink"></table>
    <div class="note">
      V 的收缩率 13.9% 与 NONMEM 侧（{nm['eta_shrink_sd'][2]:.1f}%）一致；
      ka 条件均值出现 −0.65% 的轻微负收缩，是小样本条件抽样波动的正常现象（mode 收缩 +2.6%）。
    </div>
  </div>
</div>

<!-- ============================ CROSS ============================ -->
<h2 class="sec" id="cross">四、双引擎交叉验证 <span class="chip">NONMEM FOCE-I × Monolix SAEM · 同一数据</span></h2>
<div class="sec-desc">
  结构参数三个 θ 的相对差均 ≤2.2%，且 95% CI 大幅重叠；{x['n_matched']} 个匹配时间点的个体预测
  RMSE 仅 {x['rmse_ipred']} mg/L；η（EBE）逐人方向一致。这是两个独立实现、独立算法之间期望达到的可复现性水平。
</div>

<div class="grid">
  <div class="card">
    <h3>X1 · 典型参数 — 点估计 + 95% CI 对比</h3>
    <div class="desc">上排（蓝）NONMEM θ，下排（黄）Monolix pop；对数轴。三对 CI 均互相覆盖对方点估计。</div>
    <div class="chart" id="xTyp"></div>
  </div>
  <div class="card">
    <h3>X2 · 相对差 (NM−MLX)/MLX</h3>
    <div class="desc">
      KA {pct(x['typical'][0]['nm'], x['typical'][0]['mx'])} ·
      CL {pct(x['typical'][1]['nm'], x['typical'][1]['mx'])} ·
      V {pct(x['typical'][2]['nm'], x['typical'][2]['mx'])} —
      全部在 ±2.2% 内（绿色 ≤2%）。
    </div>
    <div class="chart" id="xDiff"></div>
  </div>
</div>

<div class="grid">
  <div class="card">
    <h3>X3 · 个体预测逐点对比（同 ID 同时间）</h3>
    <div class="desc">NONMEM IPRED（POSTHOC）vs Monolix indivPred（SAEM 条件估计），{x['n_matched']}/120 点精确匹配。</div>
    <div class="chart" id="xIpred"></div>
  </div>
  <div class="card">
    <h3>X4 · 随机效应 η 对比（EBE vs 条件估计）</h3>
    <div class="desc">每个点是一名受试者；两引擎 η 沿 y=x 同方向、同量级。ID9 在两侧都是 η_KA 最大的离群个体。</div>
    <div class="chart" id="xEbe"></div>
  </div>
</div>

<div class="card wide" style="margin-top:16px">
  <h3>X5 · 个体参数 vs 体重（模型设定差异的直接体现）</h3>
  <div class="desc">
    NONMEM（圆点）显式含 WT<sup>0.75</sup>/WT<sup>1</sup> 缩放 → 个体 CL、V 随体重呈上升趋势；
    Monolix Base（三角）无协变量 → 与体重无关的随机散布。这解释了两侧 IIV 的差异
    （NONMEM 的 IIV_CL={nmr['cv_cl']:.0f}% 已扣除体重效应；Monolix 的 ω_Cl={mxr['cv_cl']:.0f}% CV 仍含体重变异）。
  </div>
  <div class="chart" id="xCov"></div>
</div>

<div class="card wide">
  <h3>X6 · 汇总对照表</h3>
  <table id="tabCross"></table>
</div>

<!-- ============================ REPRO ============================ -->
<h2 class="sec" id="repro">五、复现步骤</h2>
<div class="two-col">
  <div class="card">
    <h3>NONMEM（需 NONMEM 7.6 + PsN）</h3>
    <div class="eq mono" style="font-family:Menlo,monospace;font-size:12px">
cd examples/nonmem-theophylline<br/>
Rscript prep_data.R<br/>
execute run1.mod -directory=theo_run -threads=4<br/>
Rscript gof_plots.R
    </div>
  </div>
  <div class="card">
    <h3>Monolix（需 MonolixSuite 2024R1，Apple Silicon 加 x86shim）</h3>
    <div class="eq mono" style="font-family:Menlo,monospace;font-size:12px">
cd examples/monolix-theophylline<br/>
PATH="$PWD/../../skills/monolix-cli/x86shim:$PATH" \\<br/>
&nbsp;&nbsp;/Applications/MonolixSuite2024R1.app/Contents/Resources/\\<br/>
&nbsp;&nbsp;monolixSuite/bin/monolix.sh --no-gui \\<br/>
&nbsp;&nbsp;-p "$PWD/theophylline_project.mlxtran" \\<br/>
&nbsp;&nbsp;-o "$PWD/theophylline_walkthrough" --mode basic
    </div>
  </div>
</div>

<footer>
  报告由 <code>scripts/build_theophylline_report.py</code> 从仓库内已提交的结果文件自动生成 ·
  图表：Apache ECharts 6（CDN）· 数据文件：
  <code>examples/nonmem-theophylline/</code>（run1.mod / run1.lst / run1.ext / run1.cor / run1.phi / sdtab1）与
  <code>examples/monolix-theophylline/theophylline_walkthrough/</code>（populationParameters / predictions /
  LogLikelihood / FisherInformation / IndividualParameters）·
  叙述性 walkthrough 见 <code>docs/walkthrough-theophylline.md</code>。
</footer>

<script>{js}</script>
</body>
</html>
"""
    return html
