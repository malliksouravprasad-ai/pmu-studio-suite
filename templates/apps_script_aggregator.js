/**
 * PMU Tools — Nightly Aggregator
 * Google Apps Script Web App
 *
 * DEPLOYMENT:
 *   1. Go to script.google.com → New Project → paste this file
 *   2. Project Settings → Script Properties → Add property:
 *        PMU_SECRET = <your-secret-token>
 *   3. Deploy → New deployment → Web App
 *        Execute as: Me
 *        Who has access: Anyone
 *   4. Copy the Web App URL into .streamlit/secrets.toml:
 *        [apps_script]
 *        web_app_url   = "https://script.google.com/macros/s/.../exec"
 *        shared_secret = "<your-secret-token>"
 *
 * NIGHTLY SCHEDULE:
 *   Run setupNightlyTrigger() once from the Apps Script editor.
 *   Then configure runNightlyAggregation() with your sheet URLs.
 */

// ── Entry points ──────────────────────────────────────────────────────────────

function doPost(e) {
  try {
    var body   = JSON.parse(e.postData.contents);
    var secret = PropertiesService.getScriptProperties().getProperty("PMU_SECRET") || "";

    if (body.secret !== secret) {
      return _json({ status: "error", error: "Unauthorized — check shared_secret in secrets.toml" });
    }

    switch (body.action) {
      case "aggregate": return _json(_aggregate(body));
      case "ping":      return _json({ status: "ok", message: "PMU Aggregator is running." });
      default:          return _json({ status: "error", error: "Unknown action: " + body.action });
    }
  } catch (err) {
    return _json({ status: "error", error: err.toString() });
  }
}

function doGet(e) {
  return _json({ status: "ok", message: "PMU Aggregator Web App is deployed and ready." });
}

// ── Aggregation engine ────────────────────────────────────────────────────────

function _aggregate(data) {
  var sourceUrl  = data.source_url  || "";
  var targetUrl  = data.target_url  || "";
  var groupCols  = data.group_cols  || [];
  var metricCols = data.metric_cols || [];
  var aggFunc    = (data.agg_func   || "SUM").toUpperCase();

  if (!sourceUrl || !targetUrl) {
    return { status: "error", error: "source_url and target_url are required." };
  }

  var srcSheet = SpreadsheetApp.openByUrl(sourceUrl).getActiveSheet();
  var srcData  = srcSheet.getDataRange().getValues();

  if (srcData.length < 2) {
    return { status: "error", error: "Source sheet has no data rows." };
  }

  var headers    = srcData[0];
  var rows       = srcData.slice(1);
  var groupIdxs  = groupCols.map(function(c)  { return headers.indexOf(c); });
  var metricIdxs = metricCols.map(function(c) { return headers.indexOf(c); });

  var missing = groupCols.filter(function(c, i) { return groupIdxs[i]  === -1; })
              .concat(metricCols.filter(function(c, i) { return metricIdxs[i] === -1; }));
  if (missing.length) {
    return { status: "error", error: "Columns not found in source sheet: " + missing.join(", ") };
  }

  // Build aggregation map
  var aggMap = {};
  rows.forEach(function(row) {
    var key = groupIdxs.map(function(i) { return String(row[i]); }).join("");
    if (!aggMap[key]) {
      aggMap[key] = {
        groupVals: groupIdxs.map(function(i) { return row[i]; }),
        metrics:   {}
      };
      metricCols.forEach(function(col) {
        aggMap[key].metrics[col] = { sum: 0, count: 0, min: Infinity, max: -Infinity };
      });
    }
    metricIdxs.forEach(function(mi, j) {
      var val = parseFloat(row[mi]);
      if (!isNaN(val)) {
        var m = aggMap[key].metrics[metricCols[j]];
        m.sum   += val;
        m.count += 1;
        m.min    = Math.min(m.min, val);
        m.max    = Math.max(m.max, val);
      }
    });
  });

  // Build output
  var outHeaders = groupCols.concat(metricCols.map(function(c) { return c + "_" + aggFunc; }));
  var outRows = Object.keys(aggMap).sort().map(function(key) {
    var entry = aggMap[key];
    var row   = entry.groupVals.slice();
    metricCols.forEach(function(col) {
      var m   = entry.metrics[col];
      var val;
      if      (aggFunc === "SUM")     val = m.sum;
      else if (aggFunc === "AVERAGE") val = m.count ? Math.round((m.sum / m.count) * 100) / 100 : 0;
      else if (aggFunc === "COUNT")   val = m.count;
      else if (aggFunc === "MIN")     val = isFinite(m.min) ? m.min : 0;
      else if (aggFunc === "MAX")     val = isFinite(m.max) ? m.max : 0;
      else                            val = m.sum;
      row.push(Math.round(val * 100) / 100);
    });
    return row;
  });

  // Write to target sheet
  var tgtSheet = SpreadsheetApp.openByUrl(targetUrl).getActiveSheet();
  tgtSheet.clearContents();
  tgtSheet.getRange(1, 1, 1, outHeaders.length).setValues([outHeaders]);
  if (outRows.length > 0) {
    tgtSheet.getRange(2, 1, outRows.length, outHeaders.length).setValues(outRows);
  }

  var ts = new Date().toISOString();
  Logger.log("PMU Aggregation complete — " + outRows.length + " rows written at " + ts);
  return { status: "ok", rows_written: outRows.length, timestamp: ts };
}

// ── Nightly schedule setup ────────────────────────────────────────────────────

/**
 * Run this function ONCE from the Apps Script editor to set up nightly execution.
 * Deletes any existing PMU trigger before creating a new one to prevent duplicates.
 */
function setupNightlyTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === "runNightlyAggregation") {
      ScriptApp.deleteTrigger(t);
    }
  });
  ScriptApp.newTrigger("runNightlyAggregation")
    .timeBased()
    .atHour(1)
    .everyDays(1)
    .create();
  Logger.log("Nightly aggregation trigger created — runs at 1:00 AM daily.");
}

/**
 * Configure your default aggregation here, then run setupNightlyTrigger().
 */
function runNightlyAggregation() {
  var config = {
    source_url:  "PASTE_YOUR_RAW_DATA_SHEET_URL_HERE",
    target_url:  "PASTE_YOUR_AGGREGATED_OUTPUT_SHEET_URL_HERE",
    group_cols:  ["District", "Block"],
    metric_cols: ["Enrolment", "Attendance", "Score"],
    agg_func:    "SUM",
  };
  var result = _aggregate(config);
  Logger.log(JSON.stringify(result));
}

// ── Helper ────────────────────────────────────────────────────────────────────

function _json(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
