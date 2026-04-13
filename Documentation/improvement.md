# NexusAI — Improvement Roadmap

> A prioritized list of bugs, security fixes, and feature enhancements for the AI Chatbot project.

---

## 🔴 Critical Bugs (Must Fix)

These are actively breaking functionality for users right now.

| # | Bug | Impact | Status |
|---|-----|--------|--------|
| 1 | **Token expires in 15 min instead of 1 day** — The config `ACCESS_TOKEN_EXPIRE_MINUTES = 1440` is defined but never passed to `create_access_token()`, so it silently defaults to 15 minutes. | Users get randomly logged out mid-session | ⬜ TODO |
| 2 | **Auth token not attached to protected API calls** — `/files/upload`, `/files`, and `/files/{id}` all require JWT auth, but the Angular `ChatbotService` never sends the `Authorization: Bearer <token>` header. | File upload, list, and delete fail with 401 errors | ⬜ TODO |
| 3 | **Chunker only works for Q&A-format PDFs** — `chunker.py` splits text using the regex `Question\s*\d+`, so any normal PDF (manuals, policies, articles) produces zero chunks and fails silently. | App is unusable for general-purpose documents | ⬜ TODO |

---

## 🟡 Security Concerns (Should Fix)

These don't break functionality but expose the app to real-world attacks.

| # | Issue | Risk Level | Status |
|---|-------|------------|--------|
| 4 | **`.env` with secrets possibly committed to Git** — Contains Groq API key, Supabase DB password, and JWT secret in plain text. | 🔴 High — Anyone with repo access can steal credentials | ⬜ TODO |
| 5 | **Weak JWT secret key** — Current secret is a simple guessable string (`jdjkfdhsfkjllhsaufbakjbvasbubkjdsf`). Should be a cryptographically random hex string. | 🟡 Medium — Tokens could be forged | ⬜ TODO |
| 6 | **No rate limiting on login** — The `/auth/login` endpoint can be hit unlimited times, enabling brute-force password attacks. | 🟡 Medium — Account compromise risk | ⬜ TODO |
| 7 | **No input validation** — Registration accepts any string as email/password. No email format check, no minimum password length. | 🟡 Medium — Garbage data and weak accounts | ⬜ TODO |

---

## ✨ Feature Enhancements (Nice to Have)

Prioritized by impact and user experience improvement.

### High Priority
| # | Feature | Description |
|---|---------|-------------|
| 8 | **Streaming Responses (SSE)** | Stream AI responses word-by-word like ChatGPT instead of waiting for the full answer. Dramatically improves perceived speed. |
| 9 | **Conversation Context** | Send previous messages as context so the AI can follow up and remember the conversation flow. Currently each question is treated independently. |
| 10 | **Embeddable Chat Widget** | Generate a `<script>` tag or iframe snippet that anyone can paste into their website to embed the chatbot. This is the core SaaS value proposition. |

### Medium Priority
| # | Feature | Description |
|---|---------|-------------|
| 11 | **Markdown Rendering in Chat** | Render AI responses with proper formatting — bold text, bullet lists, code blocks, tables — using a library like `marked.js`. |
| 12 | **Multi-File Type Support** | Accept `.txt`, `.docx`, and `.csv` files alongside PDFs. Expand the audience significantly. |
| 13 | **Chat History View** | Show past conversations per knowledge base in the admin panel. Currently history is saved to DB but never displayed. |
| 14 | **Dashboard Analytics** | Track total questions asked, popular topics, average response time, and usage per knowledge base. |

### Low Priority
| # | Feature | Description |
|---|---------|-------------|
| 15 | **Dark/Light Theme Toggle** | Add a theme switcher to the navbar for user preference. |
| 16 | **User Profile Page** | Let users change their password and view usage statistics. |
| 17 | **Multi-Model Selection** | Let users choose between AI models (llama-3.3-70b, mixtral, gemma, etc.) per knowledge base. |
| 18 | **Export Chat as PDF** | Allow users to download their conversation as a formatted PDF. |

---

## 🏗️ Architecture Improvements

Clean code changes that make the project more maintainable.

- [ ] **Split `main.py` into FastAPI Routers** — Separate auth, files, and chat into `routers/auth.py`, `routers/files.py`, `routers/chat.py`
- [ ] **Remove dead/legacy code** — `data_manager.py`, `qa_extractor.py`, `main_fixed.py`, `frontend.html`, empty `service/` directory
- [ ] **Centralize API URL** — Move the hardcoded API URL from `auth.service.ts` and `chatbot.service.ts` into Angular `environment.ts`
- [ ] **Add structured logging** — Replace silent failures with proper `logging.info()` / `logging.error()` calls
- [ ] **Add HTTP Interceptor** — Centralize auth token attachment and error handling in Angular
- [ ] **Replace `alert()` with toast notifications** — Use proper UI feedback instead of browser dialogs

---

## 📋 Recommended Implementation Order

```
Phase 1 — Bug Fixes (Day 1)
  ├── #1 Fix token expiry
  ├── #2 Add auth interceptor
  └── #3 General-purpose chunker

Phase 2 — Security (Day 2)
  ├── #4 Secure .env / .gitignore
  ├── #5 Generate strong JWT secret
  ├── #6 Add rate limiting
  └── #7 Pydantic input validation

Phase 3 — Core Features (Week 1)
  ├── #8 Streaming responses
  ├── #9 Conversation context
  └── #11 Markdown rendering

Phase 4 — SaaS Features (Week 2)
  ├── #10 Embeddable widget
  ├── #12 Multi-file support
  ├── #13 Chat history view
  └── #14 Dashboard analytics
```

---

*Last updated: April 7, 2026*