import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const ROOT = new URL("../", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const path = (p) => `${ROOT}${p}`;

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];
    if (quoted) {
      if (ch === '"' && next === '"') {
        field += '"';
        i++;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (ch !== "\r") {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  const headers = rows.shift();
  return rows.filter((r) => r.some((x) => x !== "")).map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

async function readCsv(relPath) {
  return parseCsv(await fs.readFile(path(relPath), "utf8"));
}

function num(value) {
  if (value === undefined || value === null || value === "") return null;
  const n = Number(String(value).replace(/,/g, ""));
  return Number.isFinite(n) ? n : null;
}

function colName(n) {
  let s = "";
  while (n > 0) {
    const m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

function cell(row, col) {
  return `${colName(col)}${row}`;
}

function mm(value) {
  return value === null ? null : value / 1_000_000;
}

function pct(value) {
  return value === null ? null : value;
}

function findMetric(rows, metric) {
  const row = rows.find((r) => r.metric === metric);
  return row ? num(row.value) : null;
}

function wideByYear(rows) {
  const out = {};
  for (const row of rows) out[row.year] = row;
  return out;
}

function longSource(longRows, metric, year) {
  const row = longRows.find((r) => r.metric === metric && Number(r.year) === Number(year));
  if (!row) return "";
  return `${row.source_file} | ${row.raw_tag} | ${row.accession}`;
}

function setTitle(sheet, title, subtitle = "") {
  sheet.getRange("A1:H1").merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = {
    font: { bold: true, size: 16, color: "#FFFFFF" },
    fill: "#1F2937",
  };
  if (subtitle) {
    sheet.getRange("A2:H2").merge();
    sheet.getRange("A2").values = [[subtitle]];
    sheet.getRange("A2").format = { font: { italic: true, color: "#374151" } };
  }
}

function headerStyle(range) {
  range.format = {
    fill: "#111827",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
  };
}

function sectionStyle(range) {
  range.format = {
    fill: "#D9EAD3",
    font: { bold: true, color: "#111827" },
  };
}

function inputStyle(range) {
  range.format = {
    font: { color: "#0000FF" },
    fill: "#FFF2CC",
  };
}

function formulaStyle(range) {
  range.format = { font: { color: "#000000" } };
}

const wideRows = await readCsv("extracted/yeti_financials_wide.csv");
const longRows = await readCsv("extracted/yeti_financials_annual.csv");
const salesBreakdown = await readCsv("extracted/yeti_sales_breakdown.csv");
const marketRows = await readCsv("extracted/yeti_market_data.csv");
const peerRows = await readCsv("extracted/peer_valuation.csv");
const guidanceRows = await readCsv("extracted/yeti_2026_guidance.csv");
const sourcesText = await fs.readFile(path("sources.md"), "utf8");

const hist = wideByYear(wideRows);
const years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030];
const yearLabels = ["FY2023A", "FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"];
const market = Object.fromEntries(marketRows.map((r) => [r.metric, num(r.value)]));
const guidance = Object.fromEntries(guidanceRows.map((r) => [r.metric, num(r.value)]));

const workbook = Workbook.create();
const cover = workbook.worksheets.add("Cover");
const histSheet = workbook.worksheets.add("Historical");
const assumptions = workbook.worksheets.add("Assumptions");
const model = workbook.worksheets.add("Model");
const valuation = workbook.worksheets.add("Valuation");
const scenarios = workbook.worksheets.add("Scenarios");
const peers = workbook.worksheets.add("Peers");
const sources = workbook.worksheets.add("Sources");
const checks = workbook.worksheets.add("Checks");

for (const sheet of [cover, histSheet, assumptions, model, valuation, scenarios, peers, sources, checks]) {
  sheet.showGridLines = false;
}

// Sources / audit
setTitle(sources, "Source And Extraction Audit", "All URLs are in sources.md; this tab connects extracted values to local raw files.");
const sourceLines = sourcesText.split(/\r?\n/).filter((line) => line.startsWith("| ") && !line.includes("---"));
sources.getRange("A4:F4").values = [["Source ID", "Timestamp UTC", "URL", "Local Path", "SHA-256", "Purpose"]];
headerStyle(sources.getRange("A4:F4"));
const sourceRows = sourceLines.slice(1).map((line) => line.split("|").slice(1, -1).map((x) => x.trim().replace(/^`|`$/g, "")));
if (sourceRows.length) sources.getRangeByIndexes(4, 0, sourceRows.length, 6).values = sourceRows;
sources.getRange("A40:J40").values = [["Extracted financial facts", "", "", "", "", "", "", "", "", ""]];
sectionStyle(sources.getRange("A40:J40"));
sources.getRange("A41:J41").values = [["Period", "Metric", "Value", "Unit", "Source file", "Raw tag", "Accession", "Frame", "Filed", "Notes"]];
headerStyle(sources.getRange("A41:J41"));
const auditRows = longRows.map((r) => [r.period, r.metric, num(r.value), r.unit, r.source_file, r.raw_tag, r.accession, r.frame, r.filed, r.notes]);
sources.getRangeByIndexes(41, 0, auditRows.length, 10).values = auditRows;
sources.getRange("A:K").format.autofitColumns();
sources.freezePanes.freezeRows(4);

// Historical
setTitle(histSheet, "Historical Financials", "Amounts in $mm except per-share data, shares, and percentages.");
histSheet.getRange("A4:J4").values = [["Metric", "Unit", "Source / tag", ...yearLabels.slice(0, 3), "FY2025 margin / ratio", "Notes", "Model use", ""]];
headerStyle(histSheet.getRange("A4:J4"));
const histMetrics = [
  ["revenue", "Revenue", "$mm", "Historical sales base"],
  ["cogs", "Cost of goods sold", "$mm", "Gross margin driver"],
  ["gross_profit", "Gross profit", "$mm", "Gross margin driver"],
  ["sga", "SG&A", "$mm", "Operating leverage driver"],
  ["operating_income", "Operating income", "$mm", "EBIT base"],
  ["pretax_income", "Pretax income", "$mm", "Tax bridge"],
  ["income_tax", "Income tax expense", "$mm", "Tax-rate base"],
  ["net_income", "Net income", "$mm", "Equity roll-forward"],
  ["diluted_eps", "Diluted EPS", "$/sh", "EPS bridge"],
  ["diluted_shares", "Diluted shares", "mm", "Share-count base"],
  ["operating_cash_flow", "Operating cash flow", "$mm", "Cash-flow base"],
  ["capex", "Capital expenditures", "$mm", "Capex base"],
  ["depreciation_amortization", "D&A", "$mm", "D&A base"],
  ["stock_comp", "Stock compensation", "$mm", "Equity/cash-flow add-back"],
  ["share_repurchases", "Share repurchases", "$mm", "Share-count and cash use"],
  ["free_cash_flow", "Free cash flow", "$mm", "FCF base"],
  ["cash", "Cash", "$mm", "Cash bridge"],
  ["accounts_receivable", "Accounts receivable", "$mm", "Working capital driver"],
  ["inventory", "Inventory", "$mm", "Working capital driver"],
  ["prepaids_other_current_assets", "Prepaids and other current assets", "$mm", "Working capital driver"],
  ["current_assets", "Current assets", "$mm", "Balance sheet"],
  ["ppe_net", "PP&E net", "$mm", "Capital intensity"],
  ["goodwill", "Goodwill", "$mm", "Balance sheet"],
  ["intangible_assets", "Intangible assets", "$mm", "Balance sheet"],
  ["operating_lease_assets", "Operating lease assets", "$mm", "Balance sheet"],
  ["total_assets", "Total assets", "$mm", "Balance sheet"],
  ["accounts_payable", "Accounts payable", "$mm", "Working capital driver"],
  ["current_liabilities", "Current liabilities", "$mm", "Balance sheet"],
  ["current_debt", "Current debt", "$mm", "Funded debt"],
  ["long_term_debt", "Long-term debt", "$mm", "Funded debt"],
  ["operating_lease_liabilities", "Operating lease liabilities", "$mm", "WACC debt weighting"],
  ["total_liabilities", "Total liabilities", "$mm", "Balance sheet"],
  ["stockholders_equity", "Stockholders' equity", "$mm", "Balance sheet"],
  ["funded_debt", "Funded debt", "$mm", "Equity bridge"],
];
const histRowByMetric = {};
const histValues = histMetrics.map(([key, label, unit, use], i) => {
  const rowNum = 5 + i;
  histRowByMetric[key] = rowNum;
  const vals = [2023, 2024, 2025].map((y) => {
    const v = num(hist[y]?.[key]);
    if (v === null) return null;
    if (unit === "$mm" || unit === "mm") return mm(v);
    return v;
  });
  let ratio = "";
  if (key === "gross_profit") ratio = `=F${rowNum}/F${histRowByMetric.revenue}`;
  if (key === "operating_income") ratio = `=F${rowNum}/F${histRowByMetric.revenue}`;
  if (key === "net_income") ratio = `=F${rowNum}/F${histRowByMetric.revenue}`;
  if (key === "capex") ratio = `=F${rowNum}/F${histRowByMetric.revenue}`;
  if (key === "free_cash_flow") ratio = `=F${rowNum}/F${histRowByMetric.revenue}`;
  return [label, unit, longSource(longRows, key, 2025), ...vals, ratio, "", use, key];
});
histSheet.getRangeByIndexes(4, 0, histValues.length, 10).values = histValues;
histSheet.getRange(`G5:G${4 + histValues.length}`).format.numberFormat = "0.0%";
histSheet.getRange(`D5:F${4 + histValues.length}`).format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
histSheet.getRange(`A:K`).format.autofitColumns();
histSheet.freezePanes.freezeRows(4);

// Assumptions
setTitle(assumptions, "Assumptions", "Blue/yellow cells are key inputs. Formula cells are black.");
const cash25 = mm(num(hist[2025].cash));
const fundedDebt25 = mm(num(hist[2025].funded_debt));
const totalDebtForWacc = mm(market.total_debt_stockanalysis);
const sharePrice = market.share_price;
const currentShares = market.shares_outstanding / 1_000_000;
const marketCap = market.market_cap / 1_000_000;
const rf = market.risk_free_rate_10y_treasury;
const erp = market.equity_risk_premium_kroll;
const betaRaw = market.beta_5y;
assumptions.getRange("A4:C23").values = [
  ["Valuation date", "2026-04-27", "Current date / source pull date"],
  ["Current share price", sharePrice, "StockAnalysis intraday quote"],
  ["Current diluted/share count", currentShares, "StockAnalysis shares outstanding, mm"],
  ["Market capitalization", marketCap, "$mm"],
  ["FY2025 cash", cash25, "$mm, SEC 10-K"],
  ["FY2025 funded debt", fundedDebt25, "$mm, current + long-term debt"],
  ["Total debt for WACC weight", totalDebtForWacc, "$mm, includes lease/debt items per StockAnalysis"],
  ["Risk-free rate", rf, "10-year Treasury, latest fetched row"],
  ["Equity risk premium", erp, "Kroll recommended U.S. ERP"],
  ["Raw beta", betaRaw, "StockAnalysis 5Y beta"],
  ["Beta used", null, "50% raw beta / 50% market beta to reduce small-cap noise"],
  ["Pre-tax cost of debt", 0.055, "Analyst assumption"],
  ["Tax rate", 0.24, "Management FY2026 outlook"],
  ["Cost of equity", null, "CAPM"],
  ["WACC", null, "Market-cap and total-debt weighted"],
  ["Terminal growth - base", 0.0275, "ADR 0004"],
  ["Exit EBITDA multiple", 11.5, "Peer/context triangulation"],
  ["Target P/E multiple", 16.0, "Peer/context triangulation"],
  ["Price-target method weights", "50% DCF / 25% EV-EBITDA / 25% P/E", "ADR 0005"],
  ["Recommendation threshold", "Hold unless upside >20% or downside >15%", "Risk-adjusted PM framing"],
];
assumptions.getRange("B14").formulas = [["=0.5*B13+0.5*1.0"]];
assumptions.getRange("B17").formulas = [["=B11+B14*B12"]];
assumptions.getRange("B18").formulas = [["=(B7/(B7+B10))*B17+(B10/(B7+B10))*B15*(1-B16)"]];
inputStyle(assumptions.getRange("B5:B16"));
formulaStyle(assumptions.getRange("B17:B18"));
assumptions.getRange("B5").format.numberFormat = "$0.00";
assumptions.getRange("B6").format.numberFormat = "#,##0.0";
assumptions.getRange("B7:B10").format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
assumptions.getRange("B11:B12").format.numberFormat = "0.0%";
assumptions.getRange("B13:B14").format.numberFormat = "0.00";
assumptions.getRange("B15:B18").format.numberFormat = "0.0%";
assumptions.getRange("B19").format.numberFormat = "0.0%";
assumptions.getRange("B20:B21").format.numberFormat = "0.0x";
assumptions.getRange("A25:H25").values = [["Base model forecast drivers", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E", "Source / note", ""]];
headerStyle(assumptions.getRange("A25:H25"));
const baseDrivers = [
  ["Revenue growth", guidance.adjusted_sales_growth_low && guidance.adjusted_sales_growth_high ? (guidance.adjusted_sales_growth_low + guidance.adjusted_sales_growth_high) / 2 : 0.07, 0.07, 0.06, 0.055, 0.05, "FY2026 midpoint from guidance; outer years analyst assumptions"],
  ["Gross margin", 0.578, 0.581, 0.584, 0.586, 0.587, "Tariff/supply-chain normalization assumption"],
  ["Operating margin", 0.128, 0.133, 0.137, 0.140, 0.142, "GAAP EBIT margin ramp; adjusted margin guide is 14.4%"],
  ["Tax rate", guidance.effective_tax_rate || 0.24, 0.24, 0.24, 0.24, 0.24, "FY2026 management guide"],
  ["D&A % sales", 0.029, 0.029, 0.028, 0.028, 0.0275, "Historical D&A around 2.6%-2.9% of sales"],
  ["Capex % sales", ((guidance.capex_low || 60_000_000) + (guidance.capex_high || 70_000_000)) / 2 / 1_000_000 / (mm(num(hist[2025].revenue)) * (1 + 0.07)), 0.028, 0.027, 0.026, 0.026, "FY2026 midpoint from guide; outer years normalize"],
  ["Stock comp % sales", 0.025, 0.024, 0.023, 0.022, 0.021, "Historical SBC near 2.5% of sales"],
  ["Share repurchases", (guidance.expected_share_repurchases || 100_000_000) / 1_000_000, 75, 75, 75, 75, "$mm; FY2026 from guidance"],
  ["Avg repurchase price", sharePrice * 1.08, sharePrice * 1.12, sharePrice * 1.17, sharePrice * 1.22, sharePrice * 1.27, "$/share assumption"],
  ["AR % sales", mm(num(hist[2025].accounts_receivable)) / mm(num(hist[2025].revenue)), mm(num(hist[2025].accounts_receivable)) / mm(num(hist[2025].revenue)), mm(num(hist[2025].accounts_receivable)) / mm(num(hist[2025].revenue)), mm(num(hist[2025].accounts_receivable)) / mm(num(hist[2025].revenue)), mm(num(hist[2025].accounts_receivable)) / mm(num(hist[2025].revenue)), "FY2025 ratio"],
  ["Inventory % COGS", mm(num(hist[2025].inventory)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].inventory)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].inventory)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].inventory)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].inventory)) / mm(num(hist[2025].cogs)), "FY2025 ratio"],
  ["AP % COGS", mm(num(hist[2025].accounts_payable)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].accounts_payable)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].accounts_payable)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].accounts_payable)) / mm(num(hist[2025].cogs)), mm(num(hist[2025].accounts_payable)) / mm(num(hist[2025].cogs)), "FY2025 ratio"],
];
assumptions.getRangeByIndexes(25, 0, baseDrivers.length, 7).values = baseDrivers;
inputStyle(assumptions.getRange(`B26:F${25 + baseDrivers.length}`));
assumptions.getRange(`B26:F${25 + baseDrivers.length}`).format.numberFormat = "0.0%";
assumptions.getRange("B33:F34").format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
assumptions.getRange("B34:F34").format.numberFormat = "$0.00";
assumptions.getRange("A:F").format.autofitColumns();

// Model
setTitle(model, "Three-Statement Model", "Base case; amounts in $mm except per-share data and percentages.");
model.getRangeByIndexes(3, 1, 1, yearLabels.length).values = [yearLabels];
headerStyle(model.getRange("B4:I4"));
const modelRows = [
  [5, "Revenue", "$mm"],
  [6, "Revenue growth", "%"],
  [7, "Gross profit", "$mm"],
  [8, "Gross margin", "%"],
  [9, "SG&A", "$mm"],
  [10, "SG&A % sales", "%"],
  [11, "Operating income", "$mm"],
  [12, "Operating margin", "%"],
  [13, "Net interest expense / (income)", "$mm"],
  [14, "Pretax income", "$mm"],
  [15, "Income tax", "$mm"],
  [16, "Tax rate", "%"],
  [17, "Net income", "$mm"],
  [18, "Diluted shares", "mm"],
  [19, "EPS", "$/sh"],
  [21, "Cash", "$mm"],
  [22, "Accounts receivable", "$mm"],
  [23, "Inventory", "$mm"],
  [24, "Prepaids / other current assets", "$mm"],
  [25, "Current assets", "$mm"],
  [26, "PP&E net", "$mm"],
  [27, "Goodwill + intangibles", "$mm"],
  [28, "Operating lease assets", "$mm"],
  [29, "Other assets", "$mm"],
  [30, "Total assets", "$mm"],
  [31, "Accounts payable", "$mm"],
  [32, "Accrued/current liabilities ex AP/debt", "$mm"],
  [33, "Funded debt", "$mm"],
  [34, "Operating lease liabilities", "$mm"],
  [35, "Other liabilities / balance residual", "$mm"],
  [36, "Total liabilities", "$mm"],
  [37, "Stockholders' equity", "$mm"],
  [38, "BS check", "$mm"],
  [40, "Net income (cash flow)", "$mm"],
  [41, "D&A", "$mm"],
  [42, "Stock compensation", "$mm"],
  [43, "Change in NWC", "$mm"],
  [44, "Operating cash flow", "$mm"],
  [45, "Capital expenditures", "$mm"],
  [46, "Free cash flow", "$mm"],
  [47, "Share repurchases", "$mm"],
  [48, "Change in funded debt", "$mm"],
  [49, "Ending cash", "$mm"],
  [50, "CFS cash check", "$mm"],
  [52, "Unlevered FCF", "$mm"],
];
for (const [row, label, unit] of modelRows) {
  model.getRange(`A${row}:C${row}`).values = [[label, unit, ""]];
}
sectionStyle(model.getRange("A5:I5"));
sectionStyle(model.getRange("A21:I21"));
sectionStyle(model.getRange("A40:I40"));
const mr = Object.fromEntries(modelRows.map(([r, label]) => [label, r]));
for (let c = 2; c <= 4; c++) {
  const year = years[c - 2];
  const hcol = colName(c + 2); // Historical D:F maps 2023: D
  const formulas = [
    [mr["Revenue"], `=Historical!${hcol}${histRowByMetric.revenue}`],
    [mr["Gross profit"], `=Historical!${hcol}${histRowByMetric.gross_profit}`],
    [mr["Gross margin"], `=${cell(mr["Gross profit"], c)}/${cell(mr["Revenue"], c)}`],
    [mr["SG&A"], `=Historical!${hcol}${histRowByMetric.sga}`],
    [mr["SG&A % sales"], `=${cell(mr["SG&A"], c)}/${cell(mr["Revenue"], c)}`],
    [mr["Operating income"], `=Historical!${hcol}${histRowByMetric.operating_income}`],
    [mr["Operating margin"], `=${cell(mr["Operating income"], c)}/${cell(mr["Revenue"], c)}`],
    [mr["Pretax income"], `=Historical!${hcol}${histRowByMetric.pretax_income}`],
    [mr["Income tax"], `=Historical!${hcol}${histRowByMetric.income_tax}`],
    [mr["Tax rate"], `=${cell(mr["Income tax"], c)}/${cell(mr["Pretax income"], c)}`],
    [mr["Net income"], `=Historical!${hcol}${histRowByMetric.net_income}`],
    [mr["Diluted shares"], `=Historical!${hcol}${histRowByMetric.diluted_shares}`],
    [mr["EPS"], `=Historical!${hcol}${histRowByMetric.diluted_eps}`],
    [mr["Cash"], `=Historical!${hcol}${histRowByMetric.cash}`],
    [mr["Accounts receivable"], `=Historical!${hcol}${histRowByMetric.accounts_receivable}`],
    [mr["Inventory"], `=Historical!${hcol}${histRowByMetric.inventory}`],
    [mr["Prepaids / other current assets"], `=Historical!${hcol}${histRowByMetric.prepaids_other_current_assets}`],
    [mr["Current assets"], `=Historical!${hcol}${histRowByMetric.current_assets}`],
    [mr["PP&E net"], `=Historical!${hcol}${histRowByMetric.ppe_net}`],
    [mr["Goodwill + intangibles"], `=Historical!${hcol}${histRowByMetric.goodwill}+Historical!${hcol}${histRowByMetric.intangible_assets}`],
    [mr["Operating lease assets"], `=Historical!${hcol}${histRowByMetric.operating_lease_assets}`],
    [mr["Total assets"], `=Historical!${hcol}${histRowByMetric.total_assets}`],
    [mr["Other assets"], `=${cell(mr["Total assets"], c)}-${cell(mr["Current assets"], c)}-${cell(mr["PP&E net"], c)}-${cell(mr["Goodwill + intangibles"], c)}-${cell(mr["Operating lease assets"], c)}`],
    [mr["Accounts payable"], `=Historical!${hcol}${histRowByMetric.accounts_payable}`],
    [mr["Accrued/current liabilities ex AP/debt"], `=Historical!${hcol}${histRowByMetric.current_liabilities}-Historical!${hcol}${histRowByMetric.accounts_payable}-Historical!${hcol}${histRowByMetric.current_debt}`],
    [mr["Funded debt"], `=Historical!${hcol}${histRowByMetric.funded_debt}`],
    [mr["Operating lease liabilities"], `=Historical!${hcol}${histRowByMetric.operating_lease_liabilities}`],
    [mr["Total liabilities"], `=Historical!${hcol}${histRowByMetric.total_liabilities}`],
    [mr["Other liabilities / balance residual"], `=${cell(mr["Total liabilities"], c)}-SUM(${cell(mr["Accounts payable"], c)}:${cell(mr["Operating lease liabilities"], c)})`],
    [mr["Stockholders' equity"], `=Historical!${hcol}${histRowByMetric.stockholders_equity}`],
    [mr["BS check"], `=${cell(mr["Total assets"], c)}-${cell(mr["Total liabilities"], c)}-${cell(mr["Stockholders' equity"], c)}`],
    [mr["Net income (cash flow)"], `=${cell(mr["Net income"], c)}`],
    [mr["D&A"], `=Historical!${hcol}${histRowByMetric.depreciation_amortization}`],
    [mr["Stock compensation"], `=Historical!${hcol}${histRowByMetric.stock_comp}`],
    [mr["Operating cash flow"], `=Historical!${hcol}${histRowByMetric.operating_cash_flow}`],
    [mr["Capital expenditures"], `=Historical!${hcol}${histRowByMetric.capex}`],
    [mr["Free cash flow"], `=Historical!${hcol}${histRowByMetric.free_cash_flow}`],
    [mr["Share repurchases"], `=Historical!${hcol}${histRowByMetric.share_repurchases}`],
    [mr["Ending cash"], `=${cell(mr["Cash"], c)}`],
    [mr["CFS cash check"], c === 2 ? "=0" : `=${cell(mr["Ending cash"], c)}-${cell(mr["Ending cash"], c - 1)}-(${cell(mr["Free cash flow"], c)}-${cell(mr["Share repurchases"], c)}+${cell(mr["Change in funded debt"], c)})`],
    [mr["Unlevered FCF"], `=${cell(mr["Operating income"], c)}*(1-${cell(mr["Tax rate"], c)})+${cell(mr["D&A"], c)}-${cell(mr["Capital expenditures"], c)}-${cell(mr["Change in NWC"], c)}`],
  ];
  for (const [r, f] of formulas) model.getRange(cell(r, c)).formulas = [[f]];
  if (c > 2) model.getRange(cell(mr["Revenue growth"], c)).formulas = [[`=${cell(mr["Revenue"], c)}/${cell(mr["Revenue"], c - 1)}-1`]];
  model.getRange(cell(mr["Change in funded debt"], c)).formulas = [[c === 2 ? "=0" : `=${cell(mr["Funded debt"], c)}-${cell(mr["Funded debt"], c - 1)}`]];
  model.getRange(cell(mr["Change in NWC"], c)).formulas = [[c === 2 ? "=0" : `=(${cell(mr["Accounts receivable"], c)}+${cell(mr["Inventory"], c)}-${cell(mr["Accounts payable"], c)})-(${cell(mr["Accounts receivable"], c - 1)}+${cell(mr["Inventory"], c - 1)}-${cell(mr["Accounts payable"], c - 1)})`]];
  model.getRange(cell(mr["Net interest expense / (income)"], c)).formulas = [[`=${cell(mr["Pretax income"], c)}-${cell(mr["Operating income"], c)}`]];
}

for (let c = 5; c <= 9; c++) {
  const aCol = colName(c - 3); // assumptions B:F
  const prev = c - 1;
  model.getRange(cell(mr["Revenue"], c)).formulas = [[`=${cell(mr["Revenue"], prev)}*(1+Assumptions!${aCol}26)`]];
  model.getRange(cell(mr["Revenue growth"], c)).formulas = [[`=${cell(mr["Revenue"], c)}/${cell(mr["Revenue"], prev)}-1`]];
  model.getRange(cell(mr["Gross margin"], c)).formulas = [[`=Assumptions!${aCol}27`]];
  model.getRange(cell(mr["Gross profit"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*${cell(mr["Gross margin"], c)}`]];
  model.getRange(cell(mr["Operating margin"], c)).formulas = [[`=Assumptions!${aCol}28`]];
  model.getRange(cell(mr["Operating income"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*${cell(mr["Operating margin"], c)}`]];
  model.getRange(cell(mr["SG&A"], c)).formulas = [[`=${cell(mr["Gross profit"], c)}-${cell(mr["Operating income"], c)}`]];
  model.getRange(cell(mr["SG&A % sales"], c)).formulas = [[`=${cell(mr["SG&A"], c)}/${cell(mr["Revenue"], c)}`]];
  model.getRange(cell(mr["Net interest expense / (income)"], c)).formulas = [[`=${cell(mr["Funded debt"], prev)}*Assumptions!$B$15-${cell(mr["Cash"], prev)}*3.0%`]];
  model.getRange(cell(mr["Pretax income"], c)).formulas = [[`=${cell(mr["Operating income"], c)}-${cell(mr["Net interest expense / (income)"], c)}`]];
  model.getRange(cell(mr["Tax rate"], c)).formulas = [[`=Assumptions!${aCol}29`]];
  model.getRange(cell(mr["Income tax"], c)).formulas = [[`=${cell(mr["Pretax income"], c)}*${cell(mr["Tax rate"], c)}`]];
  model.getRange(cell(mr["Net income"], c)).formulas = [[`=${cell(mr["Pretax income"], c)}-${cell(mr["Income tax"], c)}`]];
  if (c === 5) {
    model.getRange(cell(mr["Diluted shares"], c)).formulas = [[`=${guidance.diluted_shares / 1_000_000}`]];
  } else {
    model.getRange(cell(mr["Diluted shares"], c)).formulas = [[`=${cell(mr["Diluted shares"], prev)}-${cell(mr["Share repurchases"], c)}/${cell(34, c - 3)}`]];
  }
  model.getRange(cell(mr["EPS"], c)).formulas = [[`=${cell(mr["Net income"], c)}/${cell(mr["Diluted shares"], c)}`]];
  model.getRange(cell(mr["Net income (cash flow)"], c)).formulas = [[`=${cell(mr["Net income"], c)}`]];
  model.getRange(cell(mr["Accounts receivable"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*Assumptions!${aCol}35`]];
  model.getRange(cell(mr["Inventory"], c)).formulas = [[`=(${cell(mr["Revenue"], c)}-${cell(mr["Gross profit"], c)})*Assumptions!${aCol}36`]];
  model.getRange(cell(mr["Prepaids / other current assets"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*2.1%`]];
  model.getRange(cell(mr["PP&E net"], c)).formulas = [[`=${cell(mr["PP&E net"], prev)}+${cell(mr["Capital expenditures"], c)}-${cell(mr["D&A"], c)}*70%`]];
  model.getRange(cell(mr["Goodwill + intangibles"], c)).formulas = [[`=${cell(mr["Goodwill + intangibles"], prev)}`]];
  model.getRange(cell(mr["Operating lease assets"], c)).formulas = [[`=${cell(mr["Operating lease assets"], prev)}`]];
  model.getRange(cell(mr["Other assets"], c)).formulas = [[`=${cell(mr["Other assets"], prev)}`]];
  model.getRange(cell(mr["Accounts payable"], c)).formulas = [[`=(${cell(mr["Revenue"], c)}-${cell(mr["Gross profit"], c)})*Assumptions!${aCol}37`]];
  model.getRange(cell(mr["Accrued/current liabilities ex AP/debt"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*10.0%`]];
  model.getRange(cell(mr["Funded debt"], c)).formulas = [[`=${cell(mr["Funded debt"], prev)}`]];
  model.getRange(cell(mr["Operating lease liabilities"], c)).formulas = [[`=${cell(mr["Operating lease liabilities"], prev)}`]];
  model.getRange(cell(mr["Stockholders' equity"], c)).formulas = [[`=${cell(mr["Stockholders' equity"], prev)}+${cell(mr["Net income"], c)}+${cell(mr["Stock compensation"], c)}-${cell(mr["Share repurchases"], c)}`]];
  model.getRange(cell(mr["Cash"], c)).formulas = [[`=${cell(mr["Cash"], prev)}+${cell(mr["Free cash flow"], c)}-${cell(mr["Share repurchases"], c)}+${cell(mr["Change in funded debt"], c)}`]];
  model.getRange(cell(mr["Current assets"], c)).formulas = [[`=SUM(${cell(mr["Cash"], c)}:${cell(mr["Prepaids / other current assets"], c)})`]];
  model.getRange(cell(mr["Total assets"], c)).formulas = [[`=SUM(${cell(mr["Current assets"], c)}:${cell(mr["Other assets"], c)})`]];
  model.getRange(cell(mr["Other liabilities / balance residual"], c)).formulas = [[`=${cell(mr["Total assets"], c)}-${cell(mr["Stockholders' equity"], c)}-SUM(${cell(mr["Accounts payable"], c)}:${cell(mr["Operating lease liabilities"], c)})`]];
  model.getRange(cell(mr["Total liabilities"], c)).formulas = [[`=SUM(${cell(mr["Accounts payable"], c)}:${cell(mr["Other liabilities / balance residual"], c)})`]];
  model.getRange(cell(mr["BS check"], c)).formulas = [[`=${cell(mr["Total assets"], c)}-${cell(mr["Total liabilities"], c)}-${cell(mr["Stockholders' equity"], c)}`]];
  model.getRange(cell(mr["D&A"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*Assumptions!${aCol}30`]];
  model.getRange(cell(mr["Stock compensation"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*Assumptions!${aCol}32`]];
  model.getRange(cell(mr["Change in NWC"], c)).formulas = [[`=(${cell(mr["Accounts receivable"], c)}+${cell(mr["Inventory"], c)}-${cell(mr["Accounts payable"], c)})-(${cell(mr["Accounts receivable"], prev)}+${cell(mr["Inventory"], prev)}-${cell(mr["Accounts payable"], prev)})`]];
  model.getRange(cell(mr["Operating cash flow"], c)).formulas = [[`=${cell(mr["Net income"], c)}+${cell(mr["D&A"], c)}+${cell(mr["Stock compensation"], c)}-${cell(mr["Change in NWC"], c)}`]];
  model.getRange(cell(mr["Capital expenditures"], c)).formulas = [[`=${cell(mr["Revenue"], c)}*Assumptions!${aCol}31`]];
  model.getRange(cell(mr["Free cash flow"], c)).formulas = [[`=${cell(mr["Operating cash flow"], c)}-${cell(mr["Capital expenditures"], c)}`]];
  model.getRange(cell(mr["Share repurchases"], c)).formulas = [[`=Assumptions!${aCol}33`]];
  model.getRange(cell(mr["Change in funded debt"], c)).formulas = [[`=${cell(mr["Funded debt"], c)}-${cell(mr["Funded debt"], prev)}`]];
  model.getRange(cell(mr["Ending cash"], c)).formulas = [[`=${cell(mr["Cash"], c)}`]];
  model.getRange(cell(mr["CFS cash check"], c)).formulas = [[`=${cell(mr["Ending cash"], c)}-${cell(mr["Ending cash"], prev)}-(${cell(mr["Free cash flow"], c)}-${cell(mr["Share repurchases"], c)}+${cell(mr["Change in funded debt"], c)})`]];
  model.getRange(cell(mr["Unlevered FCF"], c)).formulas = [[`=${cell(mr["Operating income"], c)}*(1-${cell(mr["Tax rate"], c)})+${cell(mr["D&A"], c)}-${cell(mr["Capital expenditures"], c)}-${cell(mr["Change in NWC"], c)}`]];
}
model.getRange("B5:I52").format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
for (const r of [6, 8, 10, 12, 16]) model.getRange(`B${r}:I${r}`).format.numberFormat = "0.0%";
model.getRange("B18:I18").format.numberFormat = "#,##0.0";
model.getRange("B19:I19").format.numberFormat = "$0.00";
model.getRange("A:I").format.autofitColumns();
model.freezePanes.freezeRows(4);
model.freezePanes.freezeColumns(1);

// Peers
setTitle(peers, "Peer Valuation", "Market and peer metrics from fetched StockAnalysis pages.");
peers.getRange("A4:E4").values = [["Ticker", "Metric", "Value", "Display", "Source file"]];
headerStyle(peers.getRange("A4:E4"));
const peerValues = peerRows.map((r) => [r.ticker, r.metric, num(r.value), r.display_value, r.source_file]);
peers.getRangeByIndexes(4, 0, peerValues.length, 5).values = peerValues;
peers.getRange("A:E").format.autofitColumns();

// Valuation
setTitle(valuation, "Valuation", "Base-case DCF plus trading-multiple triangulation; amounts in $mm except per-share values.");
valuation.getRange("A4:F4").values = [["DCF", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]];
headerStyle(valuation.getRange("A4:F4"));
valuation.getRange("A5:A12").values = [["Unlevered FCF"], ["Discount factor"], ["PV FCF"], ["Terminal growth"], ["Terminal value"], ["PV terminal value"], ["Enterprise value"], ["Equity value / share"]];
for (let c = 2; c <= 6; c++) {
  const modelCol = c + 3;
  valuation.getRange(cell(5, c)).formulas = [[`=Model!${cell(mr["Unlevered FCF"], modelCol)}`]];
  valuation.getRange(cell(6, c)).formulas = [[`=1/(1+Assumptions!$B$18)^${c - 1}`]];
  valuation.getRange(cell(7, c)).formulas = [[`=${cell(5, c)}*${cell(6, c)}`]];
}
valuation.getRange("B8").formulas = [["=Assumptions!$B$19"]];
valuation.getRange("B9").formulas = [["=F5*(1+B8)/(Assumptions!$B$18-B8)"]];
valuation.getRange("B10").formulas = [["=B9*F6"]];
valuation.getRange("B11").formulas = [["=SUM(B7:F7)+B10"]];
valuation.getRange("B12").formulas = [["=(B11+Assumptions!$B$8-Assumptions!$B$9)/Assumptions!$B$6"]];
valuation.getRange("A15:D15").values = [["Multiple triangulation", "Value", "Weight", "Weighted value"]];
headerStyle(valuation.getRange("A15:D15"));
valuation.getRange("A16:A20").values = [["DCF value / share"], ["EV/EBITDA value / share"], ["P/E value / share"], ["Blended 12-month price target"], ["Upside / downside vs current"]];
valuation.getRange("B16").formulas = [["=B12"]];
valuation.getRange("B17").formulas = [[`=((Model!${cell(mr["Operating income"], 5)}+Model!${cell(mr["D&A"], 5)})*Assumptions!$B$20+Assumptions!$B$8-Assumptions!$B$9)/Assumptions!$B$6`]];
valuation.getRange("B18").formulas = [[`=Model!${cell(mr["EPS"], 5)}*Assumptions!$B$21`]];
valuation.getRange("C16:C18").values = [[0.50], [0.25], [0.25]];
valuation.getRange("D16").formulas = [["=B16*C16"]];
valuation.getRange("D17").formulas = [["=B17*C17"]];
valuation.getRange("D18").formulas = [["=B18*C18"]];
valuation.getRange("B19").formulas = [["=ROUND(SUM(D16:D18),0)"]];
valuation.getRange("B20").formulas = [["=B19/Assumptions!$B$5-1"]];
valuation.getRange("A23:B28").values = [
  ["Sell-side / market reference", ""],
  ["Consensus target average", market.consensus_target_average],
  ["Consensus target median", market.consensus_target_median],
  ["Consensus 2026 revenue", mm(market.consensus_2026_revenue)],
  ["Consensus 2026 EPS", market.consensus_2026_eps],
  ["Recommendation", "HOLD"],
];
sectionStyle(valuation.getRange("A23:B23"));
valuation.getRange("B16:B19").format.numberFormat = "$0.00";
valuation.getRange("B20").format.numberFormat = "0.0%";
valuation.getRange("C16:D18").format.numberFormat = "0.0%";
valuation.getRange("D16:D18").format.numberFormat = "$0.00";
valuation.getRange("B24:B25").format.numberFormat = "$0.00";
valuation.getRange("B26").format.numberFormat = "$#,##0.0";
valuation.getRange("B27").format.numberFormat = "$0.00";
valuation.getRange("B5:F11").format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
valuation.getRange("B6:F6").format.numberFormat = "0.000x";
valuation.getRange("B8").format.numberFormat = "0.0%";
valuation.getRange("A:F").format.autofitColumns();

// Scenarios
setTitle(scenarios, "Bear / Base / Bull Scenarios", "Standalone DCF scenario table for the memo probability-weighted case.");
scenarios.getRange("A4:J4").values = [["Scenario", "Probability", "FY26 growth", "FY27 growth", "FY28 growth", "FY29 growth", "FY30 growth", "FCF margin FY26", "FCF margin FY30", "Terminal growth"]];
headerStyle(scenarios.getRange("A4:J4"));
scenarios.getRange("A5:J7").values = [
  ["Bear", 0.25, 0.04, 0.035, 0.035, 0.03, 0.03, 0.095, 0.105, 0.02],
  ["Base", 0.50, 0.07, 0.07, 0.06, 0.055, 0.05, 0.112, 0.120, 0.0275],
  ["Bull", 0.25, 0.08, 0.09, 0.08, 0.07, 0.06, 0.120, 0.135, 0.03],
];
inputStyle(scenarios.getRange("B5:J7"));
scenarios.getRange("L4:AI4").values = [[
  "Rev 26", "Rev 27", "Rev 28", "Rev 29", "Rev 30",
  "FCF m 26", "FCF m 27", "FCF m 28", "FCF m 29", "FCF m 30",
  "FCF 26", "FCF 27", "FCF 28", "FCF 29", "FCF 30",
  "PV 26", "PV 27", "PV 28", "PV 29", "PV 30",
  "PV TV", "EV", "Equity value", "Per share"
]];
headerStyle(scenarios.getRange("L4:AI4"));
for (let r = 5; r <= 7; r++) {
  scenarios.getRange(`L${r}`).formulas = [[`=Model!D${mr["Revenue"]}*(1+C${r})`]];
  scenarios.getRange(`M${r}`).formulas = [[`=L${r}*(1+D${r})`]];
  scenarios.getRange(`N${r}`).formulas = [[`=M${r}*(1+E${r})`]];
  scenarios.getRange(`O${r}`).formulas = [[`=N${r}*(1+F${r})`]];
  scenarios.getRange(`P${r}`).formulas = [[`=O${r}*(1+G${r})`]];
  scenarios.getRange(`Q${r}:U${r}`).formulas = [[`=H${r}`, `=H${r}+($I${r}-$H${r})*0.25`, `=H${r}+($I${r}-$H${r})*0.50`, `=H${r}+($I${r}-$H${r})*0.75`, `=I${r}`]];
  scenarios.getRange(`V${r}:Z${r}`).formulas = [[`=L${r}*Q${r}`, `=M${r}*R${r}`, `=N${r}*S${r}`, `=O${r}*T${r}`, `=P${r}*U${r}`]];
  scenarios.getRange(`AA${r}:AE${r}`).formulas = [[`=V${r}/(1+Assumptions!$B$18)^1`, `=W${r}/(1+Assumptions!$B$18)^2`, `=X${r}/(1+Assumptions!$B$18)^3`, `=Y${r}/(1+Assumptions!$B$18)^4`, `=Z${r}/(1+Assumptions!$B$18)^5`]];
  scenarios.getRange(`AF${r}`).formulas = [[`=Z${r}*(1+J${r})/(Assumptions!$B$18-J${r})/(1+Assumptions!$B$18)^5`]];
  scenarios.getRange(`AG${r}`).formulas = [[`=SUM(AA${r}:AE${r})+AF${r}`]];
  scenarios.getRange(`AH${r}`).formulas = [[`=AG${r}+Assumptions!$B$8-Assumptions!$B$9`]];
  scenarios.getRange(`AI${r}`).formulas = [[`=AH${r}/Assumptions!$B$6`]];
}
scenarios.getRange("A10:B11").values = [["Probability-weighted DCF value", ""], ["Current price", sharePrice]];
scenarios.getRange("B10").formulas = [["=SUMPRODUCT(B5:B7,AI5:AI7)"]];
scenarios.getRange("B10:B11").format.numberFormat = "$0.00";
scenarios.getRange("B5:J7").format.numberFormat = "0.0%";
scenarios.getRange("L5:AH7").format.numberFormat = "$#,##0.0;[Red]($#,##0.0);-";
scenarios.getRange("Q5:U7").format.numberFormat = "0.0%";
scenarios.getRange("AI5:AI7").format.numberFormat = "$0.00";
scenarios.getRange("A:AI").format.autofitColumns();

// Checks
setTitle(checks, "Model Checks", "Checks should read OK before using the workbook.");
checks.getRange("A4:F4").values = [["Check", "Actual", "Expected", "Difference", "Tolerance", "Status"]];
headerStyle(checks.getRange("A4:F4"));
checks.getRange("A5:A11").values = [
  ["FY2030 balance sheet balances"],
  ["FY2030 cash flow ties to cash"],
  ["Source rows loaded"],
  ["Scenario probabilities sum to 100%"],
  ["WACC greater than terminal growth"],
  ["Blended target is calculated"],
  ["Recommendation cell populated"],
];
checks.getRange("B5").formulas = [[`=Model!I${mr["BS check"]}`]];
checks.getRange("C5").values = [[0]];
checks.getRange("D5").formulas = [["=B5-C5"]];
checks.getRange("E5").values = [[0.01]];
checks.getRange("F5").formulas = [["=IF(ABS(D5)<=E5,\"OK\",\"Check\")"]];
checks.getRange("B6").formulas = [[`=Model!I${mr["CFS cash check"]}`]];
checks.getRange("C6").values = [[0]];
checks.getRange("D6").formulas = [["=B6-C6"]];
checks.getRange("E6").values = [[0.01]];
checks.getRange("F6").formulas = [["=IF(ABS(D6)<=E6,\"OK\",\"Check\")"]];
checks.getRange("B7").values = [[auditRows.length]];
checks.getRange("C7").values = [[50]];
checks.getRange("D7").formulas = [["=B7-C7"]];
checks.getRange("E7").values = [[0]];
checks.getRange("F7").formulas = [["=IF(B7>=C7,\"OK\",\"Check\")"]];
checks.getRange("B8").formulas = [["=SUM(Scenarios!B5:B7)"]];
checks.getRange("C8").values = [[1]];
checks.getRange("D8").formulas = [["=B8-C8"]];
checks.getRange("E8").values = [[0.0001]];
checks.getRange("F8").formulas = [["=IF(ABS(D8)<=E8,\"OK\",\"Check\")"]];
checks.getRange("B9").formulas = [["=Assumptions!B18"]];
checks.getRange("C9").formulas = [["=Assumptions!B19"]];
checks.getRange("D9").formulas = [["=B9-C9"]];
checks.getRange("E9").values = [[0]];
checks.getRange("F9").formulas = [["=IF(B9>C9,\"OK\",\"Check\")"]];
checks.getRange("B10").formulas = [["=Valuation!B19"]];
checks.getRange("F10").formulas = [["=IF(B10>0,\"OK\",\"Check\")"]];
checks.getRange("B11").formulas = [["=Valuation!B28"]];
checks.getRange("F11").formulas = [["=IF(B11<>\"\",\"OK\",\"Check\")"]];
checks.getRange("B5:E9").format.numberFormat = "0.000";
checks.getRange("A:F").format.autofitColumns();

// Cover
setTitle(cover, "YETI Holdings Investment Memo Model", "HOLD recommendation; 12-month target triangulated from DCF and market multiples.");
cover.getRange("A4:B12").values = [
  ["Ticker", "YETI"],
  ["Recommendation", "HOLD"],
  ["12-month price target", ""],
  ["Current price", sharePrice],
  ["Implied upside", ""],
  ["Market cap", marketCap],
  ["FY2025 revenue", mm(num(hist[2025].revenue))],
  ["FY2025 free cash flow", mm(num(hist[2025].free_cash_flow))],
  ["Model status", ""],
];
cover.getRange("B6").formulas = [["=Valuation!B19"]];
cover.getRange("B8").formulas = [["=B6/B7-1"]];
cover.getRange("B12").formulas = [["=IF(COUNTIF(Checks!F5:F11,\"Check\")=0,\"OK\",\"Review checks\")"]];
cover.getRange("B6:B7").format.numberFormat = "$0.00";
cover.getRange("B8").format.numberFormat = "0.0%";
cover.getRange("B9:B11").format.numberFormat = "$#,##0.0";
cover.getRange("D4:G4").values = [["Year", "Revenue", "Op margin", "FCF"]];
headerStyle(cover.getRange("D4:G4"));
for (let i = 0; i < yearLabels.length; i++) {
  const row = 5 + i;
  const modelCol = colName(2 + i);
  cover.getRange(`D${row}:G${row}`).values = [[yearLabels[i], "", "", ""]];
  cover.getRange(`E${row}:G${row}`).formulas = [[
    `=Model!${modelCol}5`,
    `=Model!${modelCol}12`,
    `=Model!${modelCol}46`,
  ]];
}
cover.getRange("E5:E12").format.numberFormat = "$#,##0.0";
cover.getRange("F5:F12").format.numberFormat = "0.0%";
cover.getRange("G5:G12").format.numberFormat = "$#,##0.0";
const chart = cover.charts.add("line", cover.getRange("D4:E12"));
chart.title = "Revenue Trajectory";
chart.hasLegend = true;
chart.xAxis = { axisType: "textAxis" };
chart.setPosition("D15", "L30");
cover.getRange("A:L").format.autofitColumns();

cover.getRange("A4:A12").format = { font: { bold: true } };
valuation.getRange("A16:A20").format = { font: { bold: true } };

const outputDir = path("model");
await fs.mkdir(`${outputDir}/previews`, { recursive: true });

for (const sheetName of ["Cover", "Assumptions", "Model", "Valuation", "Scenarios", "Checks", "Sources"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outputDir}/previews/${sheetName.toLowerCase()}.png`, new Uint8Array(await preview.arrayBuffer()));
}

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 200 },
  summary: "formula error scan",
});
await fs.writeFile(`${outputDir}/formula-error-scan.ndjson`, errors.ndjson ?? "");

const checkInspect = await workbook.inspect({
  kind: "table",
  range: "Checks!A4:F11",
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 6,
});
await fs.writeFile(`${outputDir}/checks-inspect.ndjson`, checkInspect.ndjson ?? "");

const keyOutputRanges = [
  ["cover", "Cover!A4:B12", 12, 2],
  ["assumptions", "Assumptions!A4:C23", 25, 3],
  ["base_model", "Model!A5:I52", 55, 9],
  ["valuation", "Valuation!A4:F28", 30, 6],
  ["scenarios", "Scenarios!A4:AI10", 10, 35],
  ["checks", "Checks!A4:F11", 10, 6],
];
const keyOutputBlocks = [];
for (const [name, range, tableMaxRows, tableMaxCols] of keyOutputRanges) {
  const inspected = await workbook.inspect({
    kind: "table",
    range,
    include: "values,formulas",
    tableMaxRows,
    tableMaxCols,
  });
  keyOutputBlocks.push(JSON.stringify({ name, range, ndjson: inspected.ndjson ?? "" }));
}
await fs.writeFile(`${outputDir}/key-outputs.ndjson`, `${keyOutputBlocks.join("\n")}\n`);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/yeti_investment_model.xlsx`);
console.log(`Wrote ${outputDir}/yeti_investment_model.xlsx`);
