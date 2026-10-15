// 선택 실습: Node.js 22.18+ 또는 24.3+의 내장 TypeScript 실행 기능을 사용한다.
import { get } from "node:http";
import { performance } from "node:perf_hooks";

// 1. 명령줄 주소가 없으면 기본 /echo 주소로 요청한다.
const urlArgument = process.argv[2];
const target = new URL(urlArgument ?? "http://127.0.0.1:8080/echo?message=hello");
if (target.protocol !== "http:") {
  throw new Error("Week 1 uses an http:// test URL.");
}

const start = performance.now();
const logEvent = (event: string, detail: object = {}) => {
  const elapsedMilliseconds = Number((performance.now() - start).toFixed(2));
  console.log(JSON.stringify({
    event,
    elapsed_ms: elapsedMilliseconds,
    ...detail,
  }));
};

// 2. 요청을 시작한다. 응답이 오면 이 콜백 안에서 상태·헤더·본문을 읽는다.
logEvent("request", { method: "GET", url: target.href });
const request = get(target, { agent: false }, (response) => {
  logEvent("response", { status: response.statusCode, headers: response.headers });

  // data는 본문 일부가 도착할 때마다, end는 본문이 모두 도착했을 때 실행된다.
  response.setEncoding("utf8");
  let body = "";
  response.on("data", (chunk: string) => {
    body += chunk;
  });
  response.on("end", () => {
    clearTimeout(deadline);
    logEvent("body", { body });
    if ((response.statusCode ?? 0) >= 400) {
      process.exitCode = 2;
    }
  });
  response.on("error", (error) => {
    request.destroy(error);
  });
});

// 3. TCP 연결이 만들어지면 내 주소와 상대 주소를 기록한다.
request.on("socket", (socket) => {
  socket.once("connect", () => {
    logEvent("connected", {
      local: `${socket.localAddress}:${socket.localPort}`,
      remote: `${socket.remoteAddress}:${socket.remotePort}`,
    });
  });
});

// 4. 응답이 오래 걸리면 3초 후 요청을 중단한다.
const deadline = setTimeout(() => {
  request.destroy(new Error("lab deadline: 3000 ms"));
}, 3000);

// 연결·전송 오류나 시간 초과를 기록한다. HTTP 상태를 받았는지는 response 로그로 확인한다.
request.on("error", (error: NodeJS.ErrnoException) => {
  clearTimeout(deadline);
  logEvent("network_error", {
    code: error.code ?? "LAB_TIMEOUT",
    message: error.message,
  });
  process.exitCode = 1;
});
