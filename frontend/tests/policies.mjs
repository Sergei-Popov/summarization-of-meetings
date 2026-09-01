import { readFile, readdir } from "node:fs/promises";
import { sep } from "node:path";

import ts from "typescript";

const DTO_NAME = /(dto|request|response|problem|payload|schema)/i;

export async function filesBelow(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) => {
      const path = `${directory}/${entry.name}`;
      return entry.isDirectory() ? filesBelow(path) : [path];
    }),
  );
  return nested.flat();
}

function usesGeneratedType(node, generatedImports) {
  let generated = false;
  function visit(child) {
    if (ts.isIdentifier(child) && generatedImports.has(child.text)) {
      generated = true;
      return;
    }
    ts.forEachChild(child, visit);
  }
  visit(node);
  return generated;
}

function isSchemaInitializer(node) {
  if (!node || !ts.isCallExpression(node)) {
    return false;
  }
  const expression = node.expression;
  return (
    (ts.isPropertyAccessExpression(expression) &&
      ["object", "strictObject", "schema"].includes(expression.name.text)) ||
    (ts.isIdentifier(expression) && /schema|validator/i.test(expression.text))
  );
}

export async function findHandwrittenDtoViolations(directory) {
  const sourceFiles = (await filesBelow(directory)).filter(
    (path) =>
      /\.[cm]?tsx?$/.test(path) &&
      !path.includes(`${sep}generated${sep}`) &&
      !path.includes("/generated/"),
  );
  const violations = [];

  for (const path of sourceFiles) {
    const sourceText = await readFile(path, "utf8");
    const sourceFile = ts.createSourceFile(path, sourceText, ts.ScriptTarget.Latest, true);
    const generatedImports = new Set();
    for (const statement of sourceFile.statements) {
      if (
        ts.isImportDeclaration(statement) &&
        ts.isStringLiteral(statement.moduleSpecifier) &&
        statement.moduleSpecifier.text.includes("generated/")
      ) {
        const bindings = statement.importClause?.namedBindings;
        if (bindings && ts.isNamedImports(bindings)) {
          for (const element of bindings.elements) generatedImports.add(element.name.text);
        }
      }
    }

    function visit(node) {
      if (ts.isInterfaceDeclaration(node) && DTO_NAME.test(node.name.text)) {
        violations.push(`${path}: handwritten interface ${node.name.text}`);
      }
      if (
        ts.isTypeAliasDeclaration(node) &&
        DTO_NAME.test(node.name.text) &&
        !usesGeneratedType(node.type, generatedImports)
      ) {
        violations.push(`${path}: handwritten type ${node.name.text}`);
      }
      if (
        ts.isVariableDeclaration(node) &&
        ts.isIdentifier(node.name) &&
        (DTO_NAME.test(node.name.text) || isSchemaInitializer(node.initializer)) &&
        isSchemaInitializer(node.initializer)
      ) {
        violations.push(`${path}: handwritten schema ${node.name.text}`);
      }
      ts.forEachChild(node, visit);
    }
    visit(sourceFile);
  }
  return violations;
}
