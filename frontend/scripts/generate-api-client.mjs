import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(scriptDir, "..");
const backendRoot = path.resolve(frontendRoot, "../backend");
const outputFile = path.resolve(
  frontendRoot,
  "apps/apollo/src/lib/api/generated.ts",
);

function runOpenApiExport() {
  const pythonSource = [
    "import json",
    "from optimark_athena.app import app",
    "print(json.dumps(app.openapi()))",
  ].join("; ");

  const result = spawnSync(
    "uv",
    ["run", "--package", "athena", "python", "-c", pythonSource],
    {
      cwd: backendRoot,
      encoding: "utf8",
    },
  );

  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || "failed to export OpenAPI schema");
  }

  return JSON.parse(result.stdout);
}

function toIdentifier(name) {
  return name.replace(/[^A-Za-z0-9_$]/g, "_");
}

function toCamelCase(value) {
  return value
    .split(/[^A-Za-z0-9]+/)
    .filter(Boolean)
    .map((part, index) => {
      const lower = part.toLowerCase();
      if (index === 0) {
        return lower;
      }

      return lower.charAt(0).toUpperCase() + lower.slice(1);
    })
    .join("");
}

function toOperationName(operationId) {
  const baseName = operationId.includes("_api_")
    ? operationId.slice(0, operationId.indexOf("_api_"))
    : operationId;

  return toCamelCase(baseName);
}

function renderType(schema, context) {
  if (!schema) {
    return "unknown";
  }

  if (schema.$ref) {
    return schema.$ref.split("/").at(-1);
  }

  if (schema.anyOf) {
    return schema.anyOf.map((entry) => renderType(entry, context)).join(" | ");
  }

  if (schema.enum) {
    return schema.enum.map((value) => JSON.stringify(value)).join(" | ");
  }

  if (schema.type === "array") {
    const itemType = renderType(schema.items, context);
    const wrappedItemType = itemType.includes("|") ? `(${itemType})` : itemType;
    return `${wrappedItemType}[]`;
  }

  if (schema.type === "object") {
    if (schema.properties) {
      const required = new Set(schema.required ?? []);
      const fields = Object.entries(schema.properties).map(([key, value]) => {
        const propertyName = /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(key)
          ? key
          : JSON.stringify(key);
        const optional = required.has(key) ? "" : "?";
        return `${propertyName}${optional}: ${renderType(value, context)};`;
      });

      if (!fields.length) {
        return "Record<string, never>";
      }

      return `{\n${fields.map((field) => `  ${field}`).join("\n")}\n}`;
    }

    if (schema.additionalProperties) {
      const valueType =
        schema.additionalProperties === true
          ? "unknown"
          : renderType(schema.additionalProperties, context);

      return `Record<string, ${valueType}>`;
    }

    return "Record<string, unknown>";
  }

  if (schema.type === "string") {
    return "string";
  }

  if (schema.type === "integer" || schema.type === "number") {
    return "number";
  }

  if (schema.type === "boolean") {
    return "boolean";
  }

  if (schema.type === "null") {
    return "null";
  }

  return "unknown";
}

function renderSchemas(openApi) {
  const schemas = openApi.components?.schemas ?? {};

  return Object.entries(schemas)
    .map(([name, schema]) => `export type ${name} = ${renderType(schema, openApi)};\n`)
    .join("\n");
}

function getSuccessResponse(operation) {
  const responseCode = Object.keys(operation.responses)
    .filter((code) => code.startsWith("2"))
    .sort()[0];

  if (!responseCode) {
    throw new Error(`operation ${operation.operationId} has no success response`);
  }

  return operation.responses[responseCode];
}

function renderPathTemplate(pathname, pathParameters) {
  const segments = pathname
    .split(/(\{[^}]+\})/g)
    .filter(Boolean)
    .map((segment) => {
      const match = segment.match(/^\{([^}]+)\}$/);

      if (!match) {
        return segment;
      }

      const parameterName = match[1];
      return `\${encodeURIComponent(pathParams.${parameterName})}`;
    });

  if (!pathParameters.length) {
    return JSON.stringify(pathname);
  }

  return `\`${segments.join("")}\``;
}

function renderOperation(pathname, method, operation, usedNames) {
  const name = toOperationName(operation.operationId);
  const uniqueName = usedNames.has(name) ? toCamelCase(operation.operationId) : name;
  usedNames.add(uniqueName);

  const parameters = operation.parameters ?? [];
  const pathParameters = parameters.filter((parameter) => parameter.in === "path");
  const requestBodySchema =
    operation.requestBody?.content?.["application/json"]?.schema ?? null;
  const successResponse = getSuccessResponse(operation);
  const responseSchema =
    successResponse.content?.["application/json"]?.schema ?? null;
  const requestFunction = responseSchema ? "requestJson" : "requestVoid";
  const responseType = responseSchema ? renderType(responseSchema) : "void";
  const signatureParts = [];
  const callParts = [];

  if (pathParameters.length) {
    const pathShape = pathParameters
      .map((parameter) => {
        const paramName = toIdentifier(parameter.name);
        return `${paramName}: ${renderType(parameter.schema)};`;
      })
      .join(" ");
    signatureParts.push(`pathParams: { ${pathShape} }`);
  }

  if (requestBodySchema) {
    signatureParts.push(`payload: ${renderType(requestBodySchema)}`);
    callParts.push("body: JSON.stringify(payload)");
  }

  callParts.unshift(`method: ${JSON.stringify(method.toUpperCase())}`);

  const invocationPath = renderPathTemplate(pathname, pathParameters);
  const args = signatureParts.join(", ");
  const requestInit = callParts.length
    ? `, {\n      ${callParts.join(",\n      ")}\n    }`
    : "";

  const typeArgument = responseSchema ? `<${responseType}>` : "";

  return `  ${uniqueName}(${args}) {
    return ${requestFunction}${typeArgument}(${invocationPath}${requestInit});
  },`;
}

function renderOperations(openApi) {
  const usedNames = new Set();
  const operations = [];

  for (const [pathname, pathItem] of Object.entries(openApi.paths ?? {})) {
    for (const [method, operation] of Object.entries(pathItem)) {
      operations.push(renderOperation(pathname, method, operation, usedNames));
    }
  }

  return operations.join("\n");
}

function buildOutput(openApi) {
  const header = [
    "// Generated by `bun run generate:api`.",
    "// Do not edit this file manually.",
    "",
    'import { requestJson, requestVoid } from "./client";',
    "",
  ].join("\n");

  const schemas = renderSchemas(openApi);
  const operations = renderOperations(openApi);

  return `${header}${schemas}\nexport const apiClient = {\n${operations}\n} as const;\n`;
}

const openApi = runOpenApiExport();
const output = buildOutput(openApi);

mkdirSync(path.dirname(outputFile), { recursive: true });
writeFileSync(outputFile, output);
