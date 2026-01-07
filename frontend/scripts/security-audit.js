/* eslint-disable no-console */
const { spawnSync } = require("child_process");

// CRA 5 pins webpack-dev-server < 5.2.1 through react-scripts.
// These advisories are dev-server-only and require a tooling migration to eliminate.
const ALLOWED_ADVISORY_IDS = new Set([1108429, 1108430]);

function run() {
  const res = spawnSync("yarn", ["audit", "--json"], {
    cwd: __dirname + "/..",
    encoding: "utf8",
  });

  const out = (res.stdout || "").trim();
  const lines = out ? out.split("\n") : [];

  const advisories = [];
  for (const line of lines) {
    try {
      const evt = JSON.parse(line);
      if (evt.type === "auditAdvisory") {
        const adv = evt.data?.advisory;
        const id = adv?.id;
        advisories.push({
          id,
          module_name: adv?.module_name,
          severity: adv?.severity,
          title: adv?.title,
          url: adv?.url,
        });
      }
    } catch {
      // ignore non-JSON lines
    }
  }

  const disallowed = advisories.filter((a) => !ALLOWED_ADVISORY_IDS.has(a.id));
  if (disallowed.length === 0) {
    if (advisories.length) {
      console.log(
        `Allowed known dev-only advisories: ${advisories
          .map((a) => `${a.id}:${a.module_name}:${a.severity}`)
          .join(", ")}`
      );
    }
    console.log("✅ Security audit passed (with allowlist).");
    return 0;
  }

  console.error("❌ Security audit failed. Disallowed advisories found:");
  for (const a of disallowed) {
    console.error(`- ${a.id} ${a.severity} ${a.module_name}: ${a.title} (${a.url})`);
  }
  return 1;
}

process.exit(run());

