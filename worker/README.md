# infoaggre-refresh Worker

前端「立即更新」按钮的触发代理。持有一个 fine-grained PAT，校验来源 + 60s 节流后
触发 GitHub `workflow_dispatch`。token 只在这里，永不进前端。

## 一次性部署

1. 注册/登录 Cloudflare（免费，无需绑卡）。
2. 在 GitHub 建 fine-grained PAT：Settings → Developer settings → Fine-grained tokens
   - Repository access：仅 `TIANSHUUU/info-aggregator`
   - Permissions：`Actions` → Read and write
   - 复制生成的 token 串
3. 在本目录部署：
   ```bash
   cd worker
   npx wrangler login
   npx wrangler secret put GH_TOKEN   # 粘贴上一步的 token
   npx wrangler deploy
   ```
4. 记下输出里的 Worker 网址（形如 `https://infoaggre-refresh.<subdomain>.workers.dev`），
   填入前端 `src/App.jsx` 的 `REFRESH_ENDPOINT`。

## 自测

```bash
# 正确来源 → {"ok":true} 并在 Actions 触发一次 run
curl -X POST -H "Origin: https://tianshuuu.github.io" <worker-url>
# 错误/缺失来源 → 403
curl -X POST <worker-url>
```
