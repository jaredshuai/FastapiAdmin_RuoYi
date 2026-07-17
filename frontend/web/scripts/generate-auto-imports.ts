import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import { extname, resolve } from "node:path";

import type { Plugin } from "vite";
import { resolveConfig } from "vite";

type Hook = Plugin["buildStart"] | Plugin["buildEnd"];
type TransformHook = Plugin["transform"];

const sourceExtensions = new Set([".js", ".jsx", ".ts", ".tsx", ".vue"]);

async function runHook(hook: Hook): Promise<void> {
  if (!hook) return;
  const handler = typeof hook === "function" ? hook : hook.handler;
  await handler.call({} as never);
}

async function collectSourceFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const nestedFiles = await Promise.all(
    entries.map(async (entry) => {
      const path = resolve(directory, entry.name);
      if (entry.isDirectory()) return collectSourceFiles(path);
      return sourceExtensions.has(extname(entry.name)) ? [path] : [];
    })
  );
  return nestedFiles.flat();
}

async function runTransform(hook: TransformHook, code: string, id: string): Promise<void> {
  if (!hook) return;
  const handler = typeof hook === "function" ? hook : hook.handler;
  await handler.call({} as never, code, id);
}

async function main(): Promise<void> {
  // Loading the real Vite config keeps this generator and the build plugins on
  // the same AutoImport/Components options. resolveConfig also lets the
  // Components plugin emit its declaration during configResolved.
  const config = await resolveConfig({ logLevel: "silent", mode: "dev" }, "build", "dev");
  const autoImportPlugin = config.plugins.find((plugin) => plugin.name === "unplugin-auto-import");

  if (!autoImportPlugin) {
    throw new Error("Vite config does not contain unplugin-auto-import");
  }

  await runHook(autoImportPlugin.buildStart);
  const sourceFiles = await collectSourceFiles(resolve(config.root, "src"));
  for (const file of sourceFiles) {
    if (autoImportPlugin.transformInclude?.(file) === false) continue;
    await runTransform(autoImportPlugin.transform, await readFile(file, "utf8"), file);
  }
  await runHook(autoImportPlugin.buildEnd);

  const expectedFiles = [
    ".auto-import.json",
    "src/types/import/auto-imports.d.ts",
    "src/types/import/components.d.ts",
  ];
  const missingFiles = expectedFiles.filter((file) => !existsSync(resolve(config.root, file)));

  if (missingFiles.length > 0) {
    throw new Error(`Auto-import generation did not create: ${missingFiles.join(", ")}`);
  }

  console.log(`Generated ${expectedFiles.join(", ")} from ${sourceFiles.length} source files`);
}

void main();
