### Hi there 👋

後端工程師，正在練習「把大問題拆小、交給多個 AI 並行做、再用閘門驗收」這套工作方式。
Backend engineer (.NET · Go). I break big problems into small, verifiable slices and run several AI coding sessions in parallel without them stepping on each other.

#### 🔧 作品 / Projects

| 專案 | 一句話 | 看點 |
|---|---|---|
| [go-shop](https://github.com/newhand31/go-shop) | 用 Go 寫一個正式風格的電商後端，配 YouTube 教學系列 | 給 C#/Java 工程師的 Go 遷移路線 |
| CountMeIn | 陌生人聚餐配對服務，已上線 | .NET Clean Architecture、Azure 部署、BDD 驗收 |
| claude-coord（整理中） | 一人帶多個 Claude Code session 的協調工具：認領、車道、一筆一檔的帳本 | 多 AI 並行時怎麼不互踩 |
| brain-search（整理中） | 查詢 → 帶分數的知識切塊，形狀仿 Tavily 的 RAG API | 評估集、檢索指標、洩漏閘門 |

#### 🧭 我在意的事 / How I work

- **小批次、永遠可回退**：一個 PR 一個切片，主幹永遠綠。
- **驗收先寫成可執行的檢查**：AI 寫的東西，交給另一個全新 context 的 checker 對照 spec 審。
- **意圖寫進檔案**：決策、教訓、待辦放在 repo 的 `state/`，每次開工重新載入。

<!-- 這份 README 由 scripts/leak-check.py 在 commit 前掃描，避免帶出個人資料。 -->
