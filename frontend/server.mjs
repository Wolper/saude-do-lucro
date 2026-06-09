import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

const port = Number.parseInt(process.env.PORT ?? "3000", 10);
const host = process.env.HOST ?? "0.0.0.0";
const publicDir = join(process.cwd(), "public");

const server = createServer(async (_request, response) => {
  try {
    const html = await readFile(join(publicDir, "index.html"), "utf8");
    response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    response.end(html);
  } catch (error) {
    response.writeHead(500, { "content-type": "application/json; charset=utf-8" });
    response.end(JSON.stringify({ status: "error", message: "frontend unavailable" }));
  }
});

server.listen(port, host, () => {
  console.log(`Saúde do Lucro frontend running at http://localhost:${port}`);
});
