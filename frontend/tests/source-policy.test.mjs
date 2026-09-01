import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { filesBelow, findHandwrittenDtoViolations } from "./policies.mjs";

test("frontend DTO происходят только из generated OpenAPI contract", async () => {
  const client = await readFile("src/api/client.ts", "utf8");
  assert.match(client, /from "\.\/generated\/schema"/);
  assert.deepEqual(await findHandwrittenDtoViolations("src"), []);
});

test("DTO gate scans nested non-generated files and rejects interface/type/schema", async (t) => {
  const fixture = await mkdtemp(join(tmpdir(), "frontend-dto-policy-"));
  t.after(() => rm(fixture, { recursive: true, force: true }));
  await mkdir(join(fixture, "features", "nested"), { recursive: true });
  await mkdir(join(fixture, "api", "generated"), { recursive: true });
  await writeFile(
    join(fixture, "features", "nested", "contracts.ts"),
    [
      "interface HealthResponse { status: string }",
      "type ProblemDetails = { code: string }",
      "const requestSchema = z.object({ value: z.string() });",
    ].join("\n"),
  );
  await writeFile(
    join(fixture, "api", "generated", "schema.ts"),
    "interface GeneratedResponse { status: string }",
  );

  const violations = await findHandwrittenDtoViolations(fixture);

  assert.equal(violations.length, 3);
  assert.match(violations.join("\n"), /HealthResponse/);
  assert.match(violations.join("\n"), /ProblemDetails/);
  assert.match(violations.join("\n"), /requestSchema/);
  assert.doesNotMatch(violations.join("\n"), /GeneratedResponse/);
});

test("исходники не содержат remote assets, CDN или telemetry", async () => {
  const sourceFiles = await filesBelow("src");
  const contents = await Promise.all(sourceFiles.map((path) => readFile(path, "utf8")));
  const source = contents.join("\n");
  assert.doesNotMatch(source, /https?:\/\//i);
  assert.doesNotMatch(source, /segment|sentry|telemetry|google-analytics|googletagmanager/i);
  assert.doesNotMatch(source, /@import\s+url/i);
});

test("UI не требует пользовательских CSS-файлов", async () => {
  const sourceFiles = await filesBelow("src");
  assert.equal(sourceFiles.some((path) => path.endsWith(".css")), false);
});
