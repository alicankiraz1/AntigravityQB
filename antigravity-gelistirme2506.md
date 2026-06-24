# AntigravityQB Gelistirme Plani - 2026-06-25

Bu dosya AntigravityQB icin bir sonraki gelistirme hattini tarif eder. Amac,
CodexQB tarafinda ilerleyen 0.3.0 calismasini birebir kopyalamak degil,
Antigravity'nin beceri modeli, kurulum kokleri, dosya yapisi ve test kapilariyla
uyumlu parcalara ayirmaktir.

## Incelenen Durum

- AntigravityQB baseline: `main@814edf6`, temiz calisma agaci, public release
  `0.2.1`.
- AntigravityQB mevcut sozlesme: `artifact_schema_version: 2`,
  `handoff_contract_version: 1`, Step 3 preflight, semantic Step 4,
  `NO_ACTION_REQUIRED`, Ledger v2, canonical Antigravity handoff dosyalari,
  optional `Project-Comprehension.md`, deterministic fixture corpus.
- CodexQB kaynak baseline: `main@60b9d05` uzerine commit edilmemis 0.3.0
  calismasi.
- CodexQB diff ozeti: 22 dosya, 870 ekleme, 157 silme.
- Incelenen kaynak yuzeyleri: `README.md`, `CHANGELOG.md`,
  `plugins/codexqb/skills/codexqb/SKILL.md`,
  `scripts/goal_run.py`, `scripts/apply_run.py`, Goal/Apply referanslari,
  release-audit notlari ve ilgili test dosyalari.

Not: CodexQB tarafindaki 0.3.0 calismasi bu inceleme aninda kirli calisma
agacindaydi. Bu nedenle AntigravityQB icin "kesin release kaynagi" degil,
uyarlanacak tasarim girdisi olarak kullanilmalidir.

## Mevcut AntigravityQB Eslesmesi

AntigravityQB zaten 0.2.1 QB-family planlama kontratini tasiyor:

- repo-aware intake ve Step 1 ana plan akisi;
- mevcut proje icin Step 1.5 autopsy;
- optional ontology, comprehension ve ledger surekliligi;
- Step 2 sub-plan index ve faz klasorleri;
- Step 3 QA audit ve Step 3 preflight dogrulamasi;
- Step 4 icin PASS / PASS_WITH_WARNINGS / BLOCKED semantigi;
- P0/P1 blokajlari, P2/P3 uyari semantigi ve `NO_ACTION_REQUIRED`;
- Antigravity'ye ozel `references/handoffs/run-step2.md`,
  `run-step3.md`, `run-step4.md`;
- Antigravity public yuzeylerinde Codex terimi ve platform yolu tasimama
  kontrolu.

Bu nedenle bir sonraki is "0.2.1'i yeniden tasimak" degil, 0.3.x ozelliklerini
Antigravity ortaminda anlamli olan kucuk dilimlere bolmektir.

## Tasinmasi Gereken Gelistirmeler

| CodexQB gelismesi | Antigravity karari | Oncelik | Uygulama notu |
| --- | --- | --- | --- |
| `artifact_schema_version: 3` ve `handoff_contract_version: 2` | Tasinmali | P0 | README, skill, planner referanslari ve validator ayni anda guncellenmeli. 0.2.1 uyumlulugu migration notuyla korunmali. |
| Adaptive Step 2: `wave` ve `full` planlama | Tasinmali | P0 | Buyuk projelerde aktif planlama ufku yazilip sonraki fazlar roadmap card olarak ertelenmeli. Antigravity promptlari bunu acik istemeli. |
| Structured Implementation Contract | Tasinmali | P0 | Sub-plan sonuna makine-okunur kontrat eklenmeli: repo-relative path, state, validation command id, risk class, dependency labels, acceptance signals. |
| Safe `argv` validation command modeli | Tasinmali | P0 | Shell chaining, command substitution, deploy/mutation komutlari ve keyfi `python -c` reddedilmeli. Validator strict modda bunu zorlamali. |
| Framework ownership ve algorithmic invariant tablolar | Tasinmali | P1 | Step 2/3 kalite kapilarini guclendirir. Ilk dilimde uyari, ikinci dilimde strict gate olabilir. |
| Policy digest mantigi | Uyarlanarak tasinmali | P1 | Antigravity run artifact'lari icin `task_policy_digest` veya benzeri ad kullanilmali. Codex'e ozel Goal/Apply isimleri public yuzeye tasinmamali. |
| Stage-aware source snapshot | Uyarlanarak tasinmali | P1 | Step 3 audit ve Step 4 ledger gibi beklenen mutable output'lar baseline drift sayilmamali. |
| Goal preview compiler | Antigravity adiyla uyarlanmali | P1 | `goal_run.py` birebir gelmemeli. Antigravity icin `task_run.py` veya `handoff_run.py` daha dogru ad olur. |
| Apply run orchestrator | Kademeli uyarlanmali | P2 | Antigravity'nin gercek task/subtask kabiliyetleri dogrulanmadan sadece dosya-tabanli prepare/validate/finalize akisi tasinmali. |
| Writer lock, events jsonl, finalize/recover-lock | Kademeli uyarlanmali | P2 | Once tek-writer ve resume emniyeti icin minimal dosya kontrati. Sonra rol bazli akisa genisletme. |
| Privacy/public release scan | Tasinmali | P1 | Local path, attachment id, thread id ve runtime log sizintilarini public dokumanlardan ayiklayan gate eklenmeli. |
| Sanitized export hardening | Tasinmali | P1 | Mevcut `make export-sanitized` yalniz `git archive` yapiyor. Symlink, manifest, clean-tree ve secret taramasi eklenmeli. |
| Fixture corpus buyutme | Tasinmali | P1 | 0.2.1 corpus mevcut; 0.3.x icin Goal/Task, no-action, resume, security, package edge case fixture'lari eklenmeli. |

## Birebir Tasinmamasi Gerekenler

- `.codex-plugin`, `openai.yaml`, marketplace dosyalari ve Codex kurulum
  komutlari.
- `~/.codex` cache/skill path'leri.
- Codex Goal Mode, Superpowers veya Codex subagent API adlari.
- Codex'e ozel `multi_agent_v1` varsayimlari.
- Public Antigravity dokumanlarinda "CodexQB" veya Codex platform terimleri.
- Codex release evidence dosyalarindaki local runtime loglari.

AntigravityQB public yuzeyleri bugun bu ayrimi test ediyor; README, `docs/` ve
`skills/` altinda Codex terimi bulunmamali.

## Onerilen Uygulama Dilimleri

### Dilim 1 - 0.3.x planlama kontrati

Hedef:

- schema v3 / handoff v2 metadata eklemek;
- Step 2 icin `wave` / `full` planlama kiplerini tarif etmek;
- deferred roadmap card formatini tanimlamak;
- validator'a backward-compatible migration mesaji eklemek.

Dosyalar:

- `skills/antigravityqb/SKILL.md`
- `skills/antigravityqb/references/Second-Planner.md`
- `skills/antigravityqb/references/Third-Planner.md`
- `skills/antigravityqb/scripts/validate_planner_docs.py`
- `tests/test_validate_planner_docs.py`
- `README.md`, `CHANGELOG.md`, `docs/USAGE.md`

Dogru bitis kaniti:

- `make check`
- `python3 skills/antigravityqb/scripts/validate_planner_docs.py --root <fixture> --mode step2 --strict`
- Eski 0.2.1 fixture'lari anlamli migration mesaji veriyor.

### Dilim 2 - Structured implementation contracts

Hedef:

- sub-plan dosyalarinda structured implementation contract bolumu;
- repo-relative path, path state, validation command id, risk domain, security
  review flag, dependency label ve acceptance signal alanlari;
- Step 3 audit'in eksik/guvensiz kontratlari bulmasi.

Dogru bitis kaniti:

- strict validator guvensiz shell, mutating deploy komutu ve absolute path
  iceren kontrati reddeder;
- temiz fixture strict modda gecer;
- README ve docs kurulum davranisini degil planlama kontratini gunceller.

### Dilim 3 - Antigravity-native run preview

Hedef:

- CodexQB `goal_run.py` fikrini Antigravity icin yeniden adlandirmak;
- onerilen ad: `skills/antigravityqb/scripts/task_run.py` veya
  `handoff_run.py`;
- sadece artifact uretmek, komut calistirmamak;
- `Task-Run.json`, `Task-Prompt.md`, `Task-Result.json` gibi Antigravity
  bagimsiz dosyalar uretmek;
- stage-aware source snapshot ve policy digest eklemek.

Dogru bitis kaniti:

- script Step 2/3/4 icin eksik prereq durumunda execution prompt degil
  `BLOCKED` sonucu uretir;
- snapshot digest kaynak sub-plan degisiminde bozulur;
- beklenen Step 3 audit veya Step 4 ledger ciktisi drift sayilmaz.

### Dilim 4 - Dosya-tabanli apply/run orkestrasyonu

Hedef:

- Antigravity task API'sine baglanmadan once yerel dosya kontratini kurmak;
- prepare, validate, finalize, no-action, recover-lock komutlari;
- tek writer garantisi ve append-only event log;
- verified task evidence icin dosya, patch hash ve validation evidence
  zorunlulugu.

Dogru bitis kaniti:

- disposable git fixture uzerinde end-to-end smoke;
- dirty/protected worktree varsayimlari acik user approval olmadan bloklanir;
- untracked yeni dosya ancak contract `state: proposed` ise kabul edilir.

### Dilim 5 - Release ve public hygiene

Hedef:

- `make export-sanitized` hedefini manifestli, tracked-only, symlink-safe ve
  secret/privacy scan'li hale getirmek;
- README, docs, skill ve package artifact'larinin ayni surumu soyledigini
  kontrol etmek;
- Antigravity install root parity kontrolunu release checklist'e eklemek.

Dogru bitis kaniti:

- `make check`
- `make export-sanitized`
- extracted package uzerinde `make check` muadili veya validator smoke;
- app-global, ide-global ve cli-global kurulum path'lerinde skill parity diff.

## Kabul Kriterleri

Bir 0.3.x AntigravityQB dilimi tamamlanmis sayilmaz; ancak:

- repo temizdir;
- public README mevcut release ile future plan ayrimini karistirmaz;
- `make check` gecmistir;
- yeni fixture veya test eklenmistir;
- stale Codex platform terimi public Antigravity yuzeylerine sizmamistir;
- release veya install iddiasi varsa package/export ve installed-copy parity
  ayrica dogrulanmistir.

## Riskler

- CodexQB'deki 0.3.0 degisiklikleri bu inceleme aninda commit edilmemisti;
  final tasarim degisebilir.
- Antigravity tarafinda Codex Goal/Apply kavramlarinin dogrudan karsiligi
  olmayabilir; dosya-tabanli preview/run kontrati once gelmeli.
- Public dokumanlarda platform terimi karismasi mevcut testleri dusurur.
- Install parity release sonrasi unutulursa repo dogru, aktif skill eski
  kalabilir.

## Siradaki Net Adim

Once Dilim 1 uygulanmali: schema v3 / handoff v2, adaptive Step 2 ve deferred
roadmap card kontrati. Bu, runtime orchestration eklemeden once planlama
artifact'larinin yeni sekle gecmesini saglar ve en dusuk riskli temel degisikliktir.
