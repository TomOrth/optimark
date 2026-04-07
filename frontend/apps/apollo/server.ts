const host = Bun.env.HOST ?? "0.0.0.0";
const port = Number(Bun.env.PORT ?? "4173");
const distRoot = new URL("./dist/", import.meta.url);
const indexFile = Bun.file(new URL("index.html", distRoot));

const contentTypes: Record<string, string> = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
};

function contentTypeFor(pathname: string): string {
  const extension = pathname.match(/\.[^.\/]+$/)?.[0] ?? "";
  return contentTypes[extension] ?? "application/octet-stream";
}

function distUrlFor(pathname: string): URL | undefined {
  if (pathname.includes("..")) {
    return undefined;
  }

  const normalizedPathname = pathname === "/" ? "/index.html" : pathname;
  return new URL(`.${normalizedPathname}`, distRoot);
}

const server = Bun.serve({
  hostname: host,
  port,
  async fetch(request) {
    const url = new URL(request.url);
    let decodedPathname: string;

    try {
      decodedPathname = decodeURIComponent(url.pathname);
    } catch {
      return new Response("Bad Request", { status: 400 });
    }

    const fileUrl = distUrlFor(decodedPathname);

    if (!fileUrl) {
      return new Response("Not found", { status: 404 });
    }

    const file = Bun.file(fileUrl);
    const responsePathname = decodedPathname === "/" ? "/index.html" : decodedPathname;

    if (await file.exists()) {
      return new Response(file, {
        headers: {
          "Content-Type": contentTypeFor(responsePathname),
        },
      });
    }

    return new Response(indexFile, {
      headers: {
        "Content-Type": "text/html; charset=utf-8",
      },
    });
  },
});

function shutdown() {
  server.stop(true);
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

console.log(`Optimark frontend listening on http://${host}:${port}`);
